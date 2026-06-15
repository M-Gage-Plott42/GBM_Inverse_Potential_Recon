# Allowlist Manifest

Last updated: 2026-06-14

This manifest records the first-pass clean-room classification for the public
v0 derivative. It is intentionally small and should be reviewed before any
future content expansion.

## Include

| Path | Reason |
| --- | --- |
| `src/gbm_inverse_potential/` | Public v0 implementation. |
| `examples/` | Deterministic smoke demo. |
| `tests/` | Minimal correctness checks. |
| `scripts/sanitize_scan.py` | Public-release blocker scan. |
| `scripts/reproduce_public_demo_figure.py` | Public demo SVG workflow. |
| `scripts/write_coverage_badge.py` | Public coverage badge generator. |
| `.github/dependabot.yml` | Dependency and GitHub Actions update monitoring. |
| `.github/workflows/ci.yml` | Public CI test, coverage, and sanitation gate. |
| `.github/workflows/codeql.yml` | Public CodeQL code-scanning workflow. |
| `.github/workflows/docs.yml` | Public docs build and GitHub Pages deployment workflow. |
| `.coveragerc` | Coverage measurement configuration. |
| `mkdocs.yml` | Documentation site configuration. |
| `README.md` | Public landing page. |
| `LICENSE` | MIT license. |
| `CITATION.cff` | Public v0 citation metadata. |
| `SECURITY.md` | Vulnerability and private-data reporting policy. |
| `docs/` | Public-safe scope, reproducibility, and release-gate docs. |
| `docs/assets/coverage.svg` | Coverage badge generated from public tests. |

## Sanitize/Rewritten

| Source concept | Public treatment |
| --- | --- |
| Fourier/form-factor route | Rewritten as a compact public implementation. |
| Runtime dependencies | Reduced to `numpy>=1.26`. |
| Citation metadata | Retitled for the derivative repo. |
| README material | Rewritten for public users. |
| GitHub Actions references | Pinned to full commit SHAs with version comments. |
| CodeQL workflow | Added as a public-repo hardening signal with least-privilege permissions. |
| Documentation site | Added as a MkDocs site over public-safe Markdown docs. |
| Coverage badge | Generated from public coverage JSON and verified by CI. |
| Public benchmark notes | Limited to harmonic-oscillator smoke validation evidence. |
| Figure workflow | Limited to a generated public demo figure, not private manuscript figures. |

## Defer

| Source area | Reason |
| --- | --- |
| Full P6/HYI research stack | Too large for public v0; requires separate audit. |
| Large engine and plotter modules | Not needed for v0; require separate audit. |
| Reference profile libraries | Need separate size/license/provenance review. |
| Advanced Padé and ILT comparison surfaces | Defer until public v0 is stable. |

## Block

| Blocked pattern | Reason |
| --- | --- |
| `handoff/` | Private cross-repo packet material. |
| `runs/`, `snapshots/`, `spectrum_data/` | Local/private runtime data. |
| `docs/archive/` | Historical private operations and context. |
| private ops docs | Machine, SSH, workstation, or local process details. |
| raw run manifests and logs | Private local provenance and path leakage risk. |
| large media or rendered packet files | Not needed for public v0. |
| dissertation or manuscript sync material | Publication/private-status risk. |

## Current Extraction Choice

No private source files are copied verbatim in public v0. The first runnable
core is a compact public implementation of the Fourier/form-factor path for a
harmonic-oscillator benchmark.
