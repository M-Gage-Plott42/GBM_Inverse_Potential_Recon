# Coverage

Coverage is measured with `coverage.py` in CI.

Local command:

```bash
coverage run -m unittest discover -s tests
coverage report
coverage json -o /tmp/gbm_coverage.json
python scripts/write_coverage_badge.py /tmp/gbm_coverage.json docs/assets/coverage.svg
```

The CI workflow fails if package coverage drops below the configured threshold, then
regenerates `docs/assets/coverage.svg` and verifies that the committed badge is
current.

Current badge:

![Coverage](assets/coverage.svg)
