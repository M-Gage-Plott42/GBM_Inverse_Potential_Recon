# Publish Gate

Last updated: 2026-06-01

The first public v0 release gate was approved for the current release manifest
on 2026-06-01 after local checks, GitHub CI, dependency-monitoring setup,
post-public security-settings review, and human review.

Post-public hardening on 2026-06-02 added a CodeQL workflow to the approved
manifest. This does not broaden the science scope or import additional private
source material.

This approval covers only the files listed in
`docs/release_file_manifest.txt`. For any follow-on content expansion:

1. Review `docs/scope_contract.md`.
2. Review `docs/allowlist_manifest.md` against the actual staged files and the
   proposed new file set.
3. Run `python scripts/sanitize_scan.py .`.
4. Run `python -m unittest discover -s tests`.
5. Review `README.md`, `LICENSE`, `CITATION.cff`, and `SECURITY.md`.
6. Confirm no private source paths, unpublished manuscript references, raw run
   artifacts, or machine-specific operations are present.
7. Confirm `.github/dependabot.yml` remains present and workflow actions remain
   pinned to full commit SHAs with same-line version comments.
8. Confirm GitHub Security settings have been reviewed, including secret
   scanning, push protection, Dependabot security updates, and code scanning.
9. Confirm the GitHub target URL, visibility, license, and scope are approved
   by the user.
10. Push only after the local checks pass.

Post-public profile, website, and resume updates are separate source-backed
tasks.

Do not fold in additional private source-repo material until each proposed file
or concept has a fresh allowlist entry, sanitization result, tests or smoke
evidence, and human approval.
