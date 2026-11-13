# PROJECT_SPEC — sigfig

- **Name:** sigfig
- **Category:** open-source-library
- **Target user:** students, lab authors and engineers doing hand calculations in
  Python who need significant-figure and uncertainty rules applied correctly
- **Problem:** floats and spreadsheets drop trailing zeros and ignore the
  decimal-place / significant-figure rules, producing over-precise results
- **Solution:** a small `Measurement` type plus parse/round/format helpers,
  addition/subtraction/multiplication/division and quadrature uncertainty
  propagation, all on `Decimal`
- **Core workflow:** parse literals → compute → format with the correct zeros
- **Must-have features:** significant-figure parsing, half-up rounding, four
  operations with the right precision rules, scientific formatting, uncertainty
  parse/propagate/format, CLI
- **Nice-to-have features:** units and dimensional analysis, correlated errors
- **Stack:** Python 3.10+ standard library (`decimal`)
- **Test strategy:** pinned significances for known literals, half-up edge cases,
  formatting zeros, both precision rules, uncertainty alignment, CLI output
- **Demo/result strategy:** run `examples/demo.py` and record output in
  `results/`
- **Safety considerations:** pure offline arithmetic; no evaluation of arbitrary
  expressions, so no code injection surface
- **Definition of done:** tests pass, install works, demo recorded, docs accurate,
  no secrets
