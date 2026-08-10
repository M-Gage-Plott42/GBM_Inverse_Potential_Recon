# Sanitization Report

Last updated: 2026-08-10

## Status

Public v0 artifact published at `GBM_Inverse_Potential_Recon`.

- Local commit: `bb2a396 Initial public derivative skeleton`
- Private-first gate commit: `1ab19cc Harden private-first publish gate`
- Node 24 workflow update: CI and docs workflows use `actions/setup-python@v7.0.0`.
- Actions supply-chain hardening: Dependabot config added for GitHub Actions
  and pip, with CodeQL action updates grouped so `init` and `analyze` remain in
  sync; workflow actions are pinned to full commit SHAs with version comments.
- Public remote: `git@github.com:M-Gage-Plott42/GBM_Inverse_Potential_Recon.git`.
- Public visibility: approved and published for first public v0 release on
  2026-06-01.
- Public metadata: GitHub repository description is public-facing; license is
  MIT; `CITATION.cff` records released version `0.2.0` and its version DOI.
- Post-public security settings: secret scanning, push protection, and
  Dependabot security updates are enabled with zero open secret-scanning or
  Dependabot alerts as checked on 2026-06-02.
- Post-public hardening: CodeQL workflow added with least-privilege workflow
  permissions and full-SHA pinned actions.
- Evidence-layer refresh: README badges and status notes, public smoke
  benchmark notes, reproducibility tolerances, and a command-reproducible
  public demo figure workflow were added without broadening the science scope.
- Gate 1 application-service addition: a bounded typed interface reuses the
  existing public oscillator smoke path with fixed work and tests. PR #29 was
  merged to `main` as `cbde2e3f3ed66f88af885b64033cff29fc92fca6`. It imports
  no private source material.
- Local HTTP/container addition: an optional one-field FastAPI adapter,
  generated OpenAPI, operational endpoints, deny-by-default build context,
  two-stage numeric-non-root image, hardened loopback runtime, and automated
  stop/start smoke. It adds no private source material and does not publish an
  image, create a cloud resource, expose a public endpoint, or claim a release.

## Latest Local Checks

Passed locally on 2026-08-10 after development/service editable install:

```bash
python3 -m pip install -r requirements-dev.txt
python3 -m pip install -e .
python3 scripts/sanitize_scan.py .
python3 -m unittest discover -s tests
python3 -m gbm_inverse_potential.cli --json
python3 examples/harmonic_oscillator_demo.py
python3 scripts/reproduce_public_demo_figure.py --output /tmp/gbm_public_demo_density.svg
coverage run -m unittest discover -s tests
coverage report --fail-under=80
mkdocs build --strict
python3 scripts/smoke_container.py --build --revision local-review
```

The container smoke verified numeric user/group `10001:10001`, read-only root,
zero effective capabilities, no-new-privileges, 256 MiB/one CPU/64 PID limits,
no mounts, loopback-only port publication, health, exact API paths, validation,
clean bounded stop/start, byte-identical calculation output after restart, and
unique-container cleanup. The image remained local.

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
- manifest files: 55;
- tests: 43 passed on the scientific, HTTP/OpenAPI, concurrency, and sanitizer
  paths;
- package branch coverage: 90%, above the enforced 80% floor;
- Docker lifecycle smoke: pass locally; branch CI must repeat it on the Python
  3.12 job before any integration decision;
- GitHub Actions runtime: workflows use full-SHA pins for
  `actions/checkout` v7.0.1 and `actions/setup-python` v7.0.0, both selected
  for Node 24 compatibility.
- GitHub CodeQL: workflow uses full-SHA pins for `actions/checkout` v7.0.1 and
  `github/codeql-action` v4.37.3.

## Human Publish Gate

The first public v0 release gate approved the then-current historical release
manifest. The expanded 55-file source manifest is authorized for a reviewed
branch push only; it is not a new-release approval. Further private source-repo
migration requires a separate allowlist, sanitization scan, test/smoke
evidence, and human review. Do not broaden this repository by copying private
source-tree material wholesale. Main integration, a new release, a registry
push, cloud deployment, public exposure, and portfolio/resume wording remain
separate gates.
