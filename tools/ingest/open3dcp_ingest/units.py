"""Unit conversion to the Open3DCP canonical (SI/metric) units.

Conversions are expressed as a linear factor to a canonical base unit per
dimension. Open3DCP stores MPa for stress/strength, GPa for modulus, Pa for
rheological stress, mm for length, kg/m3 for density, etc. The source dataset's
unit tokens are accepted as input units.
"""
from __future__ import annotations

# token -> (canonical_base_token, factor_to_base)
# Only the units needed by the crosswalk quantity_map + common source units are listed;
# extend as new source units appear.
_FACTORS = {
    # pressure / stress  (base: Pa)
    "Pa": ("Pa", 1.0), "kPa": ("Pa", 1e3), "MPa": ("Pa", 1e6), "GPa": ("Pa", 1e9),
    "bar": ("Pa", 1e5), "psi": ("Pa", 6894.757293), "ksi": ("Pa", 6.894757293e6),
    # length (base: m)
    "nm": ("m", 1e-9), "um": ("m", 1e-6), "mm": ("m", 1e-3), "cm": ("m", 1e-2),
    "m": ("m", 1.0), "in": ("m", 0.0254), "ft": ("m", 0.3048),
    # density (base: kg/m3)
    "kg_m3": ("kg_m3", 1.0), "g_cm3": ("kg_m3", 1000.0), "Mg_m3": ("kg_m3", 1000.0),
    "lb_ft3": ("kg_m3", 16.018463), "lb_yd3": ("kg_m3", 0.59327642),
    # mass (base: kg) -- tonnage MUST be explicit; a bare "ton" is rejected (see convert()).
    # short ton (2000 lb) and long ton (2240 lb) differ from the metric tonne by -9.3% / +1.6%.
    "kg": ("kg", 1.0), "g": ("kg", 1e-3), "lb": ("kg", 0.45359237),
    "tonne": ("kg", 1000.0), "metric_ton": ("kg", 1000.0), "Mg": ("kg", 1000.0),
    "short_ton": ("kg", 907.18474), "long_ton": ("kg", 1016.0469),
    # viscosity (base: Pa_s)
    "Pa_s": ("Pa_s", 1.0), "mPa_s": ("Pa_s", 1e-3), "cP": ("Pa_s", 1e-3),
    # dimensionless / fraction (base: fraction; "%" is /100)
    "-": ("frac", 1.0), "%": ("frac", 0.01), "permille": ("frac", 1e-3),
    "microstrain": ("frac", 1e-6),
    # sorptivity (base: mm_sqrt_s)
    "mm_sqrt_s": ("mm_sqrt_s", 1.0), "mm_sqrt_h": ("mm_sqrt_s", 1.0 / 60.0),
    # time (base: s)
    "s": ("s", 1.0), "min": ("s", 60.0), "h": ("s", 3600.0), "day": ("s", 86400.0),
}

# Open3DCP target token per "base" so we can scale base -> the column's stored unit.
_TARGET_FOR = {
    "MPa": ("Pa", 1e6), "GPa": ("Pa", 1e9), "Pa": ("Pa", 1.0), "kPa": ("Pa", 1e3),
    "mm": ("m", 1e-3), "kg_m3": ("kg_m3", 1.0), "kg": ("kg", 1.0), "Pa_s": ("Pa_s", 1.0),
    "%": ("frac", 0.01), "mm_sqrt_s": ("mm_sqrt_s", 1.0), "day": ("s", 86400.0),
}

# Ambiguous tonnage tokens: a bare "ton"/"t" could be metric (1000 kg), US short (907 kg),
# or UK long (1016 kg) -- up to a ~12% spread. Reject rather than guess.
_AMBIGUOUS = {"ton", "tons", "Ton", "TON", "t", "T"}


class UnitError(ValueError):
    pass


def convert(value, from_unit: str, to_unit: str):
    """Convert a numeric value between unit tokens. Raises UnitError on dimension mismatch."""
    if value is None:
        return None
    if from_unit in _AMBIGUOUS or to_unit in _AMBIGUOUS:
        bad = from_unit if from_unit in _AMBIGUOUS else to_unit
        raise UnitError(
            f"ambiguous tonnage unit {bad!r}; specify metric_ton|short_ton|long_ton "
            "(mass) or Mg_m3|lb_yd3 (density)"
        )
    if from_unit == to_unit:
        return value
    if from_unit not in _FACTORS:
        raise UnitError(f"unknown source unit {from_unit!r}")
    if to_unit not in _TARGET_FOR:
        raise UnitError(f"unknown target unit {to_unit!r}")
    src_base, src_factor = _FACTORS[from_unit]
    tgt_base, tgt_factor = _TARGET_FOR[to_unit]
    if src_base != tgt_base:
        raise UnitError(f"cannot convert {from_unit} ({src_base}) -> {to_unit} ({tgt_base})")
    return value * src_factor / tgt_factor
