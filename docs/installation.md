# Installation

## Requirements

- Python 3.10 or newer
- `numpy>=1.26`

## From A Local Clone

```bash
git clone https://github.com/M-Gage-Plott42/GBM_Inverse_Potential_Recon.git
cd GBM_Inverse_Potential_Recon
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -e .
```

## Development Checks

```bash
python -m pip install -r requirements-dev.txt
python -m pip install -e .
python -m unittest discover -s tests
coverage run -m unittest discover -s tests
coverage report
python scripts/sanitize_scan.py .
mkdocs build --strict
```

The package exposes the console entry point:

```bash
gbm-inverse-demo --json
```

The same smoke demo is available as a module command:

```bash
python -m gbm_inverse_potential.cli --json
```
