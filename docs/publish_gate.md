# Publish Gate

Last updated: 2026-06-01

Private staging is already configured and pushed. Before any public visibility
change:

1. Review `docs/scope_contract.md`.
2. Review `docs/allowlist_manifest.md` against the actual staged files.
3. Run `python scripts/sanitize_scan.py .`.
4. Run `python -m unittest discover -s tests`.
5. Review `README.md`, `LICENSE`, `CITATION.cff`, and `SECURITY.md`.
6. Confirm no private source paths, unpublished manuscript references, raw run
   artifacts, or machine-specific operations are present.
7. Confirm `.github/dependabot.yml` is present and workflow actions are pinned
   to full commit SHAs with same-line version comments.
8. Confirm the private GitHub Security settings have been manually reviewed,
   including secret scanning and push protection availability.
9. Confirm the GitHub target URL, visibility, and license are approved by the
   user.
10. Keep the repository private unless the user explicitly approves public
    release.
11. Push only after the local checks pass.

Post-public profile, website, and resume updates are separate tasks and should
wait until the public URL is live and source-backed.
