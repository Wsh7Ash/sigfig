# Usage

## Lab-style calculations

```python
from sigfig import parse, add, multiply, divide, format_measurement

measured = [parse("10.05"), parse("10.02"), parse("10.07")]
total = measured[0]
for value in measured[1:]:
    total = add(total, value)
print(format_measurement(divide(total, parse("3.00"))))
```

Each `add` keeps the smallest decimal place in the chain, so the average keeps
hundredths until the division reduces significant figures.

## Reporting uncertainties

```python
from sigfig import parse_with_uncertainty, add, format_measurement

a = parse_with_uncertainty("1.230 +/- 0.004")
b = parse_with_uncertainty("0.500 +/- 0.002")
print(format_measurement(add(a, b)))   # 1.730 ± 0.004
```

Uncertainties are treated as independent. If two inputs share a calibration
error, their uncertainties are correlated and this model will under-report.

## Teaching significant figures

```shell
sigfig parse 1200        # 2 sigfigs: trailing zeros without a point
sigfig parse 1200.       # 4 sigfigs
sigfig round 0.004567 2  # 0.0046
```

## Choosing the right operation

- Sums and differences of measured quantities → `add` / `subtract`
- Products, ratios, unit conversions → `multiply` / `divide`
- Pure scaling by an exact number → construct `Measurement(Decimal(3), 1)` so the
  exact factor does not artificially reduce precision? Prefer multiplying the
  decimal directly and re-wrapping with the intended sig figs.

## JSON output

```shell
sigfig parse 1.230 --json
```

```json
{
  "value": "1.230",
  "sigfigs": 4,
  "decimal_places": 3,
  "formatted": "1.230",
  "scientific": "1.230e+0"
}
```

Use this when generating reports rather than parsing human text.
