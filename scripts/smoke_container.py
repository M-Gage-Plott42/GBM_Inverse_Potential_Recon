#!/usr/bin/env python3
"""Build and exercise the local-only hardened API container."""

from __future__ import annotations

import argparse
import json
import math
import os
import socket
import subprocess
import sys
import time
import urllib.error
import urllib.request
import uuid
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_IMAGE = "gbm-inverse-potential-recon:local-evidence"
CONTAINER_PORT = 8000
MEMORY_LIMIT_BYTES = 256 * 1024 * 1024


class SmokeFailure(RuntimeError):
    """Raised when local container evidence violates its contract."""


def _run(
    command: list[str], *, capture: bool = True
) -> subprocess.CompletedProcess[str]:
    result = subprocess.run(
        command,
        cwd=ROOT,
        check=False,
        text=True,
        stdout=subprocess.PIPE if capture else None,
        stderr=subprocess.STDOUT if capture else None,
    )
    if result.returncode != 0:
        output = result.stdout or ""
        raise SmokeFailure(
            f"command failed ({result.returncode}): {' '.join(command)}\n{output}"
        )
    return result


def _free_loopback_port() -> int:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as listener:
        listener.bind(("127.0.0.1", 0))
        return int(listener.getsockname()[1])


def _inspect(target: str) -> dict[str, Any]:
    payload = json.loads(_run(["docker", "inspect", target]).stdout)
    if not isinstance(payload, list) or len(payload) != 1:
        raise SmokeFailure(f"unexpected docker inspect payload for {target}")
    return payload[0]


def _request(
    base_url: str,
    path: str,
    *,
    method: str = "GET",
    payload: object | None = None,
    raw_body: bytes | None = None,
    headers: dict[str, str] | None = None,
) -> tuple[int, bytes, dict[str, str]]:
    body = raw_body
    request_headers = dict(headers or {})
    if payload is not None:
        body = json.dumps(payload, allow_nan=False, separators=(",", ":")).encode(
            "utf-8"
        )
        request_headers["Content-Type"] = "application/json"
    request = urllib.request.Request(
        base_url + path,
        data=body,
        headers=request_headers,
        method=method,
    )
    opener = urllib.request.build_opener(urllib.request.ProxyHandler({}))
    try:
        with opener.open(request, timeout=15) as response:
            return response.status, response.read(), dict(response.headers.items())
    except urllib.error.HTTPError as exc:
        return exc.code, exc.read(), dict(exc.headers.items())


def _json(body: bytes) -> Any:
    try:
        return json.loads(body)
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise SmokeFailure(f"response is not valid JSON: {body[:200]!r}") from exc


def _wait_for_http(base_url: str, container: str, timeout: float = 45.0) -> None:
    deadline = time.monotonic() + timeout
    while time.monotonic() < deadline:
        try:
            status_code, body, _headers = _request(base_url, "/health/live")
            if status_code == 200 and _json(body) == {"status": "live"}:
                return
        except (OSError, SmokeFailure, urllib.error.URLError):
            pass
        state = _inspect(container)["State"]
        if not state["Running"]:
            logs = _run(["docker", "logs", container]).stdout
            raise SmokeFailure(f"container exited before health response:\n{logs}")
        time.sleep(0.25)
    logs = _run(["docker", "logs", container]).stdout
    raise SmokeFailure(f"timed out waiting for HTTP health response:\n{logs}")


def _wait_for_docker_health(container: str, timeout: float = 30.0) -> None:
    deadline = time.monotonic() + timeout
    while time.monotonic() < deadline:
        state = _inspect(container)["State"]
        health = state.get("Health", {}).get("Status")
        if state["Running"] and health == "healthy":
            return
        if not state["Running"] or health == "unhealthy":
            logs = _run(["docker", "logs", container]).stdout
            raise SmokeFailure(f"container health failed ({health}):\n{logs}")
        time.sleep(0.5)
    raise SmokeFailure("timed out waiting for Docker HEALTHCHECK")


def _assert_image_contract(image: str, revision: str) -> str:
    inspected = _inspect(image)
    config = inspected["Config"]
    if config["User"] != "10001:10001":
        raise SmokeFailure(
            f"image user is not the approved numeric identity: {config['User']!r}"
        )
    command = config.get("Cmd") or []
    required_arguments = {
        "--workers": "1",
        "--no-access-log": None,
        "--no-proxy-headers": None,
        "--no-server-header": None,
        "--no-date-header": None,
        "--limit-concurrency": "8",
    }
    for option, value in required_arguments.items():
        if option not in command:
            raise SmokeFailure(f"image command is missing {option}")
        if value is not None and command[command.index(option) + 1] != value:
            raise SmokeFailure(f"image command has an unexpected {option} value")
    labels = config.get("Labels") or {}
    if labels.get("org.opencontainers.image.revision") != revision:
        raise SmokeFailure(
            "image revision label does not match the requested source identity"
        )
    if labels.get("org.opencontainers.image.version") != "unreleased":
        raise SmokeFailure("image must retain unreleased source status")
    if not config.get("Healthcheck", {}).get("Test"):
        raise SmokeFailure("image does not define a HEALTHCHECK")
    if config.get("ExposedPorts") != {"8000/tcp": {}}:
        raise SmokeFailure("image must expose only the reviewed container port")
    if config.get("StopSignal") != "SIGTERM":
        raise SmokeFailure(
            "image stop signal differs from the graceful-shutdown contract"
        )
    if "--reload" in command:
        raise SmokeFailure("image must not enable development reload")
    return inspected["Id"]


def _assert_runtime_contract(container: str, host_port: int) -> None:
    inspected = _inspect(container)
    host = inspected["HostConfig"]
    if not host["ReadonlyRootfs"]:
        raise SmokeFailure("container root filesystem is writable")
    if set(host.get("CapDrop") or []) != {"ALL"}:
        raise SmokeFailure("container capabilities were not all dropped")
    if not any(
        value.startswith("no-new-privileges") for value in host.get("SecurityOpt") or []
    ):
        raise SmokeFailure("container does not enforce no-new-privileges")
    if host["Memory"] != MEMORY_LIMIT_BYTES or host["NanoCpus"] != 1_000_000_000:
        raise SmokeFailure("container CPU or memory limit differs from the contract")
    if host["PidsLimit"] != 64:
        raise SmokeFailure("container PID limit differs from the contract")
    if host.get("Init") is not True:
        raise SmokeFailure("container init process is not enabled")
    expected_ulimit = [{"Name": "nofile", "Hard": 1024, "Soft": 1024}]
    if host.get("Ulimits") != expected_ulimit:
        raise SmokeFailure("container file-descriptor limit differs from the contract")
    if host.get("Binds") or inspected.get("Mounts"):
        raise SmokeFailure("container unexpectedly has a bind, volume, or tmpfs mount")
    if host.get("RestartPolicy", {}).get("Name") != "no":
        raise SmokeFailure("container has an unapproved restart policy")
    bindings = host["PortBindings"].get(f"{CONTAINER_PORT}/tcp") or []
    if bindings != [{"HostIp": "127.0.0.1", "HostPort": str(host_port)}]:
        raise SmokeFailure(f"container port is not loopback-only: {bindings!r}")

    process_status = _run(
        [
            "docker",
            "exec",
            container,
            "python",
            "-c",
            "from pathlib import Path; print(Path('/proc/1/status').read_text())",
        ]
    ).stdout
    status_values = {}
    for line in process_status.splitlines():
        if ":" in line:
            key, value = line.split(":", 1)
            status_values[key] = value.strip()
    effective_uid = int(status_values["Uid"].split()[1])
    if effective_uid == 0:
        raise SmokeFailure("container PID 1 is running as root")
    if status_values.get("CapEff") != "0000000000000000":
        raise SmokeFailure("container PID 1 retains effective capabilities")
    if status_values.get("NoNewPrivs") != "1":
        raise SmokeFailure("container PID 1 lacks no-new-privileges")

    filesystem_probe = _run(
        [
            "docker",
            "exec",
            container,
            "python",
            "-c",
            (
                "from pathlib import Path; "
                "targets=[Path('/probe'),Path('/app/probe'),Path('/tmp/probe')]; "
                "print(all(not p.exists() for p in targets))"
            ),
        ]
    ).stdout.strip()
    if filesystem_probe != "True":
        raise SmokeFailure("unexpected file exists at a write-probe location")
    for target in ("/probe", "/app/probe", "/tmp/probe"):
        probe = subprocess.run(
            [
                "docker",
                "exec",
                container,
                "python",
                "-c",
                f"from pathlib import Path; Path({target!r}).write_text('x')",
            ],
            cwd=ROOT,
            check=False,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
        )
        if probe.returncode == 0:
            raise SmokeFailure(f"read-only write unexpectedly succeeded at {target}")

    content_probe = _run(
        [
            "docker",
            "exec",
            container,
            "python",
            "-c",
            (
                "from pathlib import Path; "
                "blocked=['.git','tests','docs','.env','Dockerfile']; "
                "print(any((Path('/app')/name).exists() for name in blocked))"
            ),
        ]
    ).stdout.strip()
    if content_probe != "False":
        raise SmokeFailure("runtime image contains a blocked build-context path")


def _assert_http_contract(base_url: str) -> bytes:
    live_status, live_body, live_headers = _request(base_url, "/health/live")
    ready_status, ready_body, _ = _request(base_url, "/health/ready")
    version_status, version_body, _ = _request(base_url, "/version")
    if (live_status, _json(live_body)) != (200, {"status": "live"}):
        raise SmokeFailure("liveness response differs from the contract")
    if (ready_status, _json(ready_body)) != (200, {"status": "ready"}):
        raise SmokeFailure("readiness response differs from the contract")
    if (version_status, _json(version_body)) != (
        200,
        {
            "api_version": "1.0",
            "schema_version": "1.0",
            "algorithm_version": "1.0",
            "source_status": "unreleased",
        },
    ):
        raise SmokeFailure("version response differs from the contract")
    lowered_headers = {key.lower(): value for key, value in live_headers.items()}
    if "server" in lowered_headers or "date" in lowered_headers:
        raise SmokeFailure("server fingerprint headers are present")
    if lowered_headers.get("x-content-type-options") != "nosniff":
        raise SmokeFailure("hardening response header is missing")
    if lowered_headers.get("cache-control") != "no-store":
        raise SmokeFailure("no-store response header is missing")

    openapi_status, openapi_body, _ = _request(base_url, "/openapi.json")
    paths = set(_json(openapi_body)["paths"])
    expected_paths = {"/health/live", "/health/ready", "/version", "/v1/reconstruct"}
    if openapi_status != 200 or paths != expected_paths:
        raise SmokeFailure("OpenAPI paths differ from the reviewed contract")
    docs_status, docs_body, _ = _request(base_url, "/docs")
    if docs_status != 200 or b"swagger-ui" not in docs_body.lower():
        raise SmokeFailure("local Swagger UI is unavailable")

    valid_status, valid_body, valid_headers = _request(
        base_url, "/v1/reconstruct", method="POST", payload={"alpha": 1.0}
    )
    if valid_status != 200 or len(valid_body) >= 4096:
        raise SmokeFailure("bounded reconstruction response is invalid or oversized")
    valid = _json(valid_body)
    if valid["input"] != {"alpha": 1.0}:
        raise SmokeFailure("normalized input differs from the contract")
    if valid["profile"]["grid_work"] != 1_600_000:
        raise SmokeFailure("fixed work profile differs from the contract")
    if not all(math.isfinite(value) for value in valid["metrics"].values()):
        raise SmokeFailure("reconstruction returned a non-finite metric")
    valid_lowered = {key.lower(): value for key, value in valid_headers.items()}
    if not valid_lowered.get("content-type", "").startswith("application/json"):
        raise SmokeFailure("reconstruction response is not JSON")

    invalid_status, invalid_body, _ = _request(
        base_url,
        "/v1/reconstruct",
        method="POST",
        payload={"alpha": 1.0, "q_points": 1},
    )
    if (invalid_status, _json(invalid_body)) != (422, {"detail": "invalid request"}):
        raise SmokeFailure("invalid request did not fail closed")
    query_status, _query_body, _ = _request(
        base_url, "/v1/reconstruct?q_points=1", method="POST", payload={"alpha": 1.0}
    )
    if query_status != 422:
        raise SmokeFailure("unexpected query control was not rejected")
    oversized_status, oversized_body, _ = _request(
        base_url,
        "/v1/reconstruct",
        method="POST",
        raw_body=b"{" + b" " * 1024 + b"}",
        headers={"Content-Type": "application/json"},
    )
    if (oversized_status, _json(oversized_body)) != (
        413,
        {"detail": "request body too large"},
    ):
        raise SmokeFailure("oversized body did not fail at the wire boundary")
    return valid_body


def _build(image: str, revision: str) -> None:
    _run(
        [
            "docker",
            "build",
            "--pull",
            "--build-arg",
            f"VCS_REF={revision}",
            "--tag",
            image,
            ".",
        ],
        capture=False,
    )


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--image", default=DEFAULT_IMAGE)
    parser.add_argument("--revision", default="local-uncommitted")
    parser.add_argument("--build", action="store_true")
    args = parser.parse_args(argv)

    _run(["docker", "info"])
    if args.build:
        _build(args.image, args.revision)
    image_id = _assert_image_contract(args.image, args.revision)

    host_port = _free_loopback_port()
    container = f"gbm-api-smoke-{os.getpid()}-{uuid.uuid4().hex[:8]}"
    base_url = f"http://127.0.0.1:{host_port}"
    created = False
    primary_failure: BaseException | None = None
    try:
        _run(
            [
                "docker",
                "run",
                "--detach",
                "--name",
                container,
                "--init",
                "--read-only",
                "--cap-drop=ALL",
                "--security-opt=no-new-privileges:true",
                "--pids-limit=64",
                "--memory=256m",
                "--cpus=1",
                "--ulimit=nofile=1024:1024",
                "--stop-timeout=10",
                "--publish",
                f"127.0.0.1:{host_port}:{CONTAINER_PORT}",
                args.image,
            ]
        )
        created = True
        _wait_for_http(base_url, container)
        _wait_for_docker_health(container)
        _assert_runtime_contract(container, host_port)
        first_body = _assert_http_contract(base_url)

        _run(["docker", "stop", "--time", "10", container])
        stopped = _inspect(container)["State"]
        if (
            stopped["Running"]
            or stopped["OOMKilled"]
            or stopped["ExitCode"] not in {0, 143}
        ):
            raise SmokeFailure(f"container did not stop cleanly: {stopped!r}")
        _run(["docker", "start", container])
        _wait_for_http(base_url, container)
        _wait_for_docker_health(container)
        second_status, second_body, _ = _request(
            base_url, "/v1/reconstruct", method="POST", payload={"alpha": 1.0}
        )
        if second_status != 200 or second_body != first_body:
            raise SmokeFailure("restart did not preserve deterministic response bytes")
    except BaseException as exc:
        primary_failure = exc
        raise
    finally:
        if created:
            subprocess.run(
                ["docker", "rm", "--force", container],
                cwd=ROOT,
                check=False,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
            )
            remaining = subprocess.run(
                ["docker", "inspect", container],
                cwd=ROOT,
                check=False,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
            )
            if remaining.returncode == 0:
                cleanup_error = SmokeFailure(
                    f"container cleanup did not remove the exact target {container}"
                )
                if primary_failure is None:
                    raise cleanup_error
                print(f"additional cleanup failure: {cleanup_error}", file=sys.stderr)

    print(
        json.dumps(
            {
                "container_lifecycle": "passed",
                "host_binding": "127.0.0.1",
                "image": args.image,
                "image_id": image_id,
                "revision": args.revision,
                "runtime_user": "10001:10001",
            },
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except SmokeFailure as exc:
        print(f"container smoke failed: {exc}", file=sys.stderr)
        raise SystemExit(1) from exc
