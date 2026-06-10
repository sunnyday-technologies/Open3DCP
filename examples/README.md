# Example entries — the open concrete-data landscape

Worked Open3DCP examples converted from **public, openly-licensed** academic and national datasets. Each
carries its source, DOI, license, a `NOTICE`, a `record.json`, the converted flat CSV, and an honest fidelity
report. We commit **small curated excerpts** (reproducible from the source), never bulk re-hosts. Every example
is generic and public; each page shows the source's data classes and storage medium and how it re-formats into
Open3DCP.

## Why one shape matters

Concrete is the most-used material on earth, yet its data is scattered across academic benchmarks, national
repositories, and standards bodies — in incompatible shapes (flat vs relational vs file-based) and unit bases
(kg/m³ vs mass-%). **Open3DCP is the connective layer** across the experiment record: mix design → 3DCP
process → fresh rheology → hardened mechanical → durability → interlayer bond → embodied carbon → multi-age
strength. Put in one shape, openly licensed, each contributed record becomes usable alongside every other.

## Coverage — each source lights up a slice; Open3DCP spans the whole

| Source | Provenance | Mix design | Rheology | 3DCP process | Hardened mech. | Multi-age | Environment |
|---|:--:|:--:|:--:|:--:|:--:|:--:|:--:|
| [UCI Concrete Strength (Yeh 1998)](uci-yeh-1998/) — *cast, **100/A*** | ▢ | ✓ | ▢ | ▢ | ✓ | ✓ | ▢ |
| [Meta SustainableConcrete](meta-sustainableconcrete/) — *cast, **100/A*** | ▢ | ✓ | ▢ | ▢ | ✓ | ✓ | ✓ |
| [RILEM TC 304-ADC ILS-mech](rilem-tc304-ils-mech/) — *3DCP* | ✓ | ▢¹ | ✓ | ✓ | ✓ | ▢ | ▢ |
| [UF 3DCP mix-design](uf-3dcp-mix/) — *3DCP* | ▢ | ◐ | ✓ | ✓ | ✓ | ▢ | ▢ |
| [TU-Braunschweig 3DCP buildings](tu-braunschweig-buildings/) — *project layer* | ✓ | ▢ | ▢ | ◐ | ▢ | ▢ | ▢ |

¹ commercial premix — w/b and yield stress captured, constituent dosages not disclosed. The **gaps between
slices are the connective-layer argument**: no single source spans the whole record; the union does. *Two
sources carry a real `open3dcp-ingest` fidelity score (kg/m³ tables — both 100/A: zero assumptions under v1.7.5's preserve-don't-presume columns, with generically-recorded cells disclosed); the 3DCP-mix
and project-layer sources are hand-curated because their native bases (ratio-to-binder; project metadata) are
not yet auto-scored.* A surveyed UHPC source, **Stevens UHPC** (Mahjoubi & Bao, US — CC BY 4.0), was excluded
as reference-only: its mix variables are published as a coded ML feature matrix whose legend is paywalled, so
it is not re-ingested here.

## Storable vs reference-only

**The rule:** store only when the license clearly permits redistribution — **CC BY 4.0**, **CC0**, **US-government
public domain**, **GODL-India**, or a **permissive software license** (MIT/BSD/Apache) that allows redistribution — with attribution. Anything copyrighted, registration-gated, or unclear is
**reference-only** and cited respectfully (never stored).

**Storable** (built / verified): UCI Concrete Strength (CC BY 4.0) · Meta SustainableConcrete (MIT) ·
RILEM TC 304-ADC ILS-mech (CC BY 4.0) · UF 3DCP mix-design (CC BY 4.0) ·
TU-Braunschweig 3DCP Buildings (CC BY 4.0) · NIST Construction Materials Repository (US public domain) ·
JCI–JACT articles (CC BY 4.0, per-paper).

**Reference-only** (cited, not stored): Stevens UHPC (Mahjoubi & Bao — CC BY 4.0 but a *coded ML feature
matrix*; variable legend paywalled, so not honestly re-ingestible) · TU/e interlayer-bond + sensory set
(Versteege & Wolfs — **CC BY-SA**, copyleft ShareAlike rather than plain CC BY) · ACI (copyrighted /
request-gated) · NIMS MatNavi (self-use-only terms) · China NMDMS / Materials Genome platforms (no data
license, registration-gated) · Russia GOST standards (copyrighted) · EU NOMAD / Materials Project (atomistic,
no concrete) · image-only datasets (no mix/mechanical scalars).

**Out of scope (chemistry):** low-calcium fly-ash **geopolymers** (N-A-S-H gel — not hydraulic) are
excluded; alkali-activated-concrete corpora that are predominantly geopolymer (e.g. the BAM/TU-Berlin AAC
set, predominantly low-calcium fly-ash geopolymer) are therefore not ingested. Open3DCP covers hydraulic cementitious systems (Portland,
blended, CAC/CSA, and high-calcium alkali-activated slag).

## National map — open concrete & materials-data efforts

- **USA** — NIST (Materials Genome Initiative; Federal LCA Commons = storable, env) · UCI ML Repository (CC BY 4.0,
  storable) · **Meta SustainableConcrete** (Meta + UIUC + Amrize; MIT, storable — mix design + per-mix CO₂) ·
  Stevens UHPC (CC BY 4.0; coded matrix → reference) · UF 3DCP mix-design (CC BY 4.0, storable) · ACI (reference).
- **International / EU** — **RILEM** TC 304-ADC (the 3DCP standards anchor; ILS-mech is storable) · NOMAD (FAIR
  exemplar, no concrete).
- **Germany** — BAM + NFDI-MatWerk (FAIR infrastructure); their Zenodo concrete deposits are CC BY 4.0 storable.
- **Japan** — NIMS MatNavi (national DB, registration-gated → reference) · JCI–JACT (CC BY 4.0, per-paper storable).
- **China** — National Materials Genome stack (no license / gated → reference); CAS ScienceDB is a storable
  *platform* (CC0/CC BY) once a concrete deposit is verified.
- **South Korea** — KISTI DataON (metadata aggregator; per-record license).
- **India** — NDSAP / GODL-India permits redistribution (a future India concrete dataset would be storable);
  India participates directly via IIT Madras in the storable RILEM ILS-mech.
- **Russia** — GOST standards (cite method codes only); no open concrete dataset located.

Open3DCP interoperates by preserving provenance (`doi` / `source_citation` / `lab_name`) on every row, hosting via
GitHub + a Zenodo concept DOI, and honoring each source's license (CC BY attribution, NIST AS-IS, standards
designations for identification only).

## How each example is built

`open3dcp-ingest` converts the source into the flat schema and emits an honest 0–100 fidelity report (it never
invents a score). Conventions: **NULL, not 0**, for anything unreported; RILEM **U/V/W → X/Y/Z/CAST** orientation
crosswalk (raw code kept in `provenance_notes`); per-measurement **mean + std-dev + n**. Where a turnkey reader
exists (UCI), CI re-runs the `build_cmd` and **diffs** the output so the example can't drift; where a source needs
a reader still to be written (RILEM SQLite), the excerpt is hand-curated with a committed, documented
`build/extract.py`.

## Licensing, attribution, trademarks

Each dataset folder carries a `NOTICE` with the exact CC BY attribution (or NIST AS-IS disclaimer). Standards
designations (ASTM / EN / ACI / RILEM / GOST) are cited for identification only; trademarks belong to their owners.
This directory is a schema demonstration, not an endorsement by any source.

## Contribute

Have an openly-licensed dataset to add? Use the [submission portal](https://open3dcp.org/intake/) — provenance +
an archive DOI + a redistributable license. See the storable-license rule above.
