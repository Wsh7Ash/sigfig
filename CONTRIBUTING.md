# Contributing

## Setup

```shell
python -m pip install -e . pytest
python -m pytest tests -q
```

## Rules that must not regress

- Rounding is `ROUND_HALF_UP` on `Decimal`; do not switch to floats.
- Addition/subtraction uses the fewest decimal places.
- Multiplication/division uses the fewest significant figures.
- Formatting preserves significant zeros (`1.230` stays `1.230`).

## Adding behaviour

1. Implement at the `Measurement` level, not in the CLI.
2. Add a test with a hand-computed expected value and one edge case (zero,
   negative exponent, boundary rounding).
3. Update `docs/ARCHITECTURE.md` precision tables if the rule changes.

## Style

- Standard library only.
- No `eval` of user input; the CLI accepts literals and fixed operations only.
