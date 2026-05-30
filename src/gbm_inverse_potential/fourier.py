"""Fourier/form-factor smoke path for inverse radial reconstruction.

The implementation is intentionally small and deterministic. It reconstructs a
reduced radial density from a spherical form factor and then reconstructs a
radial potential from the resulting ground-state reduced wavefunction.
"""

from __future__ import annotations

import math
from typing import Mapping

import numpy as np
from numpy.typing import ArrayLike, NDArray


def _as_float_array(values: ArrayLike) -> NDArray[np.float64]:
    return np.asarray(values, dtype=float)


def ho_even_moment(power: int, *, alpha: float = 1.0) -> float:
    """Return <r**power> for the 3D oscillator ground-state density.

    The density is normalized as 4*pi*r**2*rho_3d(r), with
    rho_3d(r) = (alpha/pi)**(3/2) * exp(-alpha*r**2).
    """

    if power < 0 or power % 2 != 0:
        raise ValueError("power must be a nonnegative even integer")
    if alpha <= 0:
        raise ValueError("alpha must be positive")
    n = power // 2
    return 2.0 * math.gamma(n + 1.5) / math.sqrt(math.pi) * alpha ** (-n)


def ho_reduced_density(r: ArrayLike, *, alpha: float = 1.0) -> NDArray[np.float64]:
    """Analytic reduced radial density u(r)**2 for the 3D oscillator."""

    if alpha <= 0:
        raise ValueError("alpha must be positive")
    r_arr = _as_float_array(r)
    prefactor = 4.0 * alpha**1.5 / math.sqrt(math.pi)
    return prefactor * r_arr**2 * np.exp(-alpha * r_arr**2)


def ho_form_factor(q: ArrayLike, *, alpha: float = 1.0) -> NDArray[np.float64]:
    """Analytic spherical form factor for the oscillator density."""

    if alpha <= 0:
        raise ValueError("alpha must be positive")
    q_arr = _as_float_array(q)
    return np.exp(-(q_arr**2) / (4.0 * alpha))


def ho_potential(r: ArrayLike, *, alpha: float = 1.0) -> NDArray[np.float64]:
    """Analytic oscillator potential in units where hbar**2/(2m)=1."""

    if alpha <= 0:
        raise ValueError("alpha must be positive")
    r_arr = _as_float_array(r)
    return alpha**2 * r_arr**2


def ho_ground_energy(*, alpha: float = 1.0) -> float:
    """Ground-state energy for V(r)=alpha**2*r**2 in reduced units."""

    if alpha <= 0:
        raise ValueError("alpha must be positive")
    return 3.0 * alpha


def form_factor_from_even_moments(
    q: ArrayLike,
    moments: Mapping[int, float],
) -> NDArray[np.float64]:
    """Evaluate the even-moment Taylor form-factor series.

    F(q) = sum_n (-1)**n * <r**(2n)> * q**(2n) / (2n+1)!.
    """

    q_arr = _as_float_array(q)
    total = np.zeros_like(q_arr, dtype=float)
    for power, moment in sorted(moments.items()):
        if power < 0 or power % 2 != 0:
            raise ValueError("moment keys must be nonnegative even powers")
        n = power // 2
        total = total + ((-1.0) ** n) * float(moment) * q_arr**power / math.factorial(power + 1)
    return total


def _integrate_trapezoid(y: ArrayLike, x: ArrayLike) -> float:
    if hasattr(np, "trapezoid"):
        return float(np.trapezoid(y, x))
    return float(np.trapz(y, x))


def _spherical_j0(x: NDArray[np.float64]) -> NDArray[np.float64]:
    out = np.ones_like(x, dtype=float)
    mask = np.abs(x) > 1.0e-12
    out[mask] = np.sin(x[mask]) / x[mask]
    return out


def inverse_reduced_density(
    r_grid: ArrayLike,
    q_grid: ArrayLike,
    form_factor_values: ArrayLike,
) -> NDArray[np.float64]:
    """Invert a spherical form factor into reduced density u(r)**2.

    The normalization is u(r)**2 = (2/pi) * r**2 * integral q**2 F(q) j0(qr) dq.
    """

    r_arr = _as_float_array(r_grid)
    q_arr = _as_float_array(q_grid)
    f_arr = _as_float_array(form_factor_values)
    if q_arr.ndim != 1 or r_arr.ndim != 1:
        raise ValueError("r_grid and q_grid must be one-dimensional")
    if f_arr.shape != q_arr.shape:
        raise ValueError("form_factor_values must have the same shape as q_grid")
    if len(q_arr) < 3 or len(r_arr) < 3:
        raise ValueError("grids must contain at least three points")

    density = np.empty_like(r_arr, dtype=float)
    for idx, r_val in enumerate(r_arr):
        qr = q_arr * r_val
        integrand = q_arr**2 * f_arr * _spherical_j0(qr)
        density[idx] = (2.0 / math.pi) * r_val**2 * _integrate_trapezoid(integrand, q_arr)
    return density


def reconstruct_potential_from_density(
    r_grid: ArrayLike,
    reduced_density: ArrayLike,
    *,
    energy: float,
    density_floor: float = 1.0e-14,
) -> NDArray[np.float64]:
    """Reconstruct V(r)=E+u''(r)/u(r) from reduced density u(r)**2."""

    r_arr = _as_float_array(r_grid)
    rho_arr = _as_float_array(reduced_density)
    if r_arr.shape != rho_arr.shape:
        raise ValueError("r_grid and reduced_density must have the same shape")
    if len(r_arr) < 5:
        raise ValueError("at least five grid points are required")

    u = np.sqrt(np.clip(rho_arr, 0.0, None))
    du = np.gradient(u, r_arr, edge_order=2)
    d2u = np.gradient(du, r_arr, edge_order=2)
    potential = np.full_like(r_arr, np.nan, dtype=float)
    mask = u > density_floor
    potential[mask] = float(energy) + d2u[mask] / u[mask]
    return potential


def relative_l2(observed: ArrayLike, expected: ArrayLike) -> float:
    obs = _as_float_array(observed)
    exp = _as_float_array(expected)
    denom = float(np.linalg.norm(exp))
    if denom == 0.0:
        return float(np.linalg.norm(obs - exp))
    return float(np.linalg.norm(obs - exp) / denom)


def harmonic_oscillator_demo(
    *,
    alpha: float = 1.0,
    r_min: float = 0.02,
    r_max: float = 4.0,
    r_points: int = 400,
    q_max: float = 16.0,
    q_points: int = 4000,
) -> dict[str, float | int]:
    """Run the deterministic oscillator reconstruction smoke demo."""

    r_grid = np.linspace(r_min, r_max, r_points)
    q_grid = np.linspace(0.0, q_max, q_points)
    form_factor = ho_form_factor(q_grid, alpha=alpha)
    density = inverse_reduced_density(r_grid, q_grid, form_factor)
    expected_density = ho_reduced_density(r_grid, alpha=alpha)

    potential = reconstruct_potential_from_density(
        r_grid,
        density,
        energy=ho_ground_energy(alpha=alpha),
    )
    expected_potential = ho_potential(r_grid, alpha=alpha)

    density_mask = expected_density > 1.0e-5
    potential_mask = (r_grid > 0.3) & (r_grid < 2.5) & np.isfinite(potential)

    density_max_rel = float(
        np.max(np.abs(density[density_mask] - expected_density[density_mask]) / expected_density[density_mask])
    )
    potential_l2 = relative_l2(potential[potential_mask], expected_potential[potential_mask])
    potential_max_abs = float(np.max(np.abs(potential[potential_mask] - expected_potential[potential_mask])))

    return {
        "alpha": float(alpha),
        "r_points": int(r_points),
        "q_points": int(q_points),
        "q_max": float(q_max),
        "density_l2_rel": relative_l2(density, expected_density),
        "density_max_rel_window": density_max_rel,
        "density_norm_trapz": _integrate_trapezoid(density, r_grid),
        "potential_l2_rel_window": potential_l2,
        "potential_max_abs_window": potential_max_abs,
    }
