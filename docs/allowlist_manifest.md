# Allowlist Manifest

Last updated: 2026-05-30

This manifest records the first-pass clean-room classification for the public
v0 derivative. It is intentionally small and should be reviewed before any
public push.

## Include

| Path | Reason |
| --- | --- |
| `src/gbm_inverse_potential/` | Public v0 implementation. |
| `examples/` | Deterministic smoke demo. |
| `tests/` | Minimal correctness checks. |
| `scripts/sanitize_scan.py` | Public-release blocker scan. |
| `.github/dependabot.yml` | Dependency and GitHub Actions update monitoring. |
| `.github/workflows/ci.yml` | Public CI test and sanitation gate. |
| `README.md` | Public landing page. |
| `LICENSE` | Draft MIT license for review. |
| `CITATION.cff` | Draft citation metadata. |
| `SECURITY.md` | Vulnerability and private-data reporting policy. |
| `docs/` | Public-safe scope, reproducibility, and release-gate docs. |

## Sanitize/Rewritten

| Source concept | Public treatment |
| --- | --- |
| Fourier/form-factor route | Rewritten as a compact public implementation. |
| Runtime dependencies | Reduced to `numpy>=1.26`. |
| Citation metadata | Retitled for the derivative repo. |
| README material | Rewritten for public users. |
| GitHub Actions references | Pinned to full commit SHAs with version comments. |

## Defer

| Source area | Reason |
| --- | --- |
| Full P6/HYI research stack | Too large for public v0; requires separate audit. |
| Large engine, plotter, and stats modules | Monolithic, private-context-heavy, and not needed for v0. |
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
