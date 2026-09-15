# RILEM flexural specimens with their test context

## Correction made 15 September 2026

The previous nine-row excerpt pooled incompatible test methods, specimen scales and conditions. Its averages cannot support the old 32–55% comparison. The old CSV is retained only as [superseded history](history/rilem-tc304-ils-mech.superseded-2026-09-15.csv). The published manuscript v1.2 describes that frozen historical excerpt; its counts do not describe this new export.

## What one row means

The corrected CSV contains **200 individual flexural specimens**, each with its own source sample identifier in `provenance_notes`. `n_specimens` is 1. Strength and age are copied from that specimen; no averages, standard deviations, cast/printed ratios or effect estimates are calculated.

The companion [provenance ledger](provenance.csv) maps CSV row order to source `sample_id`, full sample name, compound orientation, bending method, source object, process condition, age, dimensions, support/load spans, loading rate, dates and original units. These source identifiers are not specimen-to-print-to-batch validation. The extractor does not guess a parent print or material from a mix prefix. Fresh rheology and print-process settings are therefore omitted rather than copied from the first matching record.

## Inclusion and units

Selection retains the three original mix-name prefixes 01_a, 13_a and 19_a, a finite nonnegative flexural result in N/mm² or MPa, and age from 20 through 40 days. The units are numerically equivalent. Exact prefix matching avoids SQL wildcard ambiguity. All qualifying individual specimens are retained; there is no top-three-orientations rule.

Of 292 source records in those prefixes, 200 are emitted and 92 excluded. The [inclusion ledger](inclusion.csv) records every decision and its source strength/unit. Dispositions: included: 200, missing_nonfinite_or_negative_strength: 1, outside_20_to_40_days: 51, unrecognized_strength_unit: 40.

Corrupted source unit strings are not interpreted as MPa or kg/m³. Unsupported strength units exclude a specimen; unsupported optional dimension/density units leave that output field blank while preserving the source value/unit in the context ledger. Zero is distinct from missing. No conversion based on an assumed density is performed.

## Orientation and comparison limits

Full source codes such as U.W remain intact in the ledger and notes. No first-letter X/Y/Z projection is made. CAST is retained as source preparation; printed compound codes identify printed preparation. Unknown orientation leaves preparation unresolved. Bending-method descriptions remain source context rather than an invented standard code.

Individual records are not automatically comparable or independent. A future analysis must explicitly establish compatible test geometry, method, age, condition and source-linked printing/batch relationships. This export is a traceable conversion example, not a replacement RILEM study.

## Source and reproduction

Bos, F., Robens-Radermacher, A., Muthukrishnan, S., Versteegen, J., Wolfs, R., Santhanam, M., Menna, C., & Mechtcherine, V. / RILEM TC 304-ADC (2024). Database of the RILEM TC 304-ADC interlaboratory study on mechanical properties of 3D printed concrete (ILS-mech) [Dataset]. Zenodo. DOI 10.5281/zenodo.12200570. CC BY 4.0.

License: [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/). Original database/workbook is not re-hosted. Download the source from [its repository](https://zenodo.org/records/12200570). The expected SHA-256 is `674839356d64bf9444b5b1eac8b198f68559129b571da9e82c53ae73c2a3e0df`; a changed source file requires a new audit before replacement.

Run from the repository root:

```sh
python examples/rilem-tc304-ils-mech/build/extract.py "/path/to/2024-06-21_openbis.db" --output-dir /path/to/output
```

The input is opened read-only; the extractor checks its hash again after export. The default output directory is this example folder. [Extraction report](extraction_report.json) · [CSV](rilem-tc304-ils-mech.open3dcp.csv) · [Attribution](NOTICE).
