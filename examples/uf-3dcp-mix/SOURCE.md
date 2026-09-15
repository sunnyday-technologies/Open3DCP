# UF mixture and age records with source quantities preserved

## Correction made 15 September 2026

The extractor no longer reads material-name cells as numerical SCM quantities or assigns every row to OPC/blended_OPC. It no longer claims to filter printable Portland-cement mixes or assumes each mechanical specimen was printed. The earlier CSV is retained only as [superseded history](history/uf-3dcp-mix.superseded-2026-09-15.csv).

## What one row means

The corrected CSV contains **10 source-mixture/age records** from **10 source spreadsheet rows**. These are literature records, not newly tested specimens. Selection is the first ten rows in source order with a reference, finite nonnegative static yield stress, water/binder ratio and at least one reported strength; at most two source rows per reference. All reported ages from a selected row are emitted together. Selection is not random and does not establish printability.

Each CSV row names its original Sheet1 row and primary-study reference. The [provenance ledger](provenance.csv) retains binder descriptions and selected-age counts. The [source-cell ledger](source_cells.csv) retains columns 3–96 with their original labels, values and explicit missingness, including binder names, dose/ratio cells, admixtures and activators. A name and its adjacent quantity are different cells. Raw values are not converted or classified in this ledger.

## Reporting basis and missing information

A complete inventory expressed as mass ratios on a common binder basis can be normalized to mass-% without an absolute binder dosage: divide each component ratio by the sum of all component ratios, then multiply by 100. Recovering kg/m³ separately requires an absolute scale.

This workbook excerpt does not establish that complete inventory: blank admixture entries do not mean zero, and some headers mix ratio and percent-of-binder descriptions. Constituent mass-% and kg/m³ therefore remain unconverted. Source cells are preserved so further primary-study curation can resolve those questions without guessing a density or dosage.

`material_class` and `is_3d_printed` remain blank because a source binder label is not a verified class or evidence of how each mechanical specimen was prepared. Reported binder descriptions remain accessible in the ledgers and notes. Unknowns remain usable, traceable unknowns rather than false classifications.

## Units

Static and dynamic yield stress are converted from kPa to Pa by multiplying by 1000. Plastic viscosity remains in Pa·s, strengths in MPa and test ages in days. Relevant source headers and units are checked before extraction. Explicit zero is retained; missing, negative or non-finite numeric input is not treated as a measurement.

## Source and reproduction

Gao, J., Wang, Z., & Wang, C. (2023). 3D Printing Concrete Mix Design Open Dataset (v0.3) [Dataset]. University of Florida. Zenodo. DOI 10.5281/zenodo.6828947. CC BY 4.0.

License: [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/). Original database/workbook is not re-hosted. Download the source from [its repository](https://zenodo.org/records/8070144). The expected SHA-256 is `369369bb2b19610f2ca9eced6cfc395f91e5cf81fec6e63c1fc919bcc1983316`; a changed source file requires a new audit before replacement.

Run from the repository root:

```sh
python examples/uf-3dcp-mix/build/extract.py "/path/to/3D concrete printing mix design dataset v0.3.xlsx" --output-dir /path/to/output
```

The input is opened read-only; the extractor checks its hash again after export. The default output directory is this example folder. [Extraction report](extraction_report.json) · [CSV](uf-3dcp-mix.open3dcp.csv) · [Attribution](NOTICE).
