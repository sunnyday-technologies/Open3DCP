"""Named value transforms referenced by the crosswalk.

Every transform returns a `TransformResult` carrying the converted value, the
realized fidelity class, whether an assumption had to be made, and a short note.
The engine accumulates these so the fidelity scorer can report exactly what was
preserved and what required an assumption -- the "drop nothing silently" rule.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

from . import units

# Fidelity classes (ordered best -> worst) -- kept in sync with the crosswalk.
EXACT = "exact"
DERIVED = "derived"
CATEGORICAL = "categorical"
LOSSY = "lossy"
COLLAPSE = "collapse"
FILE_REF = "file_ref"
NONE = "none"


@dataclass
class TransformResult:
    value: Optional[object]
    fidelity: str
    assumed: bool = False
    note: str = ""


def identity(value, ctx=None, **kw) -> TransformResult:
    return TransformResult(value, EXACT)


def unit_convert(value, ctx=None, from_unit=None, to_unit=None, **kw) -> TransformResult:
    if value is None:
        return TransformResult(None, EXACT)
    if from_unit is None:
        return TransformResult(value, LOSSY, assumed=True, note="source unit unknown; passed through unconverted")
    out = units.convert(float(value), from_unit, to_unit)
    return TransformResult(out, EXACT, note=f"{from_unit}->{to_unit}")


def kg_m3_to_mass_pct(value, ctx=None, **kw) -> TransformResult:
    """x_kg_m3 / total_wet_mass_kg_m3 * 100.

    Exact when the full batch mass is known (all constituents incl. water reported);
    otherwise lossy because total wet mass had to be assumed.
    """
    if value is None:
        return TransformResult(None, EXACT)
    total = (ctx or {}).get("total_wet_mass_kg_m3")
    if total and total > 0:
        exact = (ctx or {}).get("total_wet_mass_is_complete", False)
        return TransformResult(
            float(value) / total * 100.0,
            EXACT if exact else LOSSY,
            assumed=not exact,
            note="full batch known" if exact else "total wet mass partially inferred",
        )
    return TransformResult(None, LOSSY, assumed=True,
                           note="total wet mass unknown; cannot convert kg/m3 -> mass-% (sidecar kg/m3)")


def mass_pct_to_kg_m3(value, ctx=None, **kw) -> TransformResult:
    if value is None:
        return TransformResult(None, EXACT)
    rho = (ctx or {}).get("mix_density_kg_m3")
    if rho and rho > 0:
        return TransformResult(float(value) / 100.0 * rho, LOSSY, assumed=True,
                               note="used mix_density")
    return TransformResult(None, LOSSY, assumed=True, note="mix_density unknown")


def as_delivered_to_solids_pct(value, ctx=None, solids_fraction=None, **kw) -> TransformResult:
    if value is None:
        return TransformResult(None, EXACT)
    # A zero (absent) admixture carries no solids-vs-as-delivered ambiguity: 0 as-delivered = 0
    # solids. Flagging it 'assumed' wrongly penalizes value_fidelity for an absent constituent.
    if float(value) == 0.0:
        return TransformResult(0.0, EXACT, note="zero dose; admixture absent")
    total = (ctx or {}).get("total_wet_mass_kg_m3")
    sf = solids_fraction if solids_fraction is not None else (ctx or {}).get("solids_fraction")
    if total and total > 0 and sf:
        return TransformResult(float(value) * sf / total * 100.0, LOSSY, assumed=True,
                               note=f"assumed solids fraction {sf}")
    # store as-delivered mass-% if total known, else give up to sidecar
    if total and total > 0:
        return TransformResult(float(value) / total * 100.0, LOSSY, assumed=True,
                               note="solids fraction unknown; recorded as-delivered mass-% (not solids)")
    return TransformResult(None, LOSSY, assumed=True, note="total wet mass + solids fraction unknown")


def ml_m3_to_mass_pct(value, ctx=None, product_density=None, solids_fraction=None, **kw) -> TransformResult:
    if value is None:
        return TransformResult(None, EXACT)
    return TransformResult(None, LOSSY, assumed=True,
                           note="volume dose (ml/m3): needs product density + solids fraction; routed to sidecar")


def vol_fraction_to_mass_pct(value, ctx=None, **kw) -> TransformResult:
    if value is None:
        return TransformResult(None, EXACT)
    fiber_rho = (ctx or {}).get("fiber_density")
    mix_rho = (ctx or {}).get("mix_density_kg_m3")
    if fiber_rho and mix_rho:
        # value is a volume fraction (0-1 or %); normalize if given as %
        vf = float(value) / 100.0 if float(value) > 1.0 else float(value)
        return TransformResult(vf * fiber_rho / mix_rho * 100.0, LOSSY, assumed=True,
                               note="used fiber & mix densities")
    return TransformResult(None, LOSSY, assumed=True,
                           note="fiber/mix density unknown; volume fraction kept in sidecar")


def enum_map(value, ctx=None, mapping=None, **kw) -> TransformResult:
    if value is None:
        return TransformResult(None, EXACT)
    mapping = mapping or {}
    if value in mapping:
        return TransformResult(mapping[value], CATEGORICAL, note=f"{value}->{mapping[value]}")
    return TransformResult(value, CATEGORICAL, assumed=True, note=f"no enum entry for {value!r}; passed through")


REGISTRY = {
    "identity": identity,
    "unit_convert": unit_convert,
    "kg_m3_to_mass_pct": kg_m3_to_mass_pct,
    "mass_pct_to_kg_m3": mass_pct_to_kg_m3,
    "as_delivered_to_solids_pct": as_delivered_to_solids_pct,
    "ml_m3_to_mass_pct": ml_m3_to_mass_pct,
    "vol_fraction_to_mass_pct": vol_fraction_to_mass_pct,
    "enum_map": enum_map,
}


def apply(name, value, ctx=None, **kw) -> TransformResult:
    fn = REGISTRY.get(name)
    if fn is None:
        return TransformResult(value, LOSSY, assumed=True, note=f"unknown transform {name!r}")
    return fn(value, ctx=ctx, **kw)
