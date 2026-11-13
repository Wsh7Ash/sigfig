import json
import os
import sys
from decimal import Decimal

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

import pytest

from sigfig import (
    Measurement,
    SigFigError,
    add,
    decimal_places,
    divide,
    format_measurement,
    format_scientific,
    format_value,
    multiply,
    parse,
    parse_with_uncertainty,
    round_to_sigfigs,
    sigfigs_of,
    subtract,
    summarize,
)
from sigfig.cli import main


def test_parse_counts_significant_figures():
    assert parse("1.230").sigfigs == 4
    assert parse("0.00450").sigfigs == 3
    assert parse("1200").sigfigs == 2
    assert parse("1200.").sigfigs == 4
    assert parse("1.23e4").sigfigs == 3
    assert parse("-0.0500").sigfigs == 3
    assert parse("100").sigfigs == 1
    assert parse(".5").sigfigs == 1


def test_parse_rejects_garbage():
    with pytest.raises(SigFigError):
        parse("12 apples")
    with pytest.raises(SigFigError):
        parse("1.2.3")


def test_decimal_places_and_sigfigs_of():
    assert decimal_places(parse("1.230")) == 3
    assert decimal_places(parse("0.00450")) == 5
    assert decimal_places(parse("1200")) == -2
    assert sigfigs_of(Decimal("15.0")) == 3
    assert sigfigs_of(Decimal("0.150")) == 3
    assert sigfigs_of(Decimal("1.2E+3")) == 2
    assert sigfigs_of(Decimal(0)) == 1


def test_rounding_is_half_up():
    assert round_to_sigfigs(Decimal("2.345"), 3) == Decimal("2.35")
    assert round_to_sigfigs(Decimal("1234"), 2) == Decimal("1.2E+3")
    assert round_to_sigfigs(Decimal("0.004567"), 2) == Decimal("0.0046")
    assert round_to_sigfigs(Decimal("0"), 3) == 0
    with pytest.raises(SigFigError):
        round_to_sigfigs(Decimal("1"), 0)


def test_formatting_preserves_significant_zeros():
    assert format_value(parse("1.230")) == "1.230"
    assert format_value(parse("1200")) == "1200"
    assert format_value(parse("0.00450")) == "0.00450"
    assert format_scientific(Measurement(Decimal("12345"), 3)) == "1.23e+4"
    assert format_scientific(Measurement(Decimal("0.0001234"), 3)) == "1.23e-4"
    assert format_scientific(Measurement(Decimal("0"), 2)) == "0e+0"


def test_addition_uses_decimal_places():
    result = add(parse("12.50"), parse("2.5"))
    assert result.value == Decimal("15.0")
    assert result.sigfigs == 3
    assert format_measurement(result) == "15.0"
    assert format_measurement(subtract(parse("12.50"), parse("2.5"))) == "10.0"


def test_multiplication_uses_fewest_sigfigs():
    result = multiply(parse("1.234"), parse("5.6"))
    assert result.value == Decimal("6.9")
    assert result.sigfigs == 2
    assert format_measurement(result) == "6.9"
    assert format_measurement(divide(parse("10.0"), parse("3.0"))) == "3.3"


def test_division_by_zero():
    with pytest.raises(ZeroDivisionError):
        divide(parse("1.0"), parse("0.0"))


def test_uncertainty_parsing_and_propagation():
    left = parse_with_uncertainty("1.20 +/- 0.05")
    right = parse_with_uncertainty("2.30 ± 0.05")
    assert left.uncertainty == Decimal("0.05")
    total = add(left, right)
    assert format_measurement(total) == "3.50 ± 0.07"

    product = multiply(Measurement(Decimal("2.0"), 2, Decimal("0.1")),
                       Measurement(Decimal("3.0"), 2, Decimal("0.1")))
    assert product.value == Decimal("6.0")
    assert product.uncertainty is not None
    assert format_measurement(product).startswith("6.0 ± 0.")

    with pytest.raises(SigFigError):
        parse_with_uncertainty("1.2")


def test_summarize():
    stats = summarize([parse("1.20"), parse("3.0"), parse_with_uncertainty("2.0 +/- 0.1")])
    assert stats == {"count": 3, "min_sigfigs": 2, "with_uncertainty": 1}


def test_cli_parse_calc_round_and_errors(capsys):
    assert main(["parse", "0.00450"]) == 0
    out = capsys.readouterr().out
    assert "sigfigs=3" in out and "scientific=4.50e-3" in out

    assert main(["parse", "1.230", "--json"]) == 0
    payload = json.loads(capsys.readouterr().out)
    assert payload["sigfigs"] == 4 and payload["formatted"] == "1.230"

    assert main(["calc", "add", "12.50", "2.5"]) == 0
    assert "= 15.0" in capsys.readouterr().out

    assert main(["calc", "mul", "1.234", "5.6", "--json"]) == 0
    assert json.loads(capsys.readouterr().out)["result"] == "6.9"

    assert main(["round", "2.345", "3"]) == 0
    assert "2.35" in capsys.readouterr().out

    assert main(["calc", "div", "1.0", "0.0"]) == 2
    assert main(["parse", "not-a-number"]) == 2
    assert main(["round", "1.0", "0"]) == 2
