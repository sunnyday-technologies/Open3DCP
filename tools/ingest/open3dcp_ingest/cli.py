"""Command-line interface for open3dcp-ingest.

    open3dcp-ingest convert SOURCE [--kind relational|uci] [--out DIR] [--crosswalk FILE]

Writes, into --out (default: alongside SOURCE):
    <name>.open3dcp.csv      flat Open3DCP rows
    <name>.unmapped.jsonl    triage sidecar (every field with no flat home -- drop nothing)
    <name>.fidelity.json     machine-readable fidelity score
    <name>.fidelity.md       human-readable fidelity report
"""
from __future__ import annotations

import argparse
import csv
import json
import os
import sys
from dataclasses import asdict

from . import convert, fidelity as _fidelity, __version__, TARGET_SCHEMA_VERSION


def _write_outputs(result, report, source_path, out_dir):
    base = os.path.splitext(os.path.basename(source_path))[0]
    os.makedirs(out_dir, exist_ok=True)

    # flat rows -> CSV (union of all keys, stable order of first appearance)
    cols: list[str] = []
    for row in result.rows:
        for k in row:
            if k not in cols:
                cols.append(k)
    csv_path = os.path.join(out_dir, f"{base}.open3dcp.csv")
    with open(csv_path, "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=cols)
        w.writeheader()
        for row in result.rows:
            w.writerow(row)

    # sidecar
    side_path = os.path.join(out_dir, f"{base}.unmapped.jsonl")
    with open(side_path, "w", encoding="utf-8") as fh:
        for u in result.unmapped:
            fh.write(json.dumps(asdict(u), default=str) + "\n")

    # fidelity
    fj = os.path.join(out_dir, f"{base}.fidelity.json")
    with open(fj, "w", encoding="utf-8") as fh:
        json.dump(report.to_dict(), fh, indent=2)
    fm = os.path.join(out_dir, f"{base}.fidelity.md")
    with open(fm, "w", encoding="utf-8") as fh:
        fh.write(_fidelity.to_markdown(report, base))
    return csv_path, side_path, fj, fm


def main(argv=None) -> int:
    p = argparse.ArgumentParser(prog="open3dcp-ingest",
                                description="Translate external concrete datasets into the Open3DCP flat schema.")
    p.add_argument("--version", action="version",
                   version=f"open3dcp-ingest {__version__} (targets Open3DCP schema v{TARGET_SCHEMA_VERSION})")
    sub = p.add_subparsers(dest="cmd", required=True)
    c = sub.add_parser("convert", help="convert a dataset and score fidelity")
    c.add_argument("source")
    c.add_argument("--kind", choices=["relational", "uci", "flat"], default=None)
    c.add_argument("--out", default=None, help="output directory (default: alongside source)")
    c.add_argument("--crosswalk", default=None, help="path to crosswalk YAML")
    args = p.parse_args(argv)

    if args.cmd == "convert":
        if not os.path.exists(args.source):
            print(f"error: source not found: {args.source}", file=sys.stderr)
            return 2
        result, report = convert(args.source, kind=args.kind, crosswalk_path=args.crosswalk)
        out_dir = args.out or os.path.dirname(os.path.abspath(args.source))
        csv_path, side_path, fj, fm = _write_outputs(result, report, args.source, out_dir)
        if result.crosswalk_schema_version and result.crosswalk_schema_version != TARGET_SCHEMA_VERSION:
            print(f"WARNING: crosswalk targets schema v{result.crosswalk_schema_version} but this tool "
                  f"targets v{TARGET_SCHEMA_VERSION}. Update the crosswalk or tool to match.", file=sys.stderr)
        print(f"source kind     : {result.source_kind}")
        print(f"rows produced   : {len(result.rows)}")
        print(f"fidelity score  : {report.overall:.1f}/100  {report.grade}")
        print(f"sidecar entries : {len(result.unmapped)} (nothing dropped)")
        print("written:")
        for pth in (csv_path, side_path, fj, fm):
            print(f"  {pth}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
