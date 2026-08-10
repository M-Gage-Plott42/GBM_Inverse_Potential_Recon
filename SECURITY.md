# Security Policy

## Supported Versions

This repository is an initial public v0 artifact. Security reports should
target the current `main` branch only.

## Reporting A Vulnerability

Do not open a public issue for suspected secrets or private-data exposure.
Use GitHub private vulnerability reporting if enabled, or a private maintainer
contact channel.

## Data-Safety Boundary

This repository should not contain credentials, private paths, raw run logs,
private manuscript or handoff material, browser/session exports, local machine
configuration, or large generated artifacts. Run `python scripts/sanitize_scan.py .`
before any public push.

The optional HTTP adapter is approved only for local, nonpersistent,
no-upload use under the current evidence gate. Bind it to `127.0.0.1`; do not
expose the API or Swagger UI to the internet, add credentials to the image or
build context, or represent the local image as deployed. Public exposure would
require a separate review of TLS, authentication/authorization, rate and body
limits, proxy trust, self-hosted or disabled documentation assets, logging,
monitoring, and teardown controls.
