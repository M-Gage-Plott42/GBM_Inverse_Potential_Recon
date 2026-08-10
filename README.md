# GBM Inverse Potential Reconstruction

[![CI](https://github.com/M-Gage-Plott42/GBM_Inverse_Potential_Recon/actions/workflows/ci.yml/badge.svg?branch=main)](https://github.com/M-Gage-Plott42/GBM_Inverse_Potential_Recon/actions/workflows/ci.yml)
[![CodeQL](https://github.com/M-Gage-Plott42/GBM_Inverse_Potential_Recon/actions/workflows/codeql.yml/badge.svg?branch=main)](https://github.com/M-Gage-Plott42/GBM_Inverse_Potential_Recon/actions/workflows/codeql.yml)
[![Docs](https://github.com/M-Gage-Plott42/GBM_Inverse_Potential_Recon/actions/workflows/docs.yml/badge.svg?branch=main)](https://github.com/M-Gage-Plott42/GBM_Inverse_Potential_Recon/actions/workflows/docs.yml)
[![Coverage](docs/assets/coverage.svg)](docs/coverage.md)
[![Release](https://img.shields.io/github/v/release/M-Gage-Plott42/GBM_Inverse_Potential_Recon)](https://github.com/M-Gage-Plott42/GBM_Inverse_Potential_Recon/releases)
[![Python](https://img.shields.io/badge/python-3.10%2B-blue)](pyproject.toml)
[![License: MIT](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)
[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.20693817.svg)](https://doi.org/10.5281/zenodo.20693817)

A small public research-code artifact for inverse radial density and potential
reconstruction from sparse spectral-moment information.

This repository is the first public slice of a broader Generalized Borel Method
(GBM) research line. It is not a publication of the private research workspace
and does not contain the full private GBM stack. Public v0 starts with a narrow,
deterministic Fourier/form-factor route for the three-dimensional harmonic
oscillator ground state, so reviewers can inspect and run a clean proof artifact
before any larger research components are considered for release.

## What Is Included

- A minimal Python package under `src/gbm_inverse_potential/`.
- A Fourier/form-factor density reconstruction path using even radial moments.
- A finite-difference potential reconstruction smoke path.
- A deterministic harmonic-oscillator demo and unit tests.
- A bounded, deterministic Python application service over the same smoke path.
- A local FastAPI adapter with generated OpenAPI and operational endpoints.
- A non-root Docker image and automated loopback-only lifecycle smoke test.
- Public-release guard docs, sanitization checks, citation metadata, and CI.

## Evidence Status

Current public scope:

- installable base Python package with `numpy` as its only runtime dependency;
- deterministic CLI and example script for the oscillator smoke case;
- typed request/result objects, fixed computational work, and a versioned
  JSON-compatible local service contract;
- an optional FastAPI/Uvicorn HTTP layer and a local evidence container;
- expanded public examples for moment-series and alpha-sweep smoke checks;
- unit tests for moments, form-factor reconstruction, inverse density recovery,
  potential reconstruction, and sanitizer coverage;
- coverage measured in CI with a checked-in coverage badge;
- MkDocs documentation site configuration and GitHub Pages deployment workflow;
- public reproducibility notes in `docs/reproducibility.md`;
- smoke benchmark metrics in `docs/public_smoke_benchmark.md`;
- command-reproducible public demo SVG workflow in
  `scripts/reproduce_public_demo_figure.py`;
- MIT license, `CITATION.cff`, pinned GitHub Actions, Dependabot, and CodeQL.

## What Is Excluded

This first pass intentionally excludes private source-repo history, private
handoff packets, raw run outputs, workstation or cluster configuration, large
media files, manuscript sync notes, archived operational docs, private local
paths, and claims about unpublished/private research beyond the public v0
artifact. The local HTTP/container evidence does not establish a cloud
deployment, public endpoint, published image, monitored operation, or new
software release.

## Quick Start

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -r requirements-dev.txt
python -m pip install -e .
python -m unittest discover -s tests
python examples/harmonic_oscillator_demo.py
python examples/moment_series_comparison.py --json
python examples/alpha_sweep_smoke.py --json
python -m gbm_inverse_potential.cli --json
```

## Local Calculation Service

```python
from gbm_inverse_potential import CalculationRequest, run_calculation

result = run_calculation(CalculationRequest(alpha=1.0))
print(result.to_dict()["metrics"])
```

The service accepts `alpha` from `0.75` through `1.25` inclusive and always
uses the documented `400 x 4000` standard grid. See
`docs/service_contract.md` for the versioned result schema, accuracy gate, and
limitations. The Python core remains framework-neutral; the optional HTTP
adapter delegates to it without exposing grid controls, files, uploads, or
stored input.

## Local HTTP API

```bash
python -m pip install -e '.[service]'
uvicorn gbm_inverse_potential.http_api:app \
  --host 127.0.0.1 --port 8000 --workers 1 \
  --no-access-log --no-proxy-headers --no-server-header --no-date-header
```

The reviewed wire surface is `POST /v1/reconstruct`, `GET /health/live`,
`GET /health/ready`, `GET /version`, `GET /openapi.json`, and the local
Swagger UI at `GET /docs`. Keep it on loopback. See
`docs/http_container_contract.md` for request limits and failure behavior.

## Local Docker Evidence

With Docker running:

```bash
python scripts/smoke_container.py --build --revision local-review
```

The smoke workflow builds locally, starts the image with a read-only root
filesystem, numeric non-root user, dropped capabilities, no-new-privileges,
CPU/memory/PID limits, and a loopback-only host port. It checks the API,
container configuration, clean stop/start behavior, deterministic restart
output, and cleanup. It does not push the image or contact a cloud provider.

Expected demo behavior: the reconstructed reduced density and reconstructed
potential should have small relative errors on the documented smoke grid.

## CLI

```bash
python -m gbm_inverse_potential.cli --json
```

## Public Demo Figure

The repository does not claim to reproduce private manuscript figures. It
includes a command-reproducible public demo figure for the same oscillator smoke
case:

```bash
python scripts/reproduce_public_demo_figure.py > /tmp/gbm_public_demo_density.svg
```

The SVG overlays the analytic reduced density with the reconstructed reduced
density from the public Fourier/form-factor path.

## Documentation Site

The MkDocs source lives in `docs/` and is configured by `mkdocs.yml`. The
intended GitHub Pages URL is:

https://m-gage-plott42.github.io/GBM_Inverse_Potential_Recon/

The docs workflow builds the site on pull requests and deploys from `main` when
GitHub Pages is configured to use GitHub Actions.

## Repository Status

This is the first public v0 artifact from the sanitized GBM derivative path.
The scope is intentionally narrow: harmonic-oscillator Fourier/form-factor
density and potential reconstruction plus release-safety checks. The private
research workspace and broader GBM stack remain excluded.

For the exact public v0 scope and limitations, see `docs/scope_contract.md`.

Future additions should pass the same allowlist, sanitization, test, and human
review gates before they are folded into this public repository.

## Reproducibility And Benchmark Notes

- Reproducibility notes: `docs/reproducibility.md`.
- Deterministic local service contract: `docs/service_contract.md`.
- Local HTTP and container contract: `docs/http_container_contract.md`.
- Public smoke benchmark: `docs/public_smoke_benchmark.md`.
- Release and safety gate: `docs/publish_gate.md`.
- File manifest enforced by the sanitizer: `docs/release_file_manifest.txt`.

## Maintainer / Help

Maintained by Matthew Gage Plott. Use GitHub Issues for ordinary questions.
For suspected private-data or security exposure, do not open a public issue;
follow `SECURITY.md`.

## License

MIT.

## Citation

Use `CITATION.cff` for the current software citation metadata.

- Version DOI for `v0.2.0`: https://doi.org/10.5281/zenodo.20709098
- Version DOI for `v0.1.1`: https://doi.org/10.5281/zenodo.20693818
- Concept DOI for all versions: https://doi.org/10.5281/zenodo.20693817
