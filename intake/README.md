# Open3DCP dataset intake

A zero-backend submission portal served from GitHub Pages at **[open3dcp.org/intake/](https://open3dcp.org/intake/)**.

There is no server, no database, and no secret anywhere: the page collects dataset **metadata + an archive
DOI**, runs honest readiness checks, and hands off to a structured **GitHub Issue Form**. The submission is
a GitHub Issue; the submitter's GitHub account is their verified identity; the dataset bytes stay in a public
archive (Zenodo / DesignSafe / MDF-NIST / Dataverse). GitHub Actions validates and curates from there — see
[`../submissions/README.md`](../submissions/README.md).

## Files

| Path | Purpose |
|---|---|
| `index.html` | The submission page (Open3DCP playbook style). |
| `app.js` | Collects the fields, runs readiness checks, and builds a pre-filled `issues/new` deep-link. No network, no secrets. |
| `styles.css` | Self-contained playbook palette. |

## The deep-link contract

`app.js` builds `https://github.com/sunnyday-technologies/Open3DCP/issues/new?template=dataset-submission.yml&<field_id>=<value>…`.
GitHub Issue Forms pre-fill from query params keyed by each field's `id`, so the field ids in
[`../.github/ISSUE_TEMPLATE/dataset-submission.yml`](../.github/ISSUE_TEMPLATE/dataset-submission.yml) must
match the ids used in `app.js`, the parser, and the validator. Dropdowns and checkboxes **cannot** be
pre-filled via URL, so the license and the two declaration checkboxes are set by the submitter on GitHub.

## Discoverability

The page currently carries `<meta name="robots" content="noindex, nofollow">` while it is in
demonstration. Remove that one line in `index.html` (and add the page to `sitemap.xml`) to make it
discoverable.

## Validate a submission locally

```bash
# from the repo root:
pip install pyyaml
python scripts/test_submission.py                       # parser/validator regression tests
# or check a real submission — paste a rendered issue body into body.md, then:
python scripts/validate_submission.py --body-file body.md
```

Or exercise the workflow end-to-end with [`act`](https://github.com/nektos/act).
