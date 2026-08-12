# Security and data-integrity reporting

Open3DCP is an open data standard: a schema, a crosswalk, and a set of static
documents. It runs no service and executes no user data, so the realistic risks
are **integrity** rather than compromise — an artifact that does not match what
it claims, an identifier pointing somewhere unintended, or a claim of standing
the project does not have.

## Reporting

Preferred: GitHub's private reporting — **Security → Report a vulnerability** on
<https://github.com/sunnyday-technologies/Open3DCP>. That keeps the report
confidential until a fix is out.

If you cannot use GitHub, email **security@sunn3d.com**. Please do not open a
public issue for anything in the first three categories below.

## In scope

- A published schema or crosswalk artifact whose bytes differ from what this
  repository or the changelog says they should be, or whose `$id` does not match
  the path it is served from.
- A released version's artifact being altered rather than superseded, including
  anything that would make an existing DOI resolve to changed content.
- Personal data (names, emails, phone numbers, postal addresses) in any file.
  Report these privately; they are removed rather than debated.
- Anything served from `open3dcp.org` that this repository does not contain.
- Any published material implying endorsement, certification, or affiliation
  with a standards body. The project explicitly claims none, and a document
  suggesting otherwise is a misrepresentation we want to correct quickly.

## Out of scope

- Values being wrong in an upstream vendor's or paper's data. Open3DCP records
  third-party claims as published and verifies none of them; a wrong vendor
  figure is a data-quality issue, not a security one. Open a normal issue.
- Disagreement with a schema design decision while the standard is in draft.
  Use the working-group review process.
- Findings against other Sunnyday Technologies properties — report those through
  the relevant project, not here.

## Response

We aim to acknowledge within five working days. Integrity fixes ship as a new
version with the reason stated in the changelog; a published artifact is never
silently rewritten.
