from __future__ import annotations

import json
import math
import unittest
from dataclasses import fields
from unittest.mock import patch

from gbm_inverse_potential import (
    ALPHA_MAX,
    ALPHA_MIN,
    PUBLIC_STANDARD_PROFILE,
    CalculationInputError,
    CalculationInvariantError,
    CalculationRequest,
    harmonic_oscillator_demo,
    run_calculation,
)


class CalculationServiceTests(unittest.TestCase):
    def test_request_exposes_only_bounded_alpha(self) -> None:
        self.assertEqual([field.name for field in fields(CalculationRequest)], ["alpha"])
        self.assertEqual(CalculationRequest(alpha=ALPHA_MIN).alpha, ALPHA_MIN)
        self.assertEqual(CalculationRequest(alpha=ALPHA_MAX).alpha, ALPHA_MAX)

    def test_request_rejects_invalid_values(self) -> None:
        invalid_values = (
            True,
            False,
            "1.0",
            None,
            math.nan,
            math.inf,
            -math.inf,
            0.0,
            ALPHA_MIN - 0.01,
            ALPHA_MAX + 0.01,
        )
        for value in invalid_values:
            with self.subTest(value=value), self.assertRaises(CalculationInputError):
                CalculationRequest(alpha=value)  # type: ignore[arg-type]

    def test_result_schema_is_stable_and_json_compatible(self) -> None:
        payload = run_calculation(CalculationRequest()).to_dict()
        self.assertEqual(
            list(payload),
            [
                "schema_version",
                "calculation",
                "input",
                "units",
                "profile",
                "metrics",
                "quality_gate",
                "limitations",
            ],
        )
        self.assertEqual(payload["schema_version"], "1.0")
        self.assertEqual(payload["quality_gate"], "public-smoke-v1")
        self.assertEqual(payload["input"], {"alpha": 1.0})
        self.assertEqual(
            list(payload["calculation"]),
            ["id", "algorithm_version", "software"],
        )
        self.assertEqual(
            payload["calculation"]["id"],
            "harmonic-oscillator-inverse-potential",
        )
        self.assertEqual(payload["calculation"]["algorithm_version"], "1.0")
        self.assertEqual(
            payload["calculation"]["software"],
            {"name": "gbm-inverse-potential-recon"},
        )
        self.assertEqual(
            list(payload["units"]),
            ["system", "hbar_squared_over_2m", "alpha", "potential"],
        )
        self.assertEqual(payload["units"]["system"], "reduced")
        self.assertEqual(payload["units"]["hbar_squared_over_2m"], 1.0)
        self.assertEqual(
            payload["limitations"],
            [
                "harmonic_oscillator_ground_state_only",
                "analytic_form_factor_input",
                "finite_difference_stable_window_only",
            ],
        )
        profile = payload["profile"]
        self.assertIsInstance(profile, dict)
        self.assertEqual(
            list(profile),
            [
                "id",
                "r_min",
                "r_max",
                "r_points",
                "q_min",
                "q_max",
                "q_points",
                "grid_work",
            ],
        )
        self.assertEqual(profile["id"], "public-standard-v1")
        self.assertEqual(profile["grid_work"], 1_600_000)
        self.assertEqual(
            list(payload["metrics"]),
            [
                "density_l2_rel",
                "density_max_rel_window",
                "density_norm_trapz",
                "potential_l2_rel_window",
                "potential_max_abs_window",
            ],
        )
        json.dumps(payload, allow_nan=False, sort_keys=True)

    def test_profile_is_fixed_and_bounded(self) -> None:
        profile = PUBLIC_STANDARD_PROFILE
        self.assertEqual(profile.r_min, 0.02)
        self.assertEqual(profile.r_max, 4.0)
        self.assertEqual(profile.r_points, 400)
        self.assertEqual(profile.q_min, 0.0)
        self.assertEqual(profile.q_max, 16.0)
        self.assertEqual(profile.q_points, 4000)
        self.assertEqual(profile.grid_work, 1_600_000)

    def test_repeated_requests_are_equal(self) -> None:
        first = run_calculation(CalculationRequest(alpha=1.0))
        second = run_calculation(CalculationRequest(alpha=1))
        self.assertEqual(first, second)
        self.assertEqual(first.to_dict(), second.to_dict())

    def test_service_matches_existing_core_metrics(self) -> None:
        result = run_calculation(CalculationRequest(alpha=1.0))
        self.assertEqual(result.legacy_metrics(), harmonic_oscillator_demo())

    def test_service_calls_core_with_fixed_profile(self) -> None:
        raw = harmonic_oscillator_demo()
        with patch(
            "gbm_inverse_potential.service.harmonic_oscillator_demo",
            return_value=raw,
        ) as core:
            run_calculation(CalculationRequest(alpha=1.0))
        core.assert_called_once_with(
            alpha=1.0,
            r_min=0.02,
            r_max=4.0,
            r_points=400,
            q_max=16.0,
            q_points=4000,
        )

    def test_supported_interval_passes_quality_contract(self) -> None:
        for step in range(101):
            alpha = round(ALPHA_MIN + step * (ALPHA_MAX - ALPHA_MIN) / 100, 6)
            with self.subTest(alpha=alpha):
                result = run_calculation(CalculationRequest(alpha=alpha))
                self.assertLess(result.density_l2_rel, 1.0e-8)
                self.assertLess(result.density_max_rel_window, 1.0e-8)
                self.assertLess(abs(result.density_norm_trapz - 1.0), 5.0e-5)
                self.assertLess(result.potential_l2_rel_window, 1.0e-3)
                self.assertLess(result.potential_max_abs_window, 1.0e-3)

    def test_nonfinite_core_metric_fails_closed(self) -> None:
        raw = harmonic_oscillator_demo()
        raw["density_l2_rel"] = math.nan
        with patch("gbm_inverse_potential.service.harmonic_oscillator_demo", return_value=raw):
            with self.assertRaisesRegex(CalculationInvariantError, "density_l2_rel"):
                run_calculation(CalculationRequest())

    def test_malformed_request_fails_closed(self) -> None:
        with self.assertRaisesRegex(CalculationInputError, "CalculationRequest"):
            run_calculation({"alpha": 1.0})  # type: ignore[arg-type]

    def test_nonnumeric_core_metric_fails_closed(self) -> None:
        raw = harmonic_oscillator_demo()
        raw["density_l2_rel"] = True
        with patch(
            "gbm_inverse_potential.service.harmonic_oscillator_demo",
            return_value=raw,
        ):
            with self.assertRaisesRegex(CalculationInvariantError, "density_l2_rel"):
                run_calculation(CalculationRequest())

    def test_failed_quality_metric_fails_closed(self) -> None:
        raw = harmonic_oscillator_demo()
        raw["potential_max_abs_window"] = 1.0
        with patch("gbm_inverse_potential.service.harmonic_oscillator_demo", return_value=raw):
            with self.assertRaisesRegex(CalculationInvariantError, "potential_max_abs_window"):
                run_calculation(CalculationRequest())

    def test_negative_error_metric_fails_closed(self) -> None:
        raw = harmonic_oscillator_demo()
        raw["density_l2_rel"] = -1.0
        with patch(
            "gbm_inverse_potential.service.harmonic_oscillator_demo",
            return_value=raw,
        ):
            with self.assertRaisesRegex(CalculationInvariantError, "density_l2_rel"):
                run_calculation(CalculationRequest())

    def test_mismatched_core_alpha_fails_closed(self) -> None:
        raw = harmonic_oscillator_demo()
        raw["alpha"] = 1.1
        with patch(
            "gbm_inverse_potential.service.harmonic_oscillator_demo",
            return_value=raw,
        ):
            with self.assertRaisesRegex(CalculationInvariantError, "does not match"):
                run_calculation(CalculationRequest())

    def test_mismatched_core_profile_fails_closed(self) -> None:
        raw = harmonic_oscillator_demo()
        raw["q_points"] = 3999
        with patch(
            "gbm_inverse_potential.service.harmonic_oscillator_demo",
            return_value=raw,
        ):
            with self.assertRaisesRegex(CalculationInvariantError, "fixed work profile"):
                run_calculation(CalculationRequest())


if __name__ == "__main__":
    unittest.main()
