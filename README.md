# GBM Inverse Potential Reconstruction

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
- Public-release guard docs, sanitization checks, citation metadata, and CI.

## What Is Excluded

This first pass intentionally excludes private source-repo history, private
handoff packets, raw run outputs, workstation or cluster configuration, large
media files, manuscript sync notes, archived operational docs, and private local
paths.

## Quick Start

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -e .
python -m unittest discover -s tests
python examples/harmonic_oscillator_demo.py
```

Expected demo behavior: the reconstructed reduced density and reconstructed
potential should have small relative errors on the documented smoke grid.

## CLI

```bash
python -m gbm_inverse_potential.cli --json
```

## Repository Status

This is the first public v0 artifact from the sanitized GBM derivative path.
The scope is intentionally narrow: harmonic-oscillator Fourier/form-factor
density and potential reconstruction plus release-safety checks. The private
research workspace and broader GBM stack remain excluded.

Future additions should pass the same allowlist, sanitization, test, and human
review gates before they are folded into this public repository.

## Maintainer / Help

Maintained by Matthew Gage Plott. Use GitHub Issues for ordinary questions.
For suspected private-data or security exposure, do not open a public issue;
follow `SECURITY.md`.

## License

MIT.

## Citation

See `CITATION.cff`.
