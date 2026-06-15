# v0.2.0 Release Notes

Planned release date: 2026-06-15

## Added

- MkDocs documentation site configuration and GitHub Pages deployment workflow.
- Coverage measurement in CI with a committed coverage badge verified by CI.
- Public API, installation, examples, coverage, and figure-provenance docs.
- Moment-series and alpha-sweep examples built entirely from public code.

## Scope

This release is a flagship-polish release for the existing public derivative
artifact. It does not broaden the science scope or import non-public source
material.

## Release Gate

Before release:

- sanitizer scan must pass;
- unit tests must pass under coverage;
- documentation must build with `mkdocs build --strict`;
- CodeQL and CI must pass on GitHub;
- the GitHub release should trigger a Zenodo version archive.
