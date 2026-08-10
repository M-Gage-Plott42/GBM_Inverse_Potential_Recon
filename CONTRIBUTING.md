# Contributing

This project is not open for broad external contribution during the initial
public v0 phase. Small issues and documentation corrections can be considered
when they stay within the current public-safety scope.

Before proposing changes, run:

```bash
python -m pip install -r requirements-dev.txt
python -m pip install -e .
coverage run -m unittest discover -s tests
coverage report --fail-under=80
python -m unittest discover -s tests
python scripts/sanitize_scan.py .
mkdocs build --strict
```

For HTTP, Dockerfile, dependency, or container changes, also run:

```bash
python scripts/smoke_container.py --build --revision local-review
```

The smoke is local-only and must not push an image. Follow
`docs/publish_gate.md` for the complete scope and review boundary.
