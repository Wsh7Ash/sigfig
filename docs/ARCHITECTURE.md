# Architecture

## Model

```text
Measurement(value: Decimal, sigfigs: int, uncertainty: Decimal | None)
```

`value` is exact input data, not display text. `sigfigs` is the authority on how
much of it is meaningful. `decimal_places()` converts the pair into a decimal
position: `sigfigs - 1 - value.adjusted()`. The result may be negative, meaning
"round to tens/hundreds".

## Rounding

`round_to_sigfigs(value, n)` computes `places = n - 1 - value.adjusted()` and
quantizes to `10^-places` using `ROUND_HALF_UP`. `Decimal.adjusted()` is the
base-10 exponent of the leading digit, so this works for values far below 1
without special cases.

## Rules

| Operation | Precision rule | Result precision |
|---|---|---|
| `add` / `subtract` | fewest decimal places among inputs | `sigfigs_of(rounded value)` |
| `multiply` / `divide` | fewest significant figures | that minimum |

`sigfigs_of` counts stored digits, so a quantized `15.0` correctly reports three
significant figures rather than the two of the integer `15`.

## Uncertainty

- Addition/subtraction: absolute uncertainties combine in quadrature
  `sqrt(ua² + ub²)` and are quantized to the result's decimal places.
- Multiplication/division: relative uncertainties combine in quadrature and are
  converted back to an absolute value on the result.
- `format_measurement` aligns both value and uncertainty to the leading digit of
  the uncertainty, so `6.0` with `±0.36` renders as `6.0 ± 0.4`.

Zero-valued measurements are treated as having `sigfigs - 1` decimal places;
relative uncertainty is undefined at zero, so no uncertainty is propagated.

## Errors

`SigFigError` for unparseable literals, negative precision or missing `+/-`
separator; `ZeroDivisionError` for division by a zero-valued measurement. The
CLI maps both to exit code 2.
