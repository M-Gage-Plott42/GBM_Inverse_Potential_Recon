# Publish Gate

Last updated: 2026-08-10

The first public v0 release gate was approved for the then-current release manifest
on 2026-06-01 after local checks, GitHub CI, dependency-monitoring setup,
post-public security-settings review, and human review.

Post-public hardening on 2026-06-02 added a CodeQL workflow to the approved
manifest. This does not broaden the science scope or import additional private
source material.

On 2026-08-10, the local FastAPI/Docker evidence expansion was authorized for
source, test, documentation, commit, and branch push. Its fresh allowlist adds
only the bounded adapter, optional direct dependencies, HTTP tests, a
deny-by-default Docker context, a two-stage non-root image, and local lifecycle
automation. This authority does not cover a new release, container-registry
push, cloud resource, deployment, public endpoint, monitoring claim, resume
claim, or integration of the evidence branch without a separate review.

That historical release approval did not automatically extend to later source
expansions. The current source manifest is the file-set guard for this branch;
for any follow-on content expansion:

1. Review `docs/scope_contract.md`.
2. Review `docs/allowlist_manifest.md` against the actual staged files and the
   proposed new file set.
3. Run `python scripts/sanitize_scan.py .`.
4. Run `python -m unittest discover -s tests`.
5. Run `python -m gbm_inverse_potential.cli --json`.
6. Run `python examples/harmonic_oscillator_demo.py`.
7. Run
   `python scripts/reproduce_public_demo_figure.py --output /tmp/gbm_public_demo_density.svg`.
8. Run `mkdocs build --strict`.
9. For HTTP/container changes, run
   `python scripts/smoke_container.py --build --revision <reviewed-source-id>`.
10. Confirm the container is numeric non-root, read-only, capability-free,
   no-new-privileges, resource-limited, and bound only to `127.0.0.1`; confirm
   the build context is deny-by-default and no image is pushed.
11. Review `README.md`, `LICENSE`, `CITATION.cff`, and `SECURITY.md`.
12. Confirm no private source paths, unpublished manuscript references, raw run
   artifacts, or machine-specific operations are present.
13. Confirm `.github/dependabot.yml` remains present and workflow actions remain
   pinned to full commit SHAs with same-line version comments.
14. Confirm GitHub Security settings have been reviewed, including secret
   scanning, push protection, Dependabot security updates, and code scanning.
15. Confirm the GitHub target URL, visibility, license, and scope are approved
   by the user.
16. Push only after the local checks pass.

Post-public profile, website, and resume updates are separate source-backed
tasks.

The HTTP/container expansion uses version `0.2.0` only as unchanged package
metadata inherited from the last release. It is unreleased source and must not
be represented as part of the `v0.2.0` release.

Do not fold in additional private source-repo material until each proposed file
or concept has a fresh allowlist entry, sanitization result, tests or smoke
evidence, and human approval.
