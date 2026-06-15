#!/usr/bin/env python3
"""Run the public harmonic-oscillator smoke path across alpha values."""

from __future__ import annotations

import argparse
import json
from typing import Sequence

from gbm_inverse_potential import harmonic_oscillator_demo


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--alphas", type=float, nargs="+", default=[0.75, 1.0, 1.25])
    parser.add_argument("--r-points", type=int, default=300)
    parser.add_argument("--q-points", type=int, default=3000)
    parser.add_argument("--q-max", type=float, default=18.0)
    parser.add_argument("--json", action="store_true", help="Emit JSON only.")
    return parser


def run_sweep(*, alphas: list[float], r_points: int, q_points: int, q_max: float) -> list[dict[str, object]]:
    return [
        harmonic_oscillator_demo(
            alpha=alpha,
            r_points=r_points,
            q_points=q_points,
            q_max=q_max,
        )
        for alpha in alphas
    ]


def main(argv: Sequence[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    results = run_sweep(
        alphas=args.alphas,
        r_points=args.r_points,
        q_points=args.q_points,
        q_max=args.q_max,
    )
    if args.json:
        print(json.dumps(results, indent=2, sort_keys=True))
    else:
        print("alpha density_l2_rel potential_l2_rel_window")
        for row in results:
            print(f"{row['alpha']} {row['density_l2_rel']:.3e} {row['potential_l2_rel_window']:.3e}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
