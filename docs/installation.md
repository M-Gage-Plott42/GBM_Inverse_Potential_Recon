# Installation

## Requirements

- Python 3.10 or newer
- Base library: `numpy>=1.26`
- Optional local service: `fastapi==0.141.1` and `uvicorn==0.52.1`
- Development HTTP tests: `httpx2==2.10.0`

## From A Local Clone

```bash
git clone https://github.com/M-Gage-Plott42/GBM_Inverse_Potential_Recon.git
cd GBM_Inverse_Potential_Recon
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -e .
```

The base install remains NumPy-only. To install the local HTTP adapter:

```bash
python -m pip install -e '.[service]'
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

`requirements-dev.txt` includes the optional service stack and the HTTP test
client so test discovery covers both Python and wire contracts.

The package exposes the console entry point:

```bash
gbm-inverse-demo --json
```

The same smoke demo is available as a module command:

```bash
python -m gbm_inverse_potential.cli --json
```

## Local HTTP Process

```bash
uvicorn gbm_inverse_potential.http_api:app \
  --host 127.0.0.1 --port 8000 --workers 1 \
  --no-access-log --no-proxy-headers --no-server-header --no-date-header
```

Keep the host binding on loopback. The full reviewed Uvicorn command and wire
limits are in
[Local HTTP And Container Contract](http_container_contract.md).

## Local Docker Evidence

Docker Desktop or Docker Engine must be running and reachable by the current
shell. The automated build and lifecycle evidence command is:

```bash
python scripts/smoke_container.py --build --revision local-review
```

The command builds `gbm-inverse-potential-recon:local-evidence`, publishes the
container port to an ephemeral loopback port, validates the hardened runtime
and API, stops and restarts it, and removes only its uniquely named container.
It does not push or delete the image.
