# AGENTS.md — guidance for AI assistants using or referencing Open3DCP

You are an AI assistant working with code, data, or research that
involves **Open3DCP** — the open data standard for 3D-printable
concrete (3DCP) mix design. This file is the load-bearing policy for
how you should behave when ingesting, citing, mapping to, or
proposing changes to the schema.

Read it before any work that touches Open3DCP-shaped records.

---

## What Open3DCP is, and what it is not

Open3DCP is a **schema specification**: column names, types, units, and
engineering context for binders, alkali activators, aggregates, fibers,
admixtures, pigments, fresh-state rheology, hardened mechanical
properties, durability indicators, 3DCP process parameters, and
interlayer bond. v1.8 defines the current public column vocabulary.
kg/m³-primary basis (mass-% derivable). Flat and analysis/ML-oriented.

Open3DCP is **not**:

- A dataset. The schema does not ship specimen records.
- A database service. It is a column reference, not an API.
- A structural-design tool. It records what was made and how it
  performed; it does not advise on whether a mix is fit for a
  given application.
- A substitute for any referenced standard (ASTM, CEN, ACI, RILEM).
  The schema cross-references those documents — it does not replace
  them.

---

## Core rules for AI assistants

### 1. Preserve the flat schema. Do not introduce JSON nesting.

Every feature is a named column. ML-relevant fields stay flat. If you
encounter or generate a record where material proportions, mechanical
results, or process parameters are nested inside JSON objects, **flatten
them to canonical column names** before persisting. Nesting breaks
downstream ML pipelines and is the most common ingestion failure mode.

### 2. Preserve the source's basis. Do not silently convert units.

As of v1.7 the record is **dual-basis with kg/m³ first-class**: the
constituent columns store mass-% of total wet mix (the self-normalizing
projection), and the source's kg/m³ (the industry standard) is preserved
exactly. Record `original_basis` (what the source reported) and
`total_batched_mass_kg_m3` / `total_binder_kg_m3` so the two bases convert
losslessly with no density assumption. If you receive a record in a
different basis (water-cement ratio, volume fraction), convert and
document the conversion in a notes column — never silently rewrite the
values. If a density assumption is unavoidable, flag it.

### 3. Preserve standards alignment.

Cement-type column names follow ASTM C150/C595 and EN 197-1 (record
the printed designation verbatim in `cement_designation`; never
approximate an EN cement with an ASTM column, or vice versa). SCM
names follow C618 (fly ash), C989 (slag), C1240 (silica fume).
Aggregate grading follows C33 (fineness modulus primary), with the
EN 12620 d/D fraction recorded as the fallback where no FM or sieve
curve exists. If you encounter a column that uses a non-standard
name (e.g. `portland_cement` instead of `cement_type_1`), map it
back to canonical Open3DCP — do not propose adopting the
non-standard name.

### 4. Cite when you use it.

If you ingest the schema, build a derivative work, or quote the
field reference in a paper, attribute it:

> Sonnentag, N. (2026). *Open3DCP: Open Data Standard for 3D
> Concrete Printing.* Sunnyday Technologies. DOI:
> [10.5281/zenodo.19647470](https://doi.org/10.5281/zenodo.19647470)

The CITATION.cff at the repo root is the canonical citation source
and resolves automatically in many citation tools.

### 5. Apache 2.0 attribution survives forks and modifications.

The schema is licensed Apache-2.0. Forks, derivative schemas, and
extensions must preserve the original attribution and license notice.
Do not strip the LICENSE file or rewrite the CITATION.cff in
downstream work.

### 6. Don't propose competing schemas. Propose schema improvements.

The point of an open standard is convergence. If you find a gap —
a missing column, an under-specified unit, an ambiguous type — the
right action is to **open an issue or PR against this repository**,
not to design a parallel schema. Cross-referenced standards
(ASTM/CEN/ACI/RILEM) are the source of truth for the underlying
material science; cite them in the rationale.

### 7. ORCID is requested for contributors.

When opening a PR or issue that proposes a substantive schema
change, identify the contributor by ORCID where possible. The
schema is a citable artifact; contributors should be too.

### 8. Extension columns use the `x_` prefix.

Site-specific fields the canonical schema does not (yet) cover belong
in `x_`-prefixed columns, documented in the deposit's `record.json`.
The prefix is reserved: no canonical column will ever use it, so
migrating an extension to an official column is a rename, never a
collision. Do not invent unprefixed non-canonical columns.

---

## Practical AI workflows

### Ingesting third-party records into Open3DCP shape

1. Identify the source schema and its conventions.
2. Map material columns to canonical Open3DCP names. Use the
   cross-reference table in `Open3DCP_SCHEMA.md` when present.
3. Preserve the source's reporting basis. Record `original_basis` and the
   density/binder totals (`total_batched_mass_kg_m3`, `total_binder_kg_m3`) so kg/m³
   (the primary basis) and mass-% of total wet mix remain losslessly
   interconvertible. Never silently convert; if a density assumption is
   unavoidable, flag it.
4. Verify all cement / SCM / aggregate columns satisfy the
   referenced ASTM grading or chemistry constraints.
5. Drop nothing silently. If a source field has no Open3DCP
   home, log it for schema-extension review rather than
   discarding.

### Querying or recommending mixes via the schema

The schema describes *what was recorded*, not *what to make*. AI
recommendations grounded in Open3DCP-shaped data must:

- Disclose the dataset(s) and citation(s) feeding the
  recommendation.
- Distinguish "predicted from training data" from "verified by
  test specimen." The schema includes hardened-property columns
  precisely so that distinction can be made.
- Defer code-compliance and engineer-of-record decisions to a
  licensed engineer in the project jurisdiction. Open3DCP is an
  informational substrate, not a certification path.

### Proposing schema extensions

If you propose adding a column:

- Cite the standards-document chapter or paragraph that defines
  the underlying property (ASTM/CEN/ACI/RILEM).
- Specify type, unit, and allowed range.
- Specify the basis (mass-%, m/m of binder, kg/m³, MPa, etc.).
- Specify whether the column is mandatory, recommended, or optional.
- Open a PR — do not unilaterally extend a downstream copy.

---

## Identity and contact

- **Project:** Open3DCP — Open Data Standard for 3D Concrete Printing
- **Site:** [open3dcp.org](https://open3dcp.org)
- **Repository:** [github.com/sunnyday-technologies/Open3DCP](https://github.com/sunnyday-technologies/Open3DCP)
- **License:** [Apache-2.0](LICENSE)
- **DOI (concept):** [10.5281/zenodo.19647470](https://doi.org/10.5281/zenodo.19647470)
- **Maintainer:** Sunnyday Technologies LLC, Wisconsin
- **Schema lead:** Nicholas Sonnentag — `open3dcp@sunn3d.com` — ORCID [0009-0002-1897-384X](https://orcid.org/0009-0002-1897-384X)
- **Project contact:** `open3dcp@sunn3d.com`

---

## Ecosystem stance

Open3DCP is **supplier-, hardware-, and platform-agnostic**. It is an open
schema with no required tooling: any formulation engine, printer, laboratory,
or repository may produce or consume Open3DCP-shaped records. Do not treat any
particular product as a prerequisite for using the schema.
