ARG PYTHON_IMAGE=python:3.12.13-slim

FROM ${PYTHON_IMAGE} AS build

ENV PIP_DISABLE_PIP_VERSION_CHECK=1 \
    PIP_ROOT_USER_ACTION=ignore
WORKDIR /build

COPY LICENSE README.md pyproject.toml requirements.txt requirements-service.txt ./
COPY src ./src

RUN python -m pip wheel --no-cache-dir --wheel-dir /wheels -r requirements-service.txt \
    && python -m pip wheel --no-cache-dir --no-deps --wheel-dir /wheels .

FROM ${PYTHON_IMAGE} AS runtime

ARG VCS_REF=uncommitted
LABEL org.opencontainers.image.title="GBM Inverse Potential Reconstruction API" \
      org.opencontainers.image.description="Local bounded scientific calculation API evidence image" \
      org.opencontainers.image.source="https://github.com/M-Gage-Plott42/GBM_Inverse_Potential_Recon" \
      org.opencontainers.image.revision="${VCS_REF}" \
      org.opencontainers.image.version="unreleased"

ENV PIP_DISABLE_PIP_VERSION_CHECK=1 \
    PIP_ROOT_USER_ACTION=ignore \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONHASHSEED=0 \
    PYTHONUNBUFFERED=1
WORKDIR /app

COPY --from=build /wheels /wheels
RUN python -m pip install --no-cache-dir --no-compile /wheels/* \
    && rm -r /wheels

USER 10001:10001
EXPOSE 8000
STOPSIGNAL SIGTERM

HEALTHCHECK --interval=5s --timeout=3s --start-period=5s --retries=3 \
    CMD ["python", "-c", "import urllib.request; urllib.request.urlopen('http://127.0.0.1:8000/health/live', timeout=2).read()"]

CMD ["uvicorn", "gbm_inverse_potential.http_api:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "1", "--loop", "asyncio", "--http", "h11", "--lifespan", "off", "--no-access-log", "--no-proxy-headers", "--no-server-header", "--no-date-header", "--limit-concurrency", "8", "--backlog", "16", "--timeout-keep-alive", "5", "--timeout-graceful-shutdown", "10", "--h11-max-incomplete-event-size", "16384", "--reset-contextvars", "--log-level", "warning"]
