# Public API

The public API lives in `gbm_inverse_potential`.

## Harmonic-Oscillator Reference Helpers

- `ho_even_moment(power, *, alpha=1.0)`: returns the analytic even radial
  moment for the three-dimensional oscillator ground-state density.
- `ho_reduced_density(r, *, alpha=1.0)`: evaluates the analytic reduced radial
  density `u(r)^2`.
- `ho_form_factor(q, *, alpha=1.0)`: evaluates the analytic spherical form
  factor.
- `ho_potential(r, *, alpha=1.0)`: evaluates the oscillator potential in the
  reduced units used by this artifact.
- `ho_ground_energy(*, alpha=1.0)`: returns the corresponding ground-state
  energy.

## Reconstruction Helpers

- `form_factor_from_even_moments(q, moments)`: evaluates the even-moment
  Taylor form-factor series.
- `inverse_reduced_density(r_grid, q_grid, form_factor_values)`: inverts a
  spherical form factor into `u(r)^2` on a radial grid.
- `reconstruct_potential_from_density(r_grid, reduced_density, *, energy,
  density_floor=1.0e-14)`: reconstructs a radial potential from the reduced
  density through `V(r)=E+u''(r)/u(r)`.
- `harmonic_oscillator_demo(...)`: runs the deterministic public smoke path and
  returns benchmark metrics.

## Minimal Example

```python
import numpy as np

from gbm_inverse_potential import (
    ho_form_factor,
    ho_reduced_density,
    inverse_reduced_density,
)

r_grid = np.linspace(0.02, 4.0, 400)
q_grid = np.linspace(0.0, 16.0, 4000)
reconstructed = inverse_reduced_density(r_grid, q_grid, ho_form_factor(q_grid))
expected = ho_reduced_density(r_grid)
```
