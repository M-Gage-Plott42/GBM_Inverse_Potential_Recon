"""Bounded application service for the public oscillator reconstruction."""

from __future__ import annotations

import math
from dataclasses import dataclass
from numbers import Real

from .fourier import harmonic_oscillator_demo

SCHEMA_VERSION = "1.0"
ALGORITHM_VERSION = "1.0"
CALCULATION_ID = "harmonic-oscillator-inverse-potential"
SOFTWARE_NAME = "gbm-inverse-potential-recon"
QUALITY_GATE_ID = "public-smoke-v1"
ALPHA_MIN = 0.75
ALPHA_MAX = 1.25

DENSITY_L2_REL_MAX = 1.0e-8
DENSITY_MAX_REL_WINDOW_MAX = 1.0e-8
DENSITY_NORM_ERROR_MAX = 5.0e-5
POTENTIAL_L2_REL_WINDOW_MAX = 1.0e-3
POTENTIAL_MAX_ABS_WINDOW_MAX = 1.0e-3


class CalculationInputError(ValueError):
    """Raised when a request is outside the supported public contract."""


class CalculationInvariantError(RuntimeError):
    """Raised when the numerical core violates the service result contract."""


@dataclass(frozen=True, slots=True)
class CalculationRequest:
    """Input accepted by the bounded public calculation service."""

    alpha: float = 1.0

    def __post_init__(self) -> None:
        if isinstance(self.alpha, bool) or not isinstance(self.alpha, Real):
            raise CalculationInputError("alpha must be a finite real number")
        normalized = float(self.alpha)
        if not math.isfinite(normalized):
            raise CalculationInputError("alpha must be a finite real number")
        if not ALPHA_MIN <= normalized <= ALPHA_MAX:
            raise CalculationInputError(
                f"alpha must be between {ALPHA_MIN} and {ALPHA_MAX}, inclusive"
            )
        object.__setattr__(self, "alpha", normalized)


@dataclass(frozen=True, slots=True)
class CalculationProfile:
    """Application-controlled numerical work profile."""

    profile_id: str
    r_min: float
    r_max: float
    r_points: int
    q_min: float
    q_max: float
    q_points: int

    @property
    def grid_work(self) -> int:
        """Return the fixed rectangular kernel-work bound."""

        return self.r_points * self.q_points


PUBLIC_STANDARD_PROFILE = CalculationProfile(
    profile_id="public-standard-v1",
    r_min=0.02,
    r_max=4.0,
    r_points=400,
    q_min=0.0,
    q_max=16.0,
    q_points=4000,
)


@dataclass(frozen=True, slots=True)
class CalculationResult:
    """Deterministic scalar result and provenance for one service request."""

    alpha: float
    density_l2_rel: float
    density_max_rel_window: float
    density_norm_trapz: float
    potential_l2_rel_window: float
    potential_max_abs_window: float

    def to_dict(self) -> dict[str, object]:
        """Return the versioned JSON-compatible service representation."""

        profile = PUBLIC_STANDARD_PROFILE
        return {
            "schema_version": SCHEMA_VERSION,
            "calculation": {
                "id": CALCULATION_ID,
                "algorithm_version": ALGORITHM_VERSION,
                "software": {"name": SOFTWARE_NAME},
            },
            "input": {"alpha": self.alpha},
            "units": {
                "system": "reduced",
                "hbar_squared_over_2m": 1.0,
                "alpha": "inverse_reduced_length_squared",
                "potential": "reduced_energy",
            },
            "profile": {
                "id": profile.profile_id,
                "r_min": profile.r_min,
                "r_max": profile.r_max,
                "r_points": profile.r_points,
                "q_min": profile.q_min,
                "q_max": profile.q_max,
                "q_points": profile.q_points,
                "grid_work": profile.grid_work,
            },
            "metrics": {
                "density_l2_rel": self.density_l2_rel,
                "density_max_rel_window": self.density_max_rel_window,
                "density_norm_trapz": self.density_norm_trapz,
                "potential_l2_rel_window": self.potential_l2_rel_window,
                "potential_max_abs_window": self.potential_max_abs_window,
            },
            "quality_gate": QUALITY_GATE_ID,
            "limitations": [
                "harmonic_oscillator_ground_state_only",
                "analytic_form_factor_input",
                "finite_difference_stable_window_only",
            ],
        }

    def legacy_metrics(self) -> dict[str, float | int]:
        """Project the service result into the established flat CLI shape."""

        profile = PUBLIC_STANDARD_PROFILE
        return {
            "alpha": self.alpha,
            "r_points": profile.r_points,
            "q_points": profile.q_points,
            "q_max": profile.q_max,
            "density_l2_rel": self.density_l2_rel,
            "density_max_rel_window": self.density_max_rel_window,
            "density_norm_trapz": self.density_norm_trapz,
            "potential_l2_rel_window": self.potential_l2_rel_window,
            "potential_max_abs_window": self.potential_max_abs_window,
        }


def _metric(payload: dict[str, float | int], key: str) -> float:
    try:
        raw_value = payload[key]
        if isinstance(raw_value, bool) or not isinstance(raw_value, Real):
            raise TypeError
        value = float(raw_value)
    except (KeyError, TypeError, ValueError) as exc:
        raise CalculationInvariantError(
            f"calculation result is missing finite metric {key}"
        ) from exc
    if not math.isfinite(value):
        raise CalculationInvariantError(
            f"calculation result is missing finite metric {key}"
        )
    return value


def _enforce_quality(result: CalculationResult) -> None:
    failures: list[str] = []
    if not 0.0 <= result.density_l2_rel < DENSITY_L2_REL_MAX:
        failures.append("density_l2_rel")
    if not 0.0 <= result.density_max_rel_window < DENSITY_MAX_REL_WINDOW_MAX:
        failures.append("density_max_rel_window")
    if abs(result.density_norm_trapz - 1.0) >= DENSITY_NORM_ERROR_MAX:
        failures.append("density_norm_trapz")
    if not 0.0 <= result.potential_l2_rel_window < POTENTIAL_L2_REL_WINDOW_MAX:
        failures.append("potential_l2_rel_window")
    if not 0.0 <= result.potential_max_abs_window < POTENTIAL_MAX_ABS_WINDOW_MAX:
        failures.append("potential_max_abs_window")
    if failures:
        raise CalculationInvariantError("calculation failed quality gate: " + ", ".join(failures))


def run_calculation(request: CalculationRequest) -> CalculationResult:
    """Run one bounded deterministic harmonic-oscillator reconstruction."""

    if not isinstance(request, CalculationRequest):
        raise CalculationInputError("request must be a CalculationRequest")
    profile = PUBLIC_STANDARD_PROFILE
    raw = harmonic_oscillator_demo(
        alpha=request.alpha,
        r_min=profile.r_min,
        r_max=profile.r_max,
        r_points=profile.r_points,
        q_max=profile.q_max,
        q_points=profile.q_points,
    )
    observed_profile = (
        _metric(raw, "r_points"),
        _metric(raw, "q_points"),
        _metric(raw, "q_max"),
    )
    expected_profile = (
        float(profile.r_points),
        float(profile.q_points),
        profile.q_max,
    )
    if observed_profile != expected_profile:
        raise CalculationInvariantError(
            "calculation result profile does not match the fixed work profile"
        )
    result = CalculationResult(
        alpha=_metric(raw, "alpha"),
        density_l2_rel=_metric(raw, "density_l2_rel"),
        density_max_rel_window=_metric(raw, "density_max_rel_window"),
        density_norm_trapz=_metric(raw, "density_norm_trapz"),
        potential_l2_rel_window=_metric(raw, "potential_l2_rel_window"),
        potential_max_abs_window=_metric(raw, "potential_max_abs_window"),
    )
    if result.alpha != request.alpha:
        raise CalculationInvariantError(
            "calculation result alpha does not match the normalized request"
        )
    _enforce_quality(result)
    return result
