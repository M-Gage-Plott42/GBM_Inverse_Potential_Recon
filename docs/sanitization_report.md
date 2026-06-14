# Sanitization Report

Last updated: 2026-06-14

## Status

Public v0 artifact published at `GBM_Inverse_Potential_Recon`.

- Local commit: `bb2a396 Initial public derivative skeleton`
- Private-first gate commit: `1ab19cc Harden private-first publish gate`
- Node 24 workflow update: CI workflow uses `actions/setup-python@v6`.
- Actions supply-chain hardening: Dependabot config added for GitHub Actions
  and pip; workflow actions are pinned to full commit SHAs with version
  comments.
- Public remote: `git@github.com:M-Gage-Plott42/GBM_Inverse_Potential_Recon.git`.
- Public visibility: approved and published for first public v0 release on
  2026-06-01.
- Public metadata: GitHub repository description is public-facing; license is
  MIT; `CITATION.cff` records version `0.1.1` for citable-release prep.
- Post-public security settings: secret scanning, push protection, and
  Dependabot security updates are enabled with zero open secret-scanning or
  Dependabot alerts as checked on 2026-06-02.
- Post-public hardening: CodeQL workflow added with least-privilege workflow
  permissions and full-SHA pinned actions.
- Evidence-layer refresh: README badges and status notes, public smoke
  benchmark notes, reproducibility tolerances, and a command-reproducible
  public demo figure workflow were added without broadening the science scope.

## Latest Local Checks

Passed locally on 2026-06-14 after editable install:

```bash
python3 -m pip install -e .
python3 scripts/sanitize_scan.py .
python3 -m unittest discover -s tests
python3 -m gbm_inverse_potential.cli --json
python3 examples/harmonic_oscillator_demo.py
python3 scripts/reproduce_public_demo_figure.py --output /tmp/gbm_public_demo_density.svg
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
- GitHub CI: public push run `26793729957` passed for Python `3.10`, `3.11`,
  and `3.12`.
- GitHub Actions runtime: workflow uses full-SHA pins for
  `actions/checkout` v6.0.3 and `actions/setup-python` v6.2.0, both selected
  for Node 24 compatibility.
- GitHub CodeQL: workflow uses full-SHA pins for `actions/checkout` v6.0.3 and
  `github/codeql-action` v4.36.2.
- Open dependency PRs reviewed on 2026-06-14:
  `actions/checkout` v6.0.3 and `github/codeql-action` v4.36.2 both had
  passing public checks when reviewed. Their exact updates were folded into
  this evidence-layer refresh.

## Human Publish Gate

The first public v0 release gate is approved for the current manifest only.
Further private source-repo migration requires a separate allowlist,
sanitization scan, test/smoke evidence, and human review. Do not broaden this
repository by copying private source-tree material wholesale.
