"""Command line interface for sigfig."""

from __future__ import annotations

import argparse
import json
import sys
from decimal import Decimal

from . import (
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
    subtract,
)

OPERATIONS = {"add": add, "sub": subtract, "mul": multiply, "div": divide}


def _operand(text: str):
    if any(marker in text for marker in ("±", "+/-", "+-")):
        return parse_with_uncertainty(text)
    return parse(text)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="sigfig",
        description="Significant-figure arithmetic with uncertainty propagation.",
    )
    sub = parser.add_subparsers(dest="command", required=True)

    show = sub.add_parser("parse", help="show value, significant figures and scientific form")
    show.add_argument("literal")
    show.add_argument("--json", action="store_true")

    calc = sub.add_parser("calc", help="add, subtract, multiply or divide two measurements")
    calc.add_argument("op", choices=sorted(OPERATIONS))
    calc.add_argument("left")
    calc.add_argument("right")
    calc.add_argument("--json", action="store_true")

    rnd = sub.add_parser("round", help="round a value to a number of significant figures")
    rnd.add_argument("value")
    rnd.add_argument("sigfigs", type=int)
    rnd.add_argument("--json", action="store_true")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)

    try:
        if args.command == "parse":
            measurement = _operand(args.literal)
            payload = {
                "value": str(measurement.value),
                "sigfigs": measurement.sigfigs,
                "decimal_places": decimal_places(measurement),
                "formatted": format_measurement(measurement),
                "scientific": format_scientific(measurement),
            }
            if args.json:
                print(json.dumps(payload, indent=2))
            else:
                print(
                    f"{payload['formatted']}  sigfigs={payload['sigfigs']}  "
                    f"dp={payload['decimal_places']}  scientific={payload['scientific']}"
                )
            return 0

        if args.command == "calc":
            left = _operand(args.left)
            right = _operand(args.right)
            result = OPERATIONS[args.op](left, right)
            payload = {
                "operation": args.op,
                "left": format_measurement(left),
                "right": format_measurement(right),
                "result": format_measurement(result),
                "value": str(result.value),
                "sigfigs": result.sigfigs,
            }
            if args.json:
                print(json.dumps(payload, indent=2))
            else:
                print(f"{payload['left']} {args.op} {payload['right']} = {payload['result']}")
            return 0

        if args.sigfigs < 1:
            raise SigFigError("sigfigs must be at least 1")
        value = parse(args.value).value
        rounded = round_to_sigfigs(value, args.sigfigs)
        text = format(rounded, "f")
        if args.json:
            print(json.dumps({"value": str(value), "sigfigs": args.sigfigs, "rounded": text}, indent=2))
        else:
            print(f"{text} ({args.sigfigs} significant figure{'s' if args.sigfigs != 1 else ''})")
        return 0

    except (SigFigError, ZeroDivisionError, ArithmeticError) as exc:
        print(f"sigfig: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
