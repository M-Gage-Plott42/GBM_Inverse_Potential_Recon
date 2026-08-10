from __future__ import annotations

import math
import threading
import unittest
from concurrent.futures import ThreadPoolExecutor
from unittest.mock import patch

from fastapi.testclient import TestClient

from gbm_inverse_potential import CalculationRequest, run_calculation
from gbm_inverse_potential.http_api import app


class HttpApiTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.client = TestClient(app)

    def test_reconstruction_matches_bounded_python_service(self) -> None:
        for alpha in (0.75, 1, 1.0, 1.25):
            with self.subTest(alpha=alpha):
                expected = run_calculation(CalculationRequest(alpha=alpha)).to_dict()
                response = self.client.post("/v1/reconstruct", json={"alpha": alpha})
                self.assertEqual(response.status_code, 200)
                self.assertEqual(response.json(), expected)
                self.assertLess(len(response.content), 4096)
                self.assertTrue(
                    response.headers["content-type"].startswith("application/json")
                )

    def test_repeated_response_body_is_identical(self) -> None:
        first = self.client.post("/v1/reconstruct", json={"alpha": 1.0})
        second = self.client.post("/v1/reconstruct", json={"alpha": 1.0})
        self.assertEqual(first.status_code, 200)
        self.assertEqual(first.content, second.content)

    def test_request_rejects_non_numeric_and_unbounded_values(self) -> None:
        invalid_payloads = (
            {},
            {"alpha": True},
            {"alpha": False},
            {"alpha": "1.0"},
            {"alpha": None},
            {"alpha": []},
            {"alpha": {}},
            {"alpha": 0.749999},
            {"alpha": 1.250001},
            {"alpha": 10**1000},
            {"alpha": 1.0, "grid_points": 10},
            [],
            [1.0],
            "alpha=1.0",
            1.0,
        )
        with patch("gbm_inverse_potential.http_api.run_calculation") as calculation:
            for payload in invalid_payloads:
                with self.subTest(payload=payload):
                    response = self.client.post("/v1/reconstruct", json=payload)
                    self.assertEqual(response.status_code, 422)
                    self.assertEqual(response.json(), {"detail": "invalid request"})
        calculation.assert_not_called()

    def test_request_rejects_non_finite_json_numbers(self) -> None:
        with patch("gbm_inverse_potential.http_api.run_calculation") as calculation:
            for token in ("NaN", "Infinity", "-Infinity", "1e309", "-1e309"):
                with self.subTest(token=token):
                    response = self.client.post(
                        "/v1/reconstruct",
                        content=f'{{"alpha":{token}}}',
                        headers={"Content-Type": "application/json"},
                    )
                    self.assertEqual(response.status_code, 422)
                    self.assertEqual(response.json(), {"detail": "invalid request"})
        calculation.assert_not_called()

    def test_wire_boundary_rejects_queries_media_types_and_large_bodies(self) -> None:
        with patch("gbm_inverse_potential.http_api.run_calculation") as calculation:
            query = self.client.post("/v1/reconstruct?q_points=1", json={"alpha": 1.0})
            text = self.client.post(
                "/v1/reconstruct",
                content='{"alpha":1.0}',
                headers={"Content-Type": "text/plain"},
            )
            encoded = self.client.post(
                "/v1/reconstruct",
                content=b"not-really-gzip",
                headers={
                    "Content-Type": "application/json",
                    "Content-Encoding": "gzip",
                },
            )
            oversized = self.client.post(
                "/v1/reconstruct",
                content=b"{" + b" " * 1024 + b"}",
                headers={"Content-Type": "application/json"},
            )
            chunked_oversized = self.client.post(
                "/v1/reconstruct",
                content=iter([b'{"alpha":1,"padding":"', b"x" * 1100, b'"}']),
                headers={"Content-Type": "application/json"},
            )
            malformed = self.client.post(
                "/v1/reconstruct",
                content=b'{"alpha":',
                headers={"Content-Type": "application/json"},
            )
        self.assertEqual(query.status_code, 422)
        self.assertEqual(text.status_code, 415)
        self.assertEqual(encoded.status_code, 415)
        self.assertEqual(oversized.status_code, 413)
        self.assertEqual(chunked_oversized.status_code, 413)
        self.assertEqual(malformed.status_code, 422)
        calculation.assert_not_called()

    def test_health_and_version_contracts(self) -> None:
        live = self.client.get("/health/live")
        ready = self.client.get("/health/ready")
        version = self.client.get("/version")
        self.assertEqual(live.status_code, 200)
        self.assertEqual(live.json(), {"status": "live"})
        self.assertEqual(ready.status_code, 200)
        self.assertEqual(ready.json(), {"status": "ready"})
        self.assertEqual(
            version.json(),
            {
                "api_version": "1.0",
                "schema_version": "1.0",
                "algorithm_version": "1.0",
                "source_status": "unreleased",
            },
        )

    def test_simultaneous_request_is_rejected_and_slot_recovers(self) -> None:
        expected = run_calculation(CalculationRequest(alpha=1.0))
        entered = threading.Event()
        release = threading.Event()

        def blocked_calculation(_request: CalculationRequest):
            entered.set()
            if not release.wait(timeout=5):
                raise RuntimeError("test calculation was not released")
            return expected

        with patch(
            "gbm_inverse_potential.http_api.run_calculation",
            side_effect=blocked_calculation,
        ) as calculation:
            with ThreadPoolExecutor(max_workers=1) as executor:
                first_future = executor.submit(
                    self.client.post,
                    "/v1/reconstruct",
                    json={"alpha": 1.0},
                )
                self.assertTrue(entered.wait(timeout=5))
                ready = self.client.get("/health/ready")
                second = self.client.post("/v1/reconstruct", json={"alpha": 1.0})
                release.set()
                first = first_future.result(timeout=5)
            third = self.client.post("/v1/reconstruct", json={"alpha": 1.0})
        self.assertEqual(ready.status_code, 200)
        self.assertEqual(ready.json(), {"status": "ready"})
        self.assertEqual(second.status_code, 429)
        self.assertEqual(second.headers["retry-after"], "1")
        self.assertEqual(first.status_code, 200)
        self.assertEqual(third.status_code, 200)
        self.assertEqual(calculation.call_count, 2)

    def test_internal_failure_is_not_exposed(self) -> None:
        opaque_client = TestClient(app, raise_server_exceptions=False)
        with patch(
            "gbm_inverse_potential.http_api.run_calculation",
            side_effect=RuntimeError("private internal diagnostic"),
        ):
            unexpected = opaque_client.post("/v1/reconstruct", json={"alpha": 1.0})
        self.assertEqual(unexpected.status_code, 500)
        self.assertEqual(unexpected.json(), {"detail": "internal server error"})
        self.assertNotIn("private internal diagnostic", unexpected.text)

        from gbm_inverse_potential import (
            CalculationInputError,
            CalculationInvariantError,
        )

        with patch(
            "gbm_inverse_potential.http_api.run_calculation",
            side_effect=CalculationInputError("private input diagnostic"),
        ):
            rejected = self.client.post("/v1/reconstruct", json={"alpha": 1.0})
        self.assertEqual(rejected.status_code, 422)
        self.assertEqual(rejected.json(), {"detail": "invalid calculation request"})
        self.assertNotIn("private input diagnostic", rejected.text)

        with patch(
            "gbm_inverse_potential.http_api.run_calculation",
            side_effect=CalculationInvariantError("private internal diagnostic"),
        ):
            response = self.client.post("/v1/reconstruct", json={"alpha": 1.0})
        self.assertEqual(response.status_code, 503)
        self.assertEqual(response.json(), {"detail": "calculation unavailable"})
        self.assertNotIn("private internal diagnostic", response.text)

    def test_openapi_has_only_the_intended_contract_paths(self) -> None:
        response = self.client.get("/openapi.json")
        self.assertEqual(response.status_code, 200)
        schema = response.json()
        self.assertEqual(
            set(schema["paths"]),
            {"/health/live", "/health/ready", "/version", "/v1/reconstruct"},
        )
        request_schema = schema["components"]["schemas"]["ReconstructionRequest"]
        self.assertEqual(request_schema["required"], ["alpha"])
        self.assertFalse(request_schema["additionalProperties"])
        alpha = request_schema["properties"]["alpha"]
        self.assertEqual(alpha["minimum"], 0.75)
        self.assertEqual(alpha["maximum"], 1.25)
        error_schema = schema["paths"]["/v1/reconstruct"]["post"]["responses"]["422"]
        self.assertEqual(
            error_schema["content"]["application/json"]["schema"]["$ref"],
            "#/components/schemas/ErrorResponse",
        )

    def test_unpublished_routes_and_methods_are_closed(self) -> None:
        self.assertEqual(self.client.get("/").status_code, 404)
        self.assertEqual(self.client.get("/redoc").status_code, 404)
        self.assertEqual(self.client.get("/docs/oauth2-redirect").status_code, 404)
        self.assertEqual(self.client.get("/v1/reconstruct").status_code, 405)
        self.assertEqual(self.client.options("/v1/reconstruct").status_code, 405)
        docs = self.client.get("/docs")
        self.assertEqual(docs.status_code, 200)
        self.assertIn("swagger-ui", docs.text.lower())

    def test_response_hardening_headers_are_present_without_cors_or_cookies(
        self,
    ) -> None:
        response = self.client.get(
            "/version", headers={"Origin": "https://example.invalid"}
        )
        self.assertEqual(response.headers["cache-control"], "no-store")
        self.assertEqual(response.headers["x-content-type-options"], "nosniff")
        self.assertNotIn("access-control-allow-origin", response.headers)
        self.assertNotIn("set-cookie", response.headers)

    def test_nan_is_not_present_in_success_response(self) -> None:
        response = self.client.post("/v1/reconstruct", json={"alpha": 1.0})
        self.assertEqual(response.status_code, 200)
        for value in response.json()["metrics"].values():
            self.assertTrue(math.isfinite(value))


if __name__ == "__main__":
    unittest.main()
