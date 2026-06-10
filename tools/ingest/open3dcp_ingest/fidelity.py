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
    applicable: bool = True   # a dimension the source could actually exercise; N/A dims are excluded
                              # from the weighted average (weights renormalize over applicable dims)


@dataclass
class FidelityReport:
    overall: float
    grade: str
    dimensions: list[Dimension]
    n_rows: int
    n_source_fields: int
    n_unmapped: int
    weakest_link: str = ""

    def to_dict(self) -> dict[str, Any]:
        app = [d for d in self.dimensions if d.applicable]
        wsum = sum(WEIGHTS[d.name] for d in app) or 1.0
        return {
            "overall_score": round(self.overall, 1),
            "grade": self.grade,
            "weakest_applicable_dimension": self.weakest_link,
            "rows": self.n_rows,
            "source_fields": self.n_source_fields,
            "unmapped_fields": self.n_unmapped,
            "scored_over": "applicable dimensions only (weights renormalized)",
            "dimensions": [
                {"name": d.name, "score": round(d.score, 1),
                 "weight": round(WEIGHTS[d.name] / wsum, 3) if d.applicable else 0.0,
                 "nominal_weight": WEIGHTS[d.name], "applicable": d.applicable,
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


_GRADE_LABEL = {
    "A": "A (high fidelity)", "B": "B (good; review flagged items)",
    "C": "C (partial; triage recommended)", "D": "D (significant loss; keep original)",
    "F": "F (flat projection inadequate; use relational/original)",
}
_GRADE_ORDER = ["A", "B", "C", "D", "F"]


def _grade(score: float) -> str:
    if score >= 90: return _GRADE_LABEL["A"]
    if score >= 75: return _GRADE_LABEL["B"]
    if score >= 60: return _GRADE_LABEL["C"]
    if score >= 40: return _GRADE_LABEL["D"]
    return _GRADE_LABEL["F"]


def _cap_grade(grade: str, weakest: float) -> str:
    """Weakest-link gate: the letter can be no better than the weakest APPLICABLE dimension warrants,
    so a catastrophic single-dimension loss cannot read 'A' behind a high weighted average."""
    cap = "A"
    if weakest < 40: cap = "D"
    elif weakest < 60: cap = "C"
    elif weakest < 80: cap = "B"   # an 'A (high fidelity)' requires every applicable dimension to be
                                   # genuinely strong; a weak value_fidelity caps the grade at B
    if _GRADE_ORDER.index(grade[0]) < _GRADE_ORDER.index(cap):
        return _GRADE_LABEL[cap] + " — capped by the weakest dimension"
    return grade


def score(result: IngestResult) -> FidelityReport:
    dims: list[Dimension] = []
    traced = result.trace

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

    # 2. value fidelity = ASSUMPTION-FREE fraction of substantive value cells ----
    # "Substantive" excludes (a) zero-dose absences (0 -> 0, an absent constituent, no conversion) and
    # (b) file/relational cells (scored by their own dimensions) -- so the denominator can't be padded
    # with trivially-exact cells. A cell rests on an assumption if its realized fidelity is LOSSY
    # (a value approximation OR a crosswalk-declared bucketing, via worst(declared, runtime)) or it
    # carries an engine assumption flag (a defaulted cement type, an enum pass-through).
    def _trivial(t):
        return ("zero dose" in t.note or "admixture absent" in t.note
                or t.fidelity in (transforms.FILE_REF, transforms.COLLAPSE))
    substantive = [t for t in traced if not _trivial(t)]
    assumed = [t for t in substantive if t.assumed or t.fidelity == transforms.LOSSY]
    vf = ((len(substantive) - len(assumed)) / len(substantive) * 100.0) if substantive else 100.0
    examples = sorted({f"{t.target} ({t.note})" for t in assumed})
    dims.append(Dimension(
        "value_fidelity", vf,
        f"{len(substantive)} substantive value cells: {len(substantive) - len(assumed)} stored without "
        f"an assumption, {len(assumed)} rest on one (liquid->solids admixture, FM/size aggregate bucket, "
        f"defaulted cement type, or an incomplete-batch projection).",
        not_preserved=examples,
        triage="Assumed cells need the missing source detail (solids fraction, fineness modulus, "
               "aggregate size, cement type) to become exact; the value is recorded, the attribute is inferred.",
        applicable=bool(substantive),
    ))

    # 3. relational integrity -- N/A for a flat/UCI source (no one-to-many to lose) ----
    collapse = [u for u in result.unmapped if u.fidelity == transforms.COLLAPSE]
    ri = max(0.0, 100.0 - min(100.0, len(collapse) * 8.0))
    dims.append(Dimension(
        "relational_integrity", ri,
        f"{len(collapse)} relational fields (reinforcement, geometry parametrization, "
        f"devices, loading histories) had no flat home."
        + ("" if result.source_kind == "relational" else " N/A: a flat source has no relational cardinality."),
        not_preserved=sorted({u.source for u in collapse}),
        triage="Retain these in the source relational record; the flat row is a projection.",
        applicable=(result.source_kind == "relational"),
    ))

    # 4. file-referenced data capture -- N/A unless the source carried file references ----
    fref = [u for u in result.unmapped if u.fidelity == transforms.FILE_REF]
    file_traced = [t for t in traced if t.fidelity == transforms.FILE_REF]
    has_files = bool(fref or file_traced)
    fd = 100.0 if not fref else max(0.0, 100.0 - len(fref) * 10.0)
    dims.append(Dimension(
        "file_data_capture", fd,
        f"{len(fref)} curve/table/image/raw-file references not captured; {len(file_traced)} routed to "
        f"*_file columns." + ("" if has_files else " N/A: this source carries no file-referenced data."),
        not_preserved=sorted({u.source for u in fref}),
        triage="Link originals in the sidecar; the v1.7 *_file columns close this gap.",
        applicable=has_files,
    ))

    # 5. vocabulary match -- categorical resolution; unresolved = enum miss + pivot miss ----
    cat_resolved = [t for t in traced
                    if t.fidelity == transforms.CATEGORICAL and "no enum entry" not in t.note]
    cat_unres_trace = [t for t in traced
                       if t.fidelity == transforms.CATEGORICAL and "no enum entry" in t.note]
    cat_unres_side = [u for u in result.unmapped
                      if "pivot_map" in u.reason or "enum entry" in u.reason]
    denom = len(cat_resolved) + len(cat_unres_trace) + len(cat_unres_side)
    vm = (len(cat_resolved) / denom * 100.0) if denom else 100.0
    dims.append(Dimension(
        "vocabulary_match", vm,
        f"{len(cat_resolved)} categorical values resolved to canonical codes, "
        f"{len(cat_unres_trace) + len(cat_unres_side)} unresolved (enum/pivot miss, passed through)."
        + ("" if denom else " N/A: this source has no categorical vocabulary to resolve."),
        not_preserved=sorted({f"{u.source}={u.value}" for u in cat_unres_side}
                             | {f"{t.target} ({t.note})" for t in cat_unres_trace}),
        triage="Add the unresolved vocab members to the crosswalk pivot/enum maps.",
        applicable=(denom > 0),
    ))

    # overall: renormalize the weights over the APPLICABLE dimensions only, so a flat table is not
    # floated to an 'A' by three structural 100s it never had a chance to fail.
    app = [d for d in dims if d.applicable]
    wsum = sum(WEIGHTS[d.name] for d in app)
    overall = (sum(d.score * WEIGHTS[d.name] for d in app) / wsum) if wsum else 100.0
    weakest = min(app, key=lambda d: d.score) if app else dims[0]
    grade = _cap_grade(_grade(overall), weakest.score)
    return FidelityReport(overall, grade, dims,
                          n_rows=len(result.rows), n_source_fields=src,
                          n_unmapped=len(result.unmapped),
                          weakest_link=f"{weakest.name} ({weakest.score:.0f})")


def to_markdown(report: FidelityReport, dataset_name: str) -> str:
    app = [d for d in report.dimensions if d.applicable]
    wsum = sum(WEIGHTS[d.name] for d in app) or 1.0
    lines = [
        f"# Ingestion Fidelity Report — {dataset_name}",
        "",
        f"**Overall fidelity: {report.overall:.1f} / 100 — {report.grade}**",
        "",
        f"- Rows produced: {report.n_rows}",
        f"- Source fields seen: {report.n_source_fields}",
        f"- Fields routed to triage sidecar: {report.n_unmapped}",
        f"- Weakest applicable dimension: {report.weakest_link}",
        f"- Scored over the **applicable** dimensions only "
        f"({', '.join(d.name for d in app)}); weights renormalized.",
        "",
        "| Dimension | Score | Eff. weight | Applicable | Detail |",
        "|---|---:|---:|:--:|---|",
    ]
    for d in report.dimensions:
        ew = f"{WEIGHTS[d.name] / wsum:.2f}" if d.applicable else "—"
        app_mark = "yes" if d.applicable else "N/A"
        lines.append(f"| {d.name} | {d.score:.0f} | {ew} | {app_mark} | {d.detail} |")
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
