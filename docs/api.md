# Public Python And Local HTTP APIs

The public API lives in `gbm_inverse_potential`.

## Bounded Calculation Service

- `CalculationRequest(alpha=1.0)`: validates a finite `alpha` in the inclusive
  interval `0.75` through `1.25`.
- `run_calculation(request)`: evaluates the fixed `public-standard-v1` work
  profile and returns `CalculationResult`.
- `CalculationResult.to_dict()`: returns the versioned JSON-compatible service
  representation.
- `CalculationResult.legacy_metrics()`: projects the standard result into the
  established flat CLI metric shape.
- `CalculationInputError`: identifies unsupported request input.
- `CalculationInvariantError`: identifies a missing, non-finite, mismatched, or
  out-of-tolerance internal result.

See [Service Contract](service_contract.md) for the exact profile, schema,
quality gate, and non-goals.

## Local HTTP Adapter

Install the optional `service` extra before importing
`gbm_inverse_potential.http_api`. The adapter exposes:

- `POST /v1/reconstruct` with exactly one required `alpha` number;
- `GET /health/live` and `GET /health/ready`;
- `GET /version` with unreleased source status; and
- generated OpenAPI at `/openapi.json` plus local Swagger UI at `/docs`.

The adapter reuses `CalculationResult.to_dict()` as its typed success schema.
It rejects extra/query work controls, uploads, non-JSON/encoded or oversized
bodies, and simultaneous calculations. Invalid, busy, invariant, and
unexpected failures return generic `4xx`/`5xx` responses. See
[Local HTTP And Container Contract](http_container_contract.md) for exact
limits and status behavior.

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
