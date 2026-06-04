#!/usr/bin/env python3
"""Build submissions/<NNNN>.json from a published issue and append submissions/index.json.

Run by .github/workflows/publish-submission.yml after a maintainer applies the `intake:published`
label. Reads the issue from the environment: ISSUE_BODY, ISSUE_NUMBER, ISSUE_USER, ISSUE_USER_ID,
ISSUE_URL. The dataset bytes live in an external archive (by DOI); only this metadata record is
committed to the repo.
"""
import datetime
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from parse_submission import DEFAULT_FORM, load_fields, parse_body  # noqa: E402
from validate_submission import REPO_ROOT, normalize_doi  # noqa: E402

SUBM_DIR = os.path.join(REPO_ROOT, "submissions")
INDEX = os.path.join(SUBM_DIR, "index.json")


def load_index():
    if not os.path.exists(INDEX):
        return []
    try:
        with open(INDEX, encoding="utf-8") as fh:
            data = json.load(fh)
        return data if isinstance(data, list) else []
    except (json.JSONDecodeError, OSError):
        return []


def main():
    num = int(os.environ["ISSUE_NUMBER"])
    parsed = parse_body(os.environ.get("ISSUE_BODY", ""), load_fields(DEFAULT_FORM))
    now = datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    orcid = (parsed.get("declared_orcid") or "").strip() or None

    record = {
        "id": num,
        "dataset_title": parsed.get("dataset_title", ""),
        "dataset_doi": normalize_doi(parsed.get("dataset_doi", "")),
        "archive_url": parsed.get("archive_url", ""),
        "source_citation": parsed.get("source_citation", ""),
        "lab_name": parsed.get("lab_name", ""),
        "license": parsed.get("license", ""),
        "schema_version": parsed.get("schema_version", ""),
        "notes": (parsed.get("notes") or "").strip() or None,
        "redistribution_confirmed": bool(parsed.get("redistribution_confirmed")),
        "submitter": {
            "github_login": os.environ.get("ISSUE_USER", ""),
            "github_user_id": int(os.environ["ISSUE_USER_ID"]) if os.environ.get("ISSUE_USER_ID") else None,
            "declared_orcid": orcid,
        },
        "issue_url": os.environ.get("ISSUE_URL", ""),
        "published_at": now,
        # The authoritative 0-100 score is attached during curation by open3dcp-ingest, not invented here.
        "fidelity": None,
    }

    os.makedirs(SUBM_DIR, exist_ok=True)
    with open(os.path.join(SUBM_DIR, f"{num:04d}.json"), "w", encoding="utf-8") as fh:
        json.dump(record, fh, indent=2, ensure_ascii=False)
        fh.write("\n")

    index = [r for r in load_index() if r.get("id") != num]  # replace on re-publish
    index.append({
        "id": num,
        "dataset_title": record["dataset_title"],
        "dataset_doi": record["dataset_doi"],
        "license": record["license"],
        "lab_name": record["lab_name"],
        "submitter": record["submitter"]["github_login"],
        "archive_url": record["archive_url"],
        "issue_url": record["issue_url"],
        "published_at": now,
    })
    index.sort(key=lambda r: r.get("id", 0))
    with open(INDEX, "w", encoding="utf-8") as fh:
        json.dump(index, fh, indent=2, ensure_ascii=False)
        fh.write("\n")

    print(f"wrote submissions/{num:04d}.json; index now has {len(index)} record(s)")


if __name__ == "__main__":
    main()
