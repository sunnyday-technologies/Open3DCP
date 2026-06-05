"""Ingestion Fidelity Score (Open3DCP point 1.B).

Deterministic, honest scoring of how much of a source dataset survived translation
into the flat Open3DCP schema. The score decomposes into weighted dimensions; each
dimension plainly lists what was NOT preserved and a triage recommendation, so a
researcher can decide whether the flat projection is sufficient or whether the data
point should be kept in its original / relational form.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from . import transforms
from .ingest import IngestResult

# dimension weights (sum = 1.0)
WEIGHTS = {
    "field_coverage": 0.30,
    "value_fidelity": 0.30,
    "relational_integrity": 0.15,
    "file_data_capture": 0.15,
    "vocabulary_match": 0.10,
}


@dataclass
class Dimension:
    name: str
    score: float
    detail: str
    not_preserved: list[str] = field(default_factory=list)
    triage: str = ""


@dataclass
class FidelityReport:
    overall: float
    grade: str
    dimensions: list[Dimension]
    n_rows: int
    n_source_fields: int
    n_unmapped: int

    def to_dict(self) -> dict[str, Any]:
        return {
            "overall_score": round(self.overall, 1),
            "grade": self.grade,
            "rows": self.n_rows,
            "source_fields": self.n_source_fields,
            "unmapped_fields": self.n_unmapped,
            "dimensions": [
                {"name": d.name, "score": round(d.score, 1), "weight": WEIGHTS[d.name],
                 "detail": d.detail, "not_preserved_examples": d.not_preserved[:10],
                 "triage": d.triage}
                for d in self.dimensions
            ],
        }


def _is_relational_key(source: str) -> bool:
    """A foreign key / identifier (e.g. `specimens.batch_id`) has no place in a denormalized
    flat row -- the join is implicit -- so it must not be penalized as a coverage failure."""
    leaf = source.rsplit(".", 1)[-1].lower()
    return leaf == "id" or leaf.endswith("_id")


def _grade(score: float) -> str:
    if score >= 90: return "A (high fidelity)"
    if score >= 75: return "B (good; review flagged items)"
    if score >= 60: return "C (partial; triage recommended)"
    if score >= 40: return "D (significant loss; keep original)"
    return "F (flat projection inadequate; use relational/original)"


def score(result: IngestResult) -> FidelityReport:
    dims: list[Dimension] = []

    # 1. field coverage --------------------------------------------------------
    src = result.n_source_fields
    mapped = result.n_mapped_fields
    # Plumbing the flat row legitimately does not carry as its own column is excluded from the
    # coverage denominator rather than counted as loss: (a) relational foreign keys / IDs in the
    # sidecar, and (b) selector/metadata fields consumed by a mapping (pivot key, refine key,
    # carry source, data_type, folded curve descriptor) -- counted in result.n_consumed_fields.
    keys = [u for u in result.unmapped if _is_relational_key(u.source)]
    real_dropped = [u for u in result.unmapped if not _is_relational_key(u.source)]
    consumed = result.n_consumed_fields
    eff_src = max(0, src - len(keys) - consumed)
    cov = min(100.0, (mapped / eff_src * 100.0) if eff_src else 100.0)
    excl = []
    if keys:
        excl.append(f"{len(keys)} relational keys/IDs")
    if consumed:
        excl.append(f"{consumed} consumed selector/metadata fields")
    key_note = (f" Excluded from coverage (a flat row carries none as its own column): "
                f"{', '.join(excl)}." if excl else "")
    raw = (mapped / src * 100.0) if src else 100.0
    raw_note = (f" Raw coverage over all {src} populated fields (no exclusions): {raw:.0f}%."
                if (keys or consumed) else "")
    dims.append(Dimension(
        "field_coverage", cov,
        f"{mapped} of {eff_src} mappable source fields mapped to Open3DCP columns "
        f"({len(real_dropped)} routed to triage sidecar).{key_note}{raw_note}",
        not_preserved=sorted(set(u.source for u in real_dropped)),
        triage="Sidecar fields are preserved in <dataset>.unmapped.jsonl; review for schema extension.",
    ))

    # 2. value fidelity (over successfully mapped cells) -----------------------
    traced = result.trace
    if traced:
        assumed = [t for t in traced if t.assumed or t.fidelity == transforms.LOSSY]
        vf = (len(traced) - len(assumed)) / len(traced) * 100.0
        # NOTE: count exact/assumed from the `assumed` LIST (same basis as the score), not the
        # deduplicated `examples` set -- otherwise repeated (target, note) pairs make the prose
        # undercount assumptions and disagree with vf on multi-row datasets.
        examples = sorted({f"{t.target} ({t.note})" for t in assumed})
    else:
        assumed, examples = [], []
        vf = 100.0
    dims.append(Dimension(
        "value_fidelity", vf,
        f"{len(traced)} values written; "
        f"{len(traced) - len(assumed)} exact, {len(assumed)} required an assumption.",
        not_preserved=examples,
        triage="Assumed conversions (e.g. kg/m3<->mass-%, liquid->solids) need the missing "
               "density / solids fraction to become exact. Record mix_density_kg_m3 at source.",
    ))

    # 3. relational integrity (cardinality collapse) --------------------------
    collapse = [u for u in result.unmapped if u.fidelity == transforms.COLLAPSE]
    # penalize proportional to how much relational structure was dropped
    ri = max(0.0, 100.0 - min(100.0, len(collapse) * 8.0))
    dims.append(Dimension(
        "relational_integrity", ri,
        f"{len(collapse)} relational fields (reinforcement, geometry parametrization, "
        f"devices, loading histories) had no flat home.",
        not_preserved=sorted({u.source for u in collapse}),
        triage="Retain these in the source relational record; the flat row is a projection.",
    ))

    # 4. file-referenced data capture -----------------------------------------
    fref = [u for u in result.unmapped if u.fidelity == transforms.FILE_REF]
    fd = 100.0 if not fref else max(0.0, 100.0 - len(fref) * 10.0)
    dims.append(Dimension(
        "file_data_capture", fd,
        f"{len(fref)} curve/table/image/raw-file references cannot be held by the flat schema "
        f"(pre-v1.6).",
        not_preserved=sorted({u.source for u in fref}),
        triage="Link originals in the sidecar; proposed v1.6 *_file columns close this gap.",
    ))

    # 5. vocabulary match ------------------------------------------------------
    cat_cells = [t for t in traced if t.fidelity == transforms.CATEGORICAL]
    cat_unres = [u for u in result.unmapped
                 if "pivot_map" in u.reason or "enum entry" in u.reason]
    denom = len(cat_cells) + len(cat_unres)
    vm = (len(cat_cells) / denom * 100.0) if denom else 100.0
    dims.append(Dimension(
        "vocabulary_match", vm,
        f"{len(cat_cells)} categorical values resolved, {len(cat_unres)} unresolved against the crosswalk.",
        not_preserved=sorted({f"{u.source}={u.value}" for u in cat_unres}),
        triage="Add the unresolved vocab members to the crosswalk pivot/enum maps.",
    ))

    overall = sum(d.score * WEIGHTS[d.name] for d in dims)
    return FidelityReport(overall, _grade(overall), dims,
                          n_rows=len(result.rows), n_source_fields=src,
                          n_unmapped=len(result.unmapped))


def to_markdown(report: FidelityReport, dataset_name: str) -> str:
    lines = [
        f"# Ingestion Fidelity Report — {dataset_name}",
        "",
        f"**Overall fidelity: {report.overall:.1f} / 100 — {report.grade}**",
        "",
        f"- Rows produced: {report.n_rows}",
        f"- Source fields seen: {report.n_source_fields}",
        f"- Fields routed to triage sidecar: {report.n_unmapped}",
        "",
        "| Dimension | Score | Weight | Detail |",
        "|---|---:|---:|---|",
    ]
    for d in report.dimensions:
        lines.append(f"| {d.name} | {d.score:.0f} | {WEIGHTS[d.name]:.2f} | {d.detail} |")
    lines.append("")
    for d in report.dimensions:
        if d.not_preserved:
            lines.append(f"### Not preserved — {d.name}")
            lines.append(f"_{d.triage}_")
            lines.append("")
            for item in d.not_preserved[:25]:
                lines.append(f"- {item}")
            extra = len(d.not_preserved) - 25
            if extra > 0:
                lines.append(f"- … and {extra} more (see sidecar)")
            lines.append("")
    return "\n".join(lines)
