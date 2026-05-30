# Reproducibility Notes

Last updated: 2026-05-30

## Environment

Python `>=3.10` with `numpy>=1.26`.

## Smoke Commands

```bash
python -m pip install -e .
python -m unittest discover -s tests
python scripts/sanitize_scan.py .
python -m gbm_inverse_potential.cli --json
```

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
