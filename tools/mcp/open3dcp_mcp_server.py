#!/usr/bin/env python3
"""Read-only Open3DCP MCP-style stdio wrapper.

The implementation intentionally avoids third-party dependencies so the public schema repository can
ship a usable agent helper without forcing a package manager. It implements the JSON-RPC methods most
MCP-style clients need for local tools/list and tools/call interactions.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Any


REPO_ROOT = Path(__file__).resolve().parents[2]
SCHEMA_PATH = REPO_ROOT / "Open3DCP_SCHEMA.md"

RESOURCE_MAP = {
    "schema_markdown": "Open3DCP_SCHEMA.md",
    "schema_sql": "sql/create_tables.sql",
    "readme": "README.md",
    "changelog": "CHANGELOG.md",
    "llms": "llms.txt",
    "mcp_manifest": ".well-known/mcp-manifest.json",
}


def read_text(path: Path) -> str:
    if not path.is_file():
        raise FileNotFoundError(str(path.relative_to(REPO_ROOT)))
    return path.read_text(encoding="utf-8")


def schema_fields() -> set[str]:
    text = read_text(SCHEMA_PATH)
    fields: set[str] = set()
    for line in text.splitlines():
        if not line.startswith("| `"):
            continue
        match = re.match(r"^\| `([^`]+)` \|", line)
        if match:
            fields.add(match.group(1))
    fields.update({"schema", "schema_version", "record_type", "source_dataset", "provenance_notes"})
    return fields


def json_content(value: Any) -> list[dict[str, str]]:
    return [{"type": "text", "text": json.dumps(value, indent=2, sort_keys=True)}]


def text_content(value: str) -> list[dict[str, str]]:
    return [{"type": "text", "text": value}]


def tool_definitions() -> list[dict[str, Any]]:
    return [
        {
            "name": "open3dcp_get_resource",
            "description": "Return a read-only Open3DCP repository resource.",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "resource": {
                        "type": "string",
                        "enum": sorted(RESOURCE_MAP),
                    }
                },
                "required": ["resource"],
            },
        },
        {
            "name": "open3dcp_list_examples",
            "description": "List Open3DCP example record metadata files.",
            "inputSchema": {
                "type": "object",
                "properties": {},
                "additionalProperties": False,
            },
        },
        {
            "name": "open3dcp_validate_record",
            "description": "Validate a candidate flat Open3DCP-shaped JSON object.",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "record": {
                        "type": "object",
                        "description": "Candidate Open3DCP record as a JSON object.",
                    },
                    "strict_unknown_fields": {
                        "type": "boolean",
                        "default": False,
                        "description": "Treat unknown fields as errors instead of warnings.",
                    },
                },
                "required": ["record"],
            },
        },
    ]


def get_resource(arguments: dict[str, Any]) -> dict[str, Any]:
    name = str(arguments.get("resource", "")).strip()
    rel = RESOURCE_MAP.get(name)
    if not rel:
        return {"isError": True, "content": text_content(f"unknown resource: {name}")}
    return {
        "content": text_content(read_text(REPO_ROOT / rel)),
        "metadata": {
            "resource": name,
            "path": rel,
            "read_only": True,
        },
    }


def list_examples(_: dict[str, Any]) -> dict[str, Any]:
    rows = []
    for path in sorted((REPO_ROOT / "examples").glob("*/record.json")):
        try:
            record = json.loads(read_text(path))
        except json.JSONDecodeError:
            record = {}
        rows.append(
            {
                "id": record.get("id") or path.parent.name,
                "path": str(path.relative_to(REPO_ROOT)).replace("\\", "/"),
                "dataset": record.get("dataset"),
                "license": record.get("license"),
                "schema_version": record.get("schema_version"),
            }
        )
    return {"content": json_content({"examples": rows, "count": len(rows)})}


def validate_record(arguments: dict[str, Any]) -> dict[str, Any]:
    record = arguments.get("record")
    strict = bool(arguments.get("strict_unknown_fields", False))
    errors: list[str] = []
    warnings: list[str] = []

    if not isinstance(record, dict) or isinstance(record, list):
        return {"isError": True, "content": json_content({"errors": ["record must be a JSON object"]})}

    known = schema_fields()
    for key, value in record.items():
        if not isinstance(key, str) or not key:
            errors.append("all field names must be non-empty strings")
            continue
        if isinstance(value, (dict, list)):
            errors.append(f"{key}: nested objects/arrays are not valid for flat Open3DCP records")
        if key not in known:
            message = f"{key}: unknown Open3DCP field"
            (errors if strict else warnings).append(message)

    if "original_basis" not in record:
        warnings.append("original_basis is recommended so source units are not silently rewritten")
    if "source_dataset" not in record and "provenance_notes" not in record:
        warnings.append("source_dataset or provenance_notes is recommended for attribution and traceability")

    result = {
        "valid": not errors,
        "error_count": len(errors),
        "warning_count": len(warnings),
        "errors": errors,
        "warnings": warnings,
        "known_field_count": len(known),
    }
    return {"isError": bool(errors), "content": json_content(result)}


TOOLS = {
    "open3dcp_get_resource": get_resource,
    "open3dcp_list_examples": list_examples,
    "open3dcp_validate_record": validate_record,
}


def rpc_result(request_id: Any, result: Any) -> dict[str, Any]:
    return {"jsonrpc": "2.0", "id": request_id, "result": result}


def rpc_error(request_id: Any, code: int, message: str) -> dict[str, Any]:
    return {"jsonrpc": "2.0", "id": request_id, "error": {"code": code, "message": message}}


def handle_request(message: dict[str, Any]) -> dict[str, Any] | None:
    method = message.get("method")
    request_id = message.get("id")
    params = message.get("params") or {}

    if method == "initialize":
        return rpc_result(
            request_id,
            {
                "protocolVersion": "2024-11-05",
                "serverInfo": {"name": "open3dcp-readonly-wrapper", "version": "0.1.0"},
                "capabilities": {"tools": {}},
            },
        )
    if method == "notifications/initialized":
        return None
    if method == "tools/list":
        return rpc_result(request_id, {"tools": tool_definitions()})
    if method == "tools/call":
        name = params.get("name")
        arguments = params.get("arguments") or {}
        handler = TOOLS.get(name)
        if not handler:
            return rpc_error(request_id, -32601, f"unknown tool: {name}")
        try:
            return rpc_result(request_id, handler(arguments))
        except Exception as exc:  # Return errors to the client without stack traces.
            return rpc_error(request_id, -32000, f"{type(exc).__name__}: {exc}")
    return rpc_error(request_id, -32601, f"unknown method: {method}")


def serve_stdio() -> None:
    for line in sys.stdin:
        line = line.strip()
        if not line:
            continue
        try:
            message = json.loads(line)
        except json.JSONDecodeError as exc:
            print(json.dumps(rpc_error(None, -32700, f"parse error: {exc}")), flush=True)
            continue
        response = handle_request(message)
        if response is not None:
            print(json.dumps(response), flush=True)


def smoke_test() -> int:
    fields = schema_fields()
    checks = []
    checks.append({"name": "schema_fields_loaded", "pass": len(fields) > 100})
    checks.append({"name": "resources_listed", "pass": set(RESOURCE_MAP) >= {"schema_markdown", "schema_sql"}})
    valid = validate_record(
        {
            "record": {
                "source_dataset": "fixture",
                "original_basis": "kg_m3",
                "cement_type_1": 350,
                "water": 160,
                "compressive_strength_mpa": 42,
            }
        }
    )
    valid_body = json.loads(valid["content"][0]["text"])
    checks.append({"name": "valid_flat_record_passes", "pass": valid_body["valid"]})
    invalid = validate_record({"record": {"mix_design": {"water": 160}}})
    invalid_body = json.loads(invalid["content"][0]["text"])
    checks.append({"name": "nested_record_fails", "pass": not invalid_body["valid"]})
    failed = [check for check in checks if not check["pass"]]
    print(json.dumps({"status": "failed" if failed else "passed", "checks": checks}, indent=2))
    return 1 if failed else 0


def main() -> int:
    parser = argparse.ArgumentParser(description="Read-only Open3DCP MCP-style stdio wrapper")
    parser.add_argument("--smoke-test", action="store_true", help="Run local wrapper smoke checks")
    args = parser.parse_args()
    if args.smoke_test:
        return smoke_test()
    serve_stdio()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
