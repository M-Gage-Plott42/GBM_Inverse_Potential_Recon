#!/usr/bin/env python3
"""Write a small static SVG coverage badge from coverage.py JSON output."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Sequence


def _coverage_color(percent: float) -> str:
    if percent >= 90.0:
        return "#4c1"
    if percent >= 80.0:
        return "#97ca00"
    if percent >= 70.0:
        return "#dfb317"
    if percent >= 60.0:
        return "#fe7d37"
    return "#e05d44"


def _badge_svg(percent: float) -> str:
    value = f"{percent:.0f}%"
    color = _coverage_color(percent)
    return f"""<svg xmlns="http://www.w3.org/2000/svg" width="104" height="20" role="img" aria-label="coverage: {value}">
  <title>coverage: {value}</title>
  <linearGradient id="s" x2="0" y2="100%">
    <stop offset="0" stop-color="#bbb" stop-opacity=".1"/>
    <stop offset="1" stop-opacity=".1"/>
  </linearGradient>
  <clipPath id="r">
    <rect width="104" height="20" rx="3" fill="#fff"/>
  </clipPath>
  <g clip-path="url(#r)">
    <rect width="63" height="20" fill="#555"/>
    <rect x="63" width="41" height="20" fill="{color}"/>
    <rect width="104" height="20" fill="url(#s)"/>
  </g>
  <g fill="#fff" text-anchor="middle" font-family="Verdana,Geneva,DejaVu Sans,sans-serif" font-size="11">
    <text x="31.5" y="15" fill="#010101" fill-opacity=".3">coverage</text>
    <text x="31.5" y="14">coverage</text>
    <text x="82.5" y="15" fill="#010101" fill-opacity=".3">{value}</text>
    <text x="82.5" y="14">{value}</text>
  </g>
</svg>
"""


def coverage_percent(path: Path) -> float:
    payload = json.loads(path.read_text(encoding="utf-8"))
    totals = payload["totals"]
    return float(totals.get("percent_covered_display", totals["percent_covered"]))


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("coverage_json", type=Path)
    parser.add_argument("output", type=Path)
    args = parser.parse_args(argv)

    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(_badge_svg(coverage_percent(args.coverage_json)), encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
