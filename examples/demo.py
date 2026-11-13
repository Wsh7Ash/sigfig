"""Run with: PYTHONPATH=src python examples/demo.py"""

from decimal import Decimal

from sigfig import (
    Measurement,
    add,
    divide,
    format_measurement,
    format_scientific,
    multiply,
    parse,
    parse_with_uncertainty,
    round_to_sigfigs,
)


def main() -> None:
    print("-- parsing --")
    for literal in ("1.230", "1200", "1200.", "0.00450", "1.23e4"):
        measurement = parse(literal)
        print(
            f"{literal:>8} -> value={format_measurement(measurement):>10} "
            f"sigfigs={measurement.sigfigs} scientific={format_scientific(measurement)}"
        )

    print("\n-- addition: fewest decimal places --")
    total = add(parse("12.50"), parse("2.5"))
    print(f"12.50 + 2.5 = {format_measurement(total)} (sigfigs={total.sigfigs})")

    print("\n-- multiplication: fewest significant figures --")
    product = multiply(parse("2.5"), parse("4.20"))
    print(f"2.5 * 4.20 = {format_measurement(product)} (sigfigs={product.sigfigs})")

    print("\n-- division --")
    ratio = divide(parse("10.0"), parse("3.0"))
    print(f"10.0 / 3.0 = {format_measurement(ratio)}")

    print("\n-- uncertainty --")
    mass = parse_with_uncertainty("1.230 +/- 0.004")
    other = parse_with_uncertainty("0.500 +/- 0.002")
    combined = add(mass, other)
    print(f"{format_measurement(mass)} + {format_measurement(other)} = {format_measurement(combined)}")

    print("\n-- rounding --")
    print(f"round 2.345 to 3 sigfigs = {round_to_sigfigs(Decimal('2.345'), 3)}")
    print(f"scientific 12345 at 3 sigfigs = {format_scientific(Measurement(Decimal('12345'), 3))}")


if __name__ == "__main__":
    main()
