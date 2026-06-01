# Publish Gate

Last updated: 2026-06-01

Before any GitHub remote is created or any branch is pushed:

1. Review `docs/scope_contract.md`.
2. Review `docs/allowlist_manifest.md` against the actual staged files.
3. Run `python scripts/sanitize_scan.py .`.
4. Run `python -m unittest discover -s tests`.
5. Review `README.md`, `LICENSE`, `CITATION.cff`, and `SECURITY.md`.
6. Confirm no private source paths, unpublished manuscript references, raw run
   artifacts, or machine-specific operations are present.
7. Confirm the GitHub target URL, visibility, and license are approved by the
   user.
8. Create the GitHub repository as private first unless the user explicitly
   approves immediate public release.
9. Push only after the local checks pass.

Post-public profile, website, and resume updates are separate tasks and should
wait until the public URL is live and source-backed.
