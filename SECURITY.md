# Security Policy

## Supported Versions

This repository is a draft public artifact. Before public release, security
reports should target the current `main` branch only.

## Reporting A Vulnerability

Do not open a public issue for suspected secrets or private-data exposure.
Use a private maintainer contact channel until GitHub private vulnerability
reporting is enabled for the public repository.

## Data-Safety Boundary

This repository should not contain credentials, private paths, raw run logs,
private manuscript or handoff material, browser/session exports, local machine
configuration, or large generated artifacts. Run `python scripts/sanitize_scan.py .`
before any public push.
