# Reproducibility Notes

Last updated: 2026-06-14

## Environment

Python `>=3.10` with `numpy>=1.26`.

## Smoke Commands

```bash
python -m pip install -e .
python -m unittest discover -s tests
python scripts/sanitize_scan.py .
python -m gbm_inverse_potential.cli --json
python examples/harmonic_oscillator_demo.py
python scripts/reproduce_public_demo_figure.py --output /tmp/gbm_public_demo_density.svg
```

The package import path is provided by the editable install. A source-tree-only
run should set `PYTHONPATH=src` before calling the CLI or example directly.

## Deterministic Reference

The default smoke test uses the analytic three-dimensional oscillator density

```text
rho_3d(r) = (alpha/pi)^(3/2) exp(-alpha r^2)
```

with reduced density `u(r)^2 = 4 pi r^2 rho_3d(r)` and form factor
`F(q) = exp(-q^2/(4 alpha))`.

The potential reconstruction uses reduced units where `hbar^2/(2m)=1`, so the
oscillator potential is `V(r)=alpha^2 r^2` and the ground-state energy is
`E=3 alpha`.

## Expected Smoke Tolerances

The default grid is `r_points=400`, `q_points=4000`, and `q_max=16.0` with
`alpha=1.0`. On this grid, the public smoke path should satisfy:

- density relative L2 error below `1.0e-8`;
- density max relative error on the tested window below `1.0e-8`;
- density trapezoid norm within `2.0e-5` of `1.0`;
- potential relative L2 error on the tested window below `1.0e-3`;
- potential max absolute error on the tested window below `1.0e-3`.

The current observed values are tracked in `docs/public_smoke_benchmark.md`.
The SVG workflow in `scripts/reproduce_public_demo_figure.py` is a public demo
figure generator, not a claim that private manuscript figures are reproduced.
