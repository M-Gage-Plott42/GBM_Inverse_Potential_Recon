# Sanitization Report

Last updated: 2026-05-30

## Status

Draft local skeleton created at `GBM_Inverse_Potential_Recon`. No commits or
pushes have been made.

## Latest Local Checks

Passed locally on 2026-05-30:

```bash
PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=src python3 -m unittest discover -s tests
python3 scripts/sanitize_scan.py .
PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=src python3 -m gbm_inverse_potential.cli --json
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

## Human Publish Gate

Do not make this repository public until the staged files, scan output, license,
citation metadata, and README are reviewed manually.
