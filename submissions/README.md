# Submissions catalog

Curated metadata records for datasets contributed through the [Open3DCP intake](https://open3dcp.org/intake/).

**Bytes live in an archive; metadata lives here.** Each record is the metadata for a dataset that is
deposited in a public archive (Zenodo / DesignSafe / MDF-NIST / Dataverse) and referenced by **DOI** —
the dataset files themselves are never committed to this repo. This matches Open3DCP's role as a curation
layer, not an archive.

## Lifecycle

A submission is a **GitHub Issue** opened from the [Dataset Submission form](../.github/ISSUE_TEMPLATE/dataset-submission.yml).
Labels track its state:

| Label | Meaning |
|---|---|
| `intake:staging` | New submission, applied by the form. |
| `intake:staging-ok` / `intake:needs-fixes` | Automated structure check passed / found issues (see the bot comment). |
| `intake:reviewed` | A maintainer has reviewed it. |
| `intake:published` | Accepted — a maintainer applied this, which commits the record here and closes the issue. |

- **`validate-submission.yml`** runs on every submission and edit: it checks required fields, DOI/ORCID
  format, a redistributable license, and DOI de-duplication, then posts a single readiness checklist comment.
  It validates **structure only** — the authoritative 0–100 fidelity score is computed during curation by
  [`open3dcp-ingest`](../tools/ingest/), never invented automatically.
- **`publish-submission.yml`** runs when a maintainer applies `intake:published`: it writes
  `submissions/<issue-number>.json`, appends `index.json`, comments the permalink, and closes the issue.
  Only repo members with write access can trigger it.

## Files

- `index.json` — append-only summary list (id, DOI, title, license, lab, submitter, archive URL, permalink).
- `<NNNN>.json` — the full record for issue `#NNNN`.

## Identity

The submitter's **GitHub account** is the verified identity (recorded as `github_login` + immutable
`github_user_id`). An **ORCID iD** may be declared in the form; it is format/checksum-validated but
**self-asserted**, not OAuth-verified — a curator may cross-check it during review.

## One-time setup (maintainers)

Seed the lifecycle labels once so even the first submission is labeled cleanly (the validate workflow also
creates them defensively):

```bash
gh label create "intake:staging"     --color 0e8a16 --description "New dataset submission" --force
gh label create "intake:staging-ok"  --color 1f6fb2 --description "Automated checks passed" --force
gh label create "intake:needs-fixes" --color b60205 --description "Automated checks found issues" --force
gh label create "intake:reviewed"    --color 5319e7 --description "Curator reviewed" --force
gh label create "intake:published"   --color 0a7d52 --description "Accepted and recorded" --force
```

The publish workflow commits to the default branch; if branch protection later requires pull requests,
switch that step to open a PR instead of pushing directly.
