#!/usr/bin/env python3
"""Write the public harmonic-oscillator demo density figure as SVG."""

from __future__ import annotations

import argparse
from pathlib import Path
import sys

import numpy as np

from gbm_inverse_potential import (
    ho_form_factor,
    ho_reduced_density,
    inverse_reduced_density,
)


def _polyline_points(x_values: np.ndarray, y_values: np.ndarray, scale) -> str:
    return " ".join(f"{x:.2f},{y:.2f}" for x, y in scale(x_values, y_values))


def _build_svg() -> str:
    r_grid = np.linspace(0.02, 4.0, 400)
    q_grid = np.linspace(0.0, 16.0, 4000)
    analytic = ho_reduced_density(r_grid)
    reconstructed = inverse_reduced_density(r_grid, q_grid, ho_form_factor(q_grid))

    width = 760
    height = 420
    left = 72
    right = 30
    top = 32
    bottom = 58
    plot_width = width - left - right
    plot_height = height - top - bottom
    y_max = float(max(np.max(analytic), np.max(reconstructed)) * 1.08)

    def scale(x_values: np.ndarray, y_values: np.ndarray):
        x_scaled = left + (x_values - r_grid[0]) / (r_grid[-1] - r_grid[0])
        x_scaled = x_scaled * plot_width
        y_scaled = top + plot_height - y_values / y_max * plot_height
        return zip(x_scaled, y_scaled)

    analytic_points = _polyline_points(r_grid, analytic, scale)
    recon_points = _polyline_points(r_grid, reconstructed, scale)
    x_axis_y = top + plot_height

    y_label = top + plot_height / 2
    lines = [
        (
            f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" '
            f'height="{height}" viewBox="0 0 {width} {height}" '
            'role="img" aria-labelledby="title desc">'
        ),
        '  <title id="title">Public harmonic-oscillator density smoke demo</title>',
        (
            '  <desc id="desc">Analytic and reconstructed reduced radial '
            'density for the public oscillator smoke case.</desc>'
        ),
        '  <rect width="100%" height="100%" fill="#ffffff"/>',
        (
            f'  <text x="{left}" y="22" font-family="Arial, sans-serif" '
            'font-size="16" font-weight="700" fill="#1f2933">'
            'Public reduced-density smoke demo</text>'
        ),
        (
            f'  <line x1="{left}" y1="{top}" x2="{left}" y2="{x_axis_y}" '
            'stroke="#334e68" stroke-width="1.2"/>'
        ),
        (
            f'  <line x1="{left}" y1="{x_axis_y}" x2="{width - right}" '
            f'y2="{x_axis_y}" stroke="#334e68" stroke-width="1.2"/>'
        ),
        (
            f'  <text x="{width / 2 - 20:.1f}" y="{height - 18}" '
            'font-family="Arial, sans-serif" font-size="13" '
            'fill="#334e68">r</text>'
        ),
        (
            f'  <text x="16" y="{y_label:.1f}" '
            'font-family="Arial, sans-serif" font-size="13" '
            f'fill="#334e68" transform="rotate(-90 16 {y_label:.1f})">'
            'u(r)^2</text>'
        ),
        (
            f'  <polyline points="{analytic_points}" fill="none" '
            'stroke="#0b7285" stroke-width="2.4"/>'
        ),
        (
            f'  <polyline points="{recon_points}" fill="none" '
            'stroke="#c2410c" stroke-width="1.8" stroke-dasharray="6 4"/>'
        ),
        (
            f'  <rect x="{width - 246}" y="{top + 10}" width="210" '
            'height="58" fill="#ffffff" stroke="#bcccdc"/>'
        ),
        (
            f'  <line x1="{width - 232}" y1="{top + 30}" '
            f'x2="{width - 188}" y2="{top + 30}" '
            'stroke="#0b7285" stroke-width="2.4"/>'
        ),
        (
            f'  <text x="{width - 178}" y="{top + 34}" '
            'font-family="Arial, sans-serif" font-size="12" fill="#1f2933">'
            'Analytic reduced density</text>'
        ),
        (
            f'  <line x1="{width - 232}" y1="{top + 54}" '
            f'x2="{width - 188}" y2="{top + 54}" '
            'stroke="#c2410c" stroke-width="1.8" stroke-dasharray="6 4"/>'
        ),
        (
            f'  <text x="{width - 178}" y="{top + 58}" '
            'font-family="Arial, sans-serif" font-size="12" fill="#1f2933">'
            'Reconstructed density</text>'
        ),
        (
            f'  <text x="{left}" y="{height - 36}" '
            'font-family="Arial, sans-serif" font-size="11" fill="#52606d">'
            'alpha=1.0, r_points=400, q_points=4000, q_max=16.0</text>'
        ),
        "</svg>",
    ]
    return "\n".join(lines) + "\n"


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Write the public demo density SVG.")
    parser.add_argument("--output", type=Path, help="Optional SVG output path.")
    args = parser.parse_args(argv)

    svg = _build_svg()
    if args.output:
        args.output.write_text(svg, encoding="utf-8")
    else:
        sys.stdout.write(svg)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
