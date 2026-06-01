# Sanitization Report

Last updated: 2026-06-01

## Status

Draft local skeleton created at `GBM_Inverse_Potential_Recon`.

- Local commit: `bb2a396 Initial public derivative skeleton`
- Private-first gate commit: `1ab19cc Harden private-first publish gate`
- Node 24 workflow update: CI workflow uses `actions/setup-python@v6`.
- Remote status: private GitHub staging remote configured at
  `git@github.com:M-Gage-Plott42/GBM_Inverse_Potential_Recon.git`.
- Public visibility: not public.

## Latest Local Checks

Passed locally on 2026-06-01:

```bash
PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=src python3 -m unittest discover -s tests
python3 scripts/sanitize_scan.py .
PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=src python3 -m gbm_inverse_potential.cli --json
PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=src python3 examples/harmonic_oscillator_demo.py
```

Observed demo metrics:

- `density_l2_rel`: `2.73858947190776e-16`
- `density_max_rel_window`: `9.375636558551197e-12`
- `density_norm_trapz`: `0.9999927119194942`
- `potential_l2_rel_window`: `9.301565868161144e-05`
- `potential_max_abs_window`: `0.0004660347639350304`

## Current Gate Expectations

- high-confidence credential patterns: zero;
- private source repo names and local paths: zero;
- blocked directories: absent;
- files larger than 1 MB: absent;
- tests: pass on the public v0 smoke path.
- GitHub CI: passed on the private staging repo for the first private push.
- GitHub Actions runtime: workflow uses `actions/checkout@v6` and
  `actions/setup-python@v6`, both selected for Node 24 compatibility.

## Human Publish Gate

Do not make this repository public until the staged files, scan output, license,
citation metadata, and README are reviewed manually. GitHub remote creation
has started private as intended.
