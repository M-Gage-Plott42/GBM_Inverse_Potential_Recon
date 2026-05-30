"""Command-line entry points for the public smoke demo."""

from __future__ import annotations

import argparse
import json
from typing import Sequence

from .fourier import harmonic_oscillator_demo


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Run the inverse-potential oscillator smoke demo.")
    parser.add_argument("--alpha", type=float, default=1.0, help="Oscillator alpha parameter.")
    parser.add_argument("--r-points", type=int, default=400, help="Number of radial grid points.")
    parser.add_argument("--q-points", type=int, default=4000, help="Number of form-factor grid points.")
    parser.add_argument("--q-max", type=float, default=16.0, help="Maximum q value for inversion.")
    parser.add_argument("--json", action="store_true", help="Emit JSON only.")
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    result = harmonic_oscillator_demo(
        alpha=args.alpha,
        r_points=args.r_points,
        q_points=args.q_points,
        q_max=args.q_max,
    )
    if args.json:
        print(json.dumps(result, indent=2, sort_keys=True))
    else:
        print("GBM inverse-potential harmonic-oscillator smoke demo")
        for key, value in result.items():
            print(f"{key}: {value}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
