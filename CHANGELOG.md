# Changelog

## [1.0.0] - 2026-11-13

### Added

- `Measurement` type pairing a `Decimal` with significant figures and optional
  absolute uncertainty.
- `parse` / `parse_with_uncertainty` with significant-figure inference.
- `round_to_sigfigs`, `format_value`, `format_scientific`, `format_measurement`.
- `add`/`subtract` (decimal-place rule) and `multiply`/`divide`
  (significant-figure rule) with quadrature uncertainty propagation.
- CLI with `parse`, `calc` and `round` commands plus JSON output.
- pytest suite covering parsing, rounding, both precision rules, uncertainty and
  CLI exit codes.
