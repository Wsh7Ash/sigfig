# sigfig

**Measurement arithmetic that keeps significant figures honest — no float
surprises, no lost trailing zeros.**

## Why

`2.5 * 4.20` is `10.5` in Python but `11` when you respect significant figures,
and `1.20 + 2.30` should stay at two decimal places. Spreadsheets and floats
quietly break both rules. `sigfig` wraps `Decimal`, tracks how many significant
figures each measurement carries, applies the decimal-place rule for addition
and the significant-figure rule for multiplication, and propagates absolute
uncertainty through both.

## Features

- Parse decimals and scientific notation and infer significant figures
  (trailing zeros in `1200` are treated as not significant; `1200.` keeps four)
- Format with exactly the significant zeros that matter, or in scientific form
- `add`/`subtract` use the fewest decimal places; `multiply`/`divide` use the
  fewest significant figures
- Optional uncertainty: parse `1.230 +/- 0.004`, combine in quadrature, and
  render `1.230 ± 0.004` aligned to the uncertainty
- `ROUND_HALF_UP` on `Decimal`, never binary floats
- CLI (`sigfig parse|calc|round`) and importable library

## Example

```text
$ sigfig calc mul 1.234 5.6
1.234 mul 5.6 = 6.9
$ sigfig parse 0.00450
0.00450  sigfigs=3  dp=5  scientific=4.50e-3
$ sigfig calc add "1.20 +/- 0.05" "2.30 +/- 0.05"
1.20 ± 0.05 add 2.30 ± 0.05 = 3.50 ± 0.07
```

Illustrative output — see `RESULTS.md` for what has actually been executed.

## Architecture

```text
src/sigfig/__init__.py   Measurement, parsing, rounding, arithmetic, formatting
src/sigfig/cli.py        parse / calc / round commands
tests/test_sigfig.py     parsing, rounding, arithmetic, uncertainty, CLI
```

All arithmetic is defined on `Measurement(value: Decimal, sigfigs: int,
uncertainty: Decimal | None)`. Rounding goes through one helper,
`round_to_sigfigs`, which computes the target exponent from `adjusted()` and
quantizes with `ROUND_HALF_UP`.

## Requirements

- Python 3.10+
- pytest for the test suite

## Installation

```shell
git clone https://github.com/Wsh7Ash/sigfig.git
cd sigfig
python -m pip install -e .
```

## Quick start

```python
from sigfig import parse, add, multiply, format_measurement

print(format_measurement(add(parse("12.50"), parse("2.5"))))      # 15.0
print(format_measurement(multiply(parse("1.234"), parse("5.6"))))  # 6.9
```

## Usage

### Library

```python
from decimal import Decimal
from sigfig import (
    Measurement, add, divide, format_measurement, format_scientific,
    parse, parse_with_uncertainty, round_to_sigfigs,
)

length = parse("12.50")
width = parse("2.5")
print(format_measurement(add(length, width)))          # 15.0
print(format_measurement(multiply(length, width)))     # 31 (2 sig figs)

mass = parse_with_uncertainty("1.230 +/- 0.004")
print(format_measurement(mass))                        # 1.230 ± 0.004
print(format_scientific(Measurement(Decimal("12345"), 3)))  # 1.23e+4
print(round_to_sigfigs(Decimal("2.345"), 3))           # 2.35
```

### CLI

```shell
sigfig parse "1.230"
sigfig calc add "12.50" "2.5"
sigfig calc div "10.0" "3.0" --json
sigfig round "2.345" 3
```

Exit codes: `0` ok, `2` invalid literal, zero division or bad precision.

## Configuration

No configuration files. Behaviour is determined by the parsed literals; there is
no global setting for rounding, and `ROUND_HALF_UP` is deliberate.

## Testing

```shell
python -m pip install -e . pytest
python -m pytest tests -q
```

## Project structure

```text
sigfig/
├─ src/sigfig/          library + CLI
├─ tests/               pytest suite
├─ examples/            runnable examples
├─ docs/                architecture, usage, spec
├─ results/             generated output
└─ .github/workflows/   CI
```

## Limitations

- Significant figures are explicit, not inferred from computed Decimals: always
  pass a `Measurement` with an intentional `sigfigs` value.
- Uncertainties are assumed independent; correlated inputs need manual handling.
- Only absolute uncertainty is modelled; confidence levels and units are not.
- The uncertainty display uses one significant figure for the uncertainty.
- Ambiguous integers such as `1200` cannot express "two vs four" figures without
  the explicit `Measurement(..., sigfigs)` constructor.

## Roadmap

- Units with dimensional analysis
- Correlated uncertainty via covariance
- Optional truncation mode for teaching

## License

MIT — see `LICENSE`.
