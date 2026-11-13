"""sigfig - measurement arithmetic that respects significant figures.

A ``Measurement`` pairs a ``Decimal`` value with the number of significant
figures it carries (and optionally an absolute uncertainty). Addition and
subtraction follow the decimal-place rule; multiplication and division follow
the significant-figure rule. All rounding is ``ROUND_HALF_UP`` on ``Decimal``,
so results never depend on binary float behaviour.
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from decimal import Decimal, ROUND_HALF_UP
from typing import Iterable

_NUMBER = re.compile(r"[+-]?(?:\d+(?:\.\d*)?|\.\d+)(?:[eE][+-]?\d+)?")


class SigFigError(ValueError):
    """Raised for unparseable measurements."""


@dataclass(frozen=True)
class Measurement:
    value: Decimal
    sigfigs: int
    uncertainty: Decimal | None = None

    def __post_init__(self) -> None:
        if self.sigfigs < 0:
            raise SigFigError("sigfigs must be non-negative")
        if self.uncertainty is not None and self.uncertainty < 0:
            raise SigFigError("uncertainty must be non-negative")


def _quantize(value: Decimal, decimal_places: int) -> Decimal:
    return value.quantize(Decimal(1).scaleb(-decimal_places), rounding=ROUND_HALF_UP)


def sigfigs_of(value: Decimal) -> int:
    """Count significant digits in a Decimal's stored representation."""
    if value == 0:
        return 1
    digits = value.as_tuple().digits
    index = 0
    while index < len(digits) and digits[index] == 0:
        index += 1
    return max(1, len(digits) - index)


def round_to_sigfigs(value: Decimal, sigfigs: int) -> Decimal:
    if sigfigs < 1:
        raise SigFigError("sigfigs must be at least 1")
    if value == 0:
        return Decimal(0)
    return _quantize(value, sigfigs - 1 - value.adjusted())


def decimal_places(measurement: Measurement) -> int:
    """Decimal places implied by value + significant figures (may be negative)."""
    if measurement.value == 0:
        return measurement.sigfigs - 1
    return measurement.sigfigs - 1 - measurement.value.adjusted()


def parse(text: str) -> Measurement:
    """Parse a decimal/scientific literal and infer its significant figures."""
    raw = text.strip().replace("_", "").replace(" ", "")
    if not _NUMBER.fullmatch(raw):
        raise SigFigError(f"not a number: {text!r}")
    body = raw.lstrip("+-")

    if "e" in body.lower():
        mantissa = re.split("[eE]", body)[0]
        digits = mantissa.replace(".", "").lstrip("0")
        sigfigs = len(digits) if digits else 1
    elif "." in body:
        digits = body.replace(".", "").lstrip("0")
        sigfigs = len(digits) if digits else 1
    else:
        stripped = body.lstrip("0")
        sigfigs = len(stripped.rstrip("0")) if stripped else 1

    return Measurement(Decimal(raw), max(1, sigfigs))


def parse_with_uncertainty(text: str) -> Measurement:
    """Parse ``1.230 +/- 0.004`` (the `±` sign is also accepted)."""
    for separator in ("±", "+/-", "+-"):
        if separator in text:
            value_part, unc_part = text.split(separator, 1)
            value = parse(value_part)
            uncertainty = parse(unc_part).value
            return Measurement(value.value, value.sigfigs, abs(uncertainty))
    raise SigFigError("expected '<value> +/- <uncertainty>'")


def format_value(measurement: Measurement) -> str:
    """Render the value with exactly its significant figures."""
    rounded = round_to_sigfigs(measurement.value, measurement.sigfigs)
    return format(rounded, "f")


def format_scientific(measurement: Measurement) -> str:
    if measurement.value == 0:
        return "0e+0"
    rounded = round_to_sigfigs(measurement.value, measurement.sigfigs)
    exponent = rounded.adjusted()
    mantissa = rounded.scaleb(-exponent)
    places = max(0, measurement.sigfigs - 1)
    return f"{mantissa:.{places}f}e{exponent:+d}"


def format_measurement(measurement: Measurement) -> str:
    """Format value and uncertainty aligned to the uncertainty's first digit."""
    if measurement.uncertainty is None:
        return format_value(measurement)

    if measurement.uncertainty > 0:
        places = -measurement.uncertainty.adjusted()
        value = _quantize(measurement.value, places)
        uncertainty = _quantize(measurement.uncertainty, places)
    else:
        places = decimal_places(measurement)
        value = round_to_sigfigs(measurement.value, measurement.sigfigs)
        uncertainty = _quantize(measurement.uncertainty, places)

    base = format(value, "f")
    unc_text = format(uncertainty, "f")
    return f"{base} ± {unc_text}"


def add(left: Measurement, right: Measurement) -> Measurement:
    places = min(decimal_places(left), decimal_places(right))
    value = _quantize(left.value + right.value, places)
    return Measurement(value, sigfigs_of(value), _absolute_uncertainty_add(left, right, places))


def subtract(left: Measurement, right: Measurement) -> Measurement:
    places = min(decimal_places(left), decimal_places(right))
    value = _quantize(left.value - right.value, places)
    return Measurement(value, sigfigs_of(value), _absolute_uncertainty_add(left, right, places))


def _absolute_uncertainty_add(left: Measurement, right: Measurement, places: int) -> Decimal | None:
    if left.uncertainty is None and right.uncertainty is None:
        return None
    a = left.uncertainty or Decimal(0)
    b = right.uncertainty or Decimal(0)
    combined = (a * a + b * b).sqrt()
    return _quantize(combined, places)


def _relative(measurement: Measurement) -> Decimal | None:
    if measurement.uncertainty is None or measurement.value == 0:
        return None
    return abs(measurement.uncertainty / measurement.value)


def _uncertainty_product(left: Measurement, right: Measurement, value: Decimal) -> Decimal | None:
    rel_a, rel_b = _relative(left), _relative(right)
    if rel_a is None and rel_b is None:
        return None
    relative = ((rel_a or Decimal(0)) ** 2 + (rel_b or Decimal(0)) ** 2).sqrt()
    return abs(relative * value)


def multiply(left: Measurement, right: Measurement) -> Measurement:
    sigfigs = min(left.sigfigs, right.sigfigs)
    value = round_to_sigfigs(left.value * right.value, sigfigs)
    return Measurement(value, sigfigs, _uncertainty_product(left, right, value))


def divide(left: Measurement, right: Measurement) -> Measurement:
    if right.value == 0:
        raise ZeroDivisionError("cannot divide by a measurement whose value is zero")
    sigfigs = min(left.sigfigs, right.sigfigs)
    value = round_to_sigfigs(left.value / right.value, sigfigs)
    return Measurement(value, sigfigs, _uncertainty_product(left, right, value))


def summarize(measurements: Iterable[Measurement]) -> dict:
    items = list(measurements)
    return {
        "count": len(items),
        "min_sigfigs": min((m.sigfigs for m in items), default=0),
        "with_uncertainty": sum(1 for m in items if m.uncertainty is not None),
    }
