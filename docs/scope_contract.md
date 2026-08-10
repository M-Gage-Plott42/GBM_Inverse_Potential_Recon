# Scope Contract

Last updated: 2026-08-10

## Derivative Name

`GBM_Inverse_Potential_Recon`

Python package name: `gbm-inverse-potential-recon`

## License

MIT.

## Audience

- Research software reviewers who need a small, runnable proof artifact.
- Computational science and scientific Python readers.
- Hiring or portfolio reviewers who need to inspect public-safe code without
  private research operations or unpublished manuscript context.

## Included Science Slice

Public v0 is deliberately narrow:

- spherical Fourier/form-factor reconstruction from even radial moments;
- deterministic harmonic-oscillator ground-state reference;
- reduced radial density reconstruction;
- potential reconstruction by finite differences in reduced units;
- unit tests and a command-line smoke demo;
- a bounded framework-neutral Python application service over that same demo;
- a bounded local FastAPI adapter with generated OpenAPI documentation;
- a non-root local Docker evidence image and lifecycle smoke test;
- public smoke benchmark notes for the oscillator demo;
- command-reproducible public demo SVG generation.

## Blocked Content Classes

- private source-repo history;
- private handoff packets;
- raw run outputs and large generated artifacts;
- local machine paths, usernames, hostnames, and workstation configuration;
- unpublished manuscript, private review, private correspondence, or deadline
  material;
- browser/session exports, credentials, tokens, cookies, or environment files;
- private operational archives and dissertation sync notes.

## Non-Goals For Public v0

- no full research history;
- no large engine migration;
- no private run-registry reproduction;
- no publication-status or manuscript-status claims;
- no claim that private manuscript figures are reproduced;
- no additional private-source migration without a separate allowlist,
  sanitization pass, test or smoke evidence, and human review.
- no cloud resource, deployment, registry/image publication, monitored
  operation, persistence, upload handling, authentication claim, TLS claim, or
  public endpoint;
- no internet exposure of the local HTTP adapter or Swagger UI under this gate;
- no reproducible-build claim until transitive dependencies and the base image
  are locked by the later evidence gate.
