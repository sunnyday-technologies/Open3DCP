# Open3DCP MCP / Agent Wrapper

Experimental read-only wrapper for AI agents that need to inspect Open3DCP schema resources or
validate whether a candidate record is flat and uses known Open3DCP fields.

This tool does not host data, recommend mixes, call CEMFORGE, or perform structural design. It is a
schema helper around the files in this repository.

## Run

```bash
python tools/mcp/open3dcp_mcp_server.py
```

The server speaks a minimal JSON-RPC-over-stdio shape compatible with MCP-style clients that can
call tools over standard input/output. It has no third-party runtime dependencies.

## Tools

- `open3dcp_get_resource`: returns one repository resource such as the schema markdown, SQL DDL,
  README, changelog, LLM summary, or static MCP manifest.
- `open3dcp_list_examples`: lists example `record.json` entries under `examples/`.
- `open3dcp_validate_record`: validates a single JSON object for agent ingestion hygiene:
  flat object, no nested ML fields, known Open3DCP schema fields where possible, and required
  provenance hints such as `original_basis`.

## Smoke Test

```bash
python tools/mcp/open3dcp_mcp_server.py --smoke-test
```

Expected output:

```json
{"status": "passed", "...": "..."}
```

## Boundaries

- Read-only local repository access.
- No network calls.
- No secrets.
- No payment, checkout, or transactional LOGiMIX behavior.
- No physical-performance claims or engineering approval.

Open3DCP records describe what was recorded or measured. Predictions and recommendations must
separately disclose their source, confidence, and physical-validation requirement.
