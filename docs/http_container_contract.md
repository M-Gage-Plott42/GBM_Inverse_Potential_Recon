# Local HTTP And Container Contract

Last updated: 2026-08-10

## Evidence Boundary

This repository contains a local FastAPI adapter and a local Docker evidence
image for the bounded Python calculation service. They demonstrate a reviewed
wire contract, container construction, and local lifecycle checks. They do not
demonstrate a cloud deployment, public endpoint, registry publication,
authentication, TLS termination, monitoring, uptime, cost control, or a new
software release.

The base scientific package remains NumPy-only. FastAPI and Uvicorn are an
optional service dependency group, and the HTTP test client is development
only. `gbm_inverse_potential.__init__` does not import the optional adapter.

## HTTP Surface

| Method | Path | Contract |
| --- | --- | --- |
| `POST` | `/v1/reconstruct` | Run one bounded calculation. |
| `GET` | `/health/live` | Return `{"status":"live"}` when the process serves HTTP. |
| `GET` | `/health/ready` | Return `{"status":"ready"}`; there are no external startup dependencies. |
| `GET` | `/version` | Return API/schema/algorithm identities and `source_status=unreleased`. |
| `GET` | `/openapi.json` | Return generated OpenAPI for the four contract paths. |
| `GET` | `/docs` | Serve local Swagger UI for the generated schema. |

ReDoc, the Swagger OAuth redirect, root content, CORS, and alternate
calculation methods are not enabled. The Swagger UI loads browser assets from
a third-party CDN and is local-review convenience only; it must be disabled or
self-hosted before any separately approved public exposure.

## Request Boundary

The reconstruction body is exactly:

```json
{"alpha": 1.0}
```

- `alpha` must be a JSON number from `0.75` through `1.25`, inclusive.
- Booleans, strings, nulls, arrays, objects, NaN, infinities, and out-of-range
  numbers fail validation.
- Extra body fields and every query parameter are rejected.
- Only unencoded `application/json` is accepted.
- The adapter rejects a declared or streamed request body over 1,024 bytes.
- There are no file, upload, URL, path, grid, array, persistence, or arbitrary
  work controls.

The successful response is the exact versioned scalar object documented in
[Deterministic Calculation Service Contract](service_contract.md). It contains
no request ID, timestamp, timing, hostname, path, environment, or stored-input
reference. Successful and operational responses use `Cache-Control: no-store`
and `X-Content-Type-Options: nosniff`.

## Capacity And Failures

One process-local calculation lock permits one scientific calculation at a
time. A simultaneous calculation receives `429` and `Retry-After: 1`; health
and schema requests remain available. The Uvicorn command also caps concurrent
connections/tasks at eight and runs exactly one worker. Above that outer cap,
Uvicorn may return its own plain-text `503` before the request reaches FastAPI;
that server-level overload response does not use the application JSON schema or
application hardening headers.

| Status | Meaning |
| ---: | --- |
| `413` | Request body exceeds the local wire limit. |
| `415` | Content type or content encoding is unsupported. |
| `422` | Body shape/value or query controls violate the contract. |
| `429` | The single calculation slot is occupied. |
| `503` | The numerical core failed its invariant gate (generic JSON), or Uvicorn rejected outer-cap overload before the app (server-level plain text). |
| `500` | An unexpected internal failure occurred. |

Application-originated validation and internal failures use generic responses
and do not echo input, exception messages, tracebacks, dependency versions, or
machine details. OpenAPI describes those application responses; it cannot
describe Uvicorn's pre-application overload envelope.

## Local Process Run

```bash
python -m pip install -e '.[service]'
uvicorn gbm_inverse_potential.http_api:app \
  --host 127.0.0.1 --port 8000 --workers 1 \
  --loop asyncio --http h11 --lifespan off \
  --no-access-log --no-proxy-headers --no-server-header --no-date-header \
  --limit-concurrency 8 --backlog 16 --timeout-keep-alive 5 \
  --timeout-graceful-shutdown 10 --h11-max-incomplete-event-size 16384 \
  --reset-contextvars --log-level warning
```

Use only `127.0.0.1` under this gate.

## Local Container Run

The Dockerfile uses a two-stage `python:3.12.13-slim` build, installs only
wheels in the runtime stage, uses an exec-form Uvicorn command, and runs as
numeric user/group `10001:10001`. The deny-by-default `.dockerignore` sends
only the package/build inputs needed to build the wheel.

The automated evidence command is:

```bash
python scripts/smoke_container.py --build --revision local-review
```

It verifies:

- numeric non-root execution, zero effective capabilities, and
  no-new-privileges;
- read-only root filesystem with no binds, volumes, or tmpfs mounts;
- one CPU, 256 MiB memory, and 64-PID runtime ceilings;
- port `8000` published only to an ephemeral `127.0.0.1` host port;
- image health, exact routes, fixed profile, finite metrics, validation, and
  hardening headers;
- graceful bounded stop, restart, byte-identical calculation output, and exact
  container cleanup; and
- absence of `.git`, tests, docs, environment files, and Docker control files
  from `/app` in the runtime image.

The script never pushes or deletes an image and removes only the unique
container it creates. CI runs the same build/smoke on Python 3.12 without
publishing the image.

## Reproducibility Limit

Direct FastAPI/Uvicorn/test-client versions and the Python patch tag are pinned
for this local slice, and Docker builds use `--pull`. Transitive Python
dependencies are not locked with hashes, and the base image is not bound in
the Dockerfile by digest. A locally observed image ID is evidence for that
build only. Reproducible infrastructure, digest/lock policy, cloud deployment,
monitoring, cost controls, teardown proof, and resume-safe claims require their
later evidence gates.
