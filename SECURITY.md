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
