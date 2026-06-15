#!/usr/bin/env python3
"""Compare the public even-moment form-factor series with the analytic form."""

from __future__ import annotations

import argparse
import json
from typing import Sequence

import numpy as np

from gbm_inverse_potential import (
    form_factor_from_even_moments,
    ho_even_moment,
    ho_form_factor,
)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--alpha", type=float, default=1.0, help="Oscillator alpha parameter.")
    parser.add_argument("--max-power", type=int, default=18, help="Largest even moment power to include.")
    parser.add_argument("--q-max", type=float, default=2.0, help="Largest q value in the comparison grid.")
    parser.add_argument("--q-points", type=int, default=9, help="Number of q grid points.")
    parser.add_argument("--json", action="store_true", help="Emit JSON only.")
    return parser


def run_comparison(*, alpha: float, max_power: int, q_max: float, q_points: int) -> dict[str, object]:
    if max_power < 0 or max_power % 2 != 0:
        raise ValueError("max_power must be a nonnegative even integer")
    if q_points < 2:
        raise ValueError("q_points must be at least 2")

    q_grid = np.linspace(0.0, q_max, q_points)
    moments = {power: ho_even_moment(power, alpha=alpha) for power in range(0, max_power + 1, 2)}
    series = form_factor_from_even_moments(q_grid, moments)
    analytic = ho_form_factor(q_grid, alpha=alpha)
    abs_error = np.abs(series - analytic)
    return {
        "alpha": float(alpha),
        "max_power": int(max_power),
        "q_max": float(q_max),
        "q_points": int(q_points),
        "max_abs_error": float(np.max(abs_error)),
        "rms_abs_error": float(np.sqrt(np.mean(abs_error**2))),
    }


def main(argv: Sequence[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    result = run_comparison(
        alpha=args.alpha,
        max_power=args.max_power,
        q_max=args.q_max,
        q_points=args.q_points,
    )
    if args.json:
        print(json.dumps(result, indent=2, sort_keys=True))
    else:
        print("Moment-series form-factor comparison")
        for key, value in result.items():
            print(f"{key}: {value}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
