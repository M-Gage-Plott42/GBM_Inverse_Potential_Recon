from __future__ import annotations

import math
import unittest

import numpy as np

from gbm_inverse_potential import (
    form_factor_from_even_moments,
    harmonic_oscillator_demo,
    ho_even_moment,
    ho_form_factor,
    ho_potential,
    ho_reduced_density,
    inverse_reduced_density,
    reconstruct_potential_from_density,
)


class FourierSmokeTests(unittest.TestCase):
    def test_harmonic_oscillator_even_moments(self) -> None:
        self.assertAlmostEqual(ho_even_moment(0), 1.0, places=12)
        self.assertAlmostEqual(ho_even_moment(2), 1.5, places=12)
        self.assertAlmostEqual(ho_even_moment(4), 3.75, places=12)
        with self.assertRaises(ValueError):
            ho_even_moment(3)

    def test_even_moment_series_matches_form_factor_near_origin(self) -> None:
        moments = {power: ho_even_moment(power) for power in range(0, 20, 2)}
        q_grid = np.array([0.0, 0.5, 1.0, 1.5, 2.0])
        series = form_factor_from_even_moments(q_grid, moments)
        expected = ho_form_factor(q_grid)
        self.assertLess(float(np.max(np.abs(series - expected))), 3.0e-7)

    def test_fourier_inverse_recovers_reduced_density(self) -> None:
        r_grid = np.linspace(0.02, 4.0, 400)
        q_grid = np.linspace(0.0, 16.0, 4000)
        density = inverse_reduced_density(r_grid, q_grid, ho_form_factor(q_grid))
        expected = ho_reduced_density(r_grid)
        mask = expected > 1.0e-5
        max_rel = np.max(np.abs(density[mask] - expected[mask]) / expected[mask])
        norm = np.trapezoid(density, r_grid) if hasattr(np, "trapezoid") else np.trapz(density, r_grid)
        self.assertLess(float(max_rel), 1.0e-8)
        self.assertLess(abs(float(norm) - 1.0), 2.0e-5)

    def test_potential_reconstruction_recovers_oscillator_window(self) -> None:
        r_grid = np.linspace(0.02, 4.0, 400)
        density = ho_reduced_density(r_grid)
        potential = reconstruct_potential_from_density(r_grid, density, energy=3.0)
        expected = ho_potential(r_grid)
        mask = (r_grid > 0.3) & (r_grid < 2.5) & np.isfinite(potential)
        max_abs = float(np.max(np.abs(potential[mask] - expected[mask])))
        self.assertLess(max_abs, 1.0e-3)

    def test_demo_metrics_are_small(self) -> None:
        result = harmonic_oscillator_demo()
        self.assertLess(float(result["density_l2_rel"]), 1.0e-8)
        self.assertLess(float(result["potential_l2_rel_window"]), 1.0e-3)
        self.assertTrue(math.isfinite(float(result["density_norm_trapz"])))


if __name__ == "__main__":
    unittest.main()
