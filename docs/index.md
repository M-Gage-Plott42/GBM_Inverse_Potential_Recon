# GBM Inverse Potential Reconstruction

`GBM_Inverse_Potential_Recon` is a small public research-code artifact for
inverse radial density and potential reconstruction from sparse
spectral-moment information.

The public package currently focuses on a deterministic harmonic-oscillator
smoke case. It provides:

- an installable Python package under `src/gbm_inverse_potential`;
- Fourier/form-factor reconstruction helpers;
- a console script and runnable examples;
- a bounded deterministic Python calculation-service contract;
- a bounded local FastAPI/OpenAPI adapter;
- a non-root local Docker image with hardened lifecycle checks;
- unit tests, sanitizer checks, CodeQL, and coverage measurement;
- a public demo figure workflow;
- citation metadata and Zenodo archiving.

The scope is intentionally narrow. The public repository does not publish the
full research workspace, source history, local runtime data, or unpublished
paper context.

Start with [Installation](installation.md), review the Python
[Service Contract](service_contract.md) and the
[Local HTTP And Container Contract](http_container_contract.md), then run the
examples in [Examples](examples.md).

The HTTP adapter and image are local evidence only. This repository does not
claim a cloud deployment, public endpoint, published image, monitored
operation, or new release for that slice.
