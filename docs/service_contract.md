# Deterministic Calculation Service Contract

Last updated: 2026-08-10

## Scope

The package exposes a bounded, framework-neutral Python application service for
the existing harmonic-oscillator inverse-potential reconstruction. The core in
`service.py` does not start a network listener. The optional FastAPI adapter in
`http_api.py` maps one local HTTP request to this core, and the Dockerfile
packages that adapter for local evidence. Neither layer is a cloud deployment,
public endpoint, published image, or monitored-service claim.

## Request

`CalculationRequest` accepts one value:

- `alpha`: a finite real number in the inclusive interval `0.75` through
  `1.25`.

Booleans, strings, NaN, infinities, and values outside the interval fail with
`CalculationInputError`. The request exposes no file, upload, raw-array,
grid-size, or arbitrary calculation input.

The HTTP adapter preserves the same one-field boundary, rejects query controls,
and limits the request body to 1 KiB before validation. Its exact routes and
failure behavior are defined in
[Local HTTP And Container Contract](http_container_contract.md).

## Fixed Work Profile

`run_calculation()` always uses `public-standard-v1`:

| Field | Value |
| --- | ---: |
| `r_min` | `0.02` |
| `r_max` | `4.0` |
| `r_points` | `400` |
| `q_min` | `0.0` |
| `q_max` | `16.0` |
| `q_points` | `4000` |
| `grid_work` | `1600000` |

The existing CLI retains its grid flags and broader alpha behavior for local
exploratory compatibility. Those legacy controls are not fields in
`CalculationRequest`, do not receive the service quality guarantee, and are not
fields in the HTTP request model. The bounded service path always uses the
fixed profile above.

## Result

`CalculationResult.to_dict()` returns a JSON-compatible versioned object with:

- calculation, algorithm, and software-name identity;
- normalized input;
- reduced-unit context where `hbar^2/(2m)=1`;
- the exact fixed work profile;
- density and potential reconstruction metrics;
- quality-gate identity; and
- narrow scientific limitation codes.

The result deliberately excludes timestamps, timing, request identifiers,
hostnames, paths, environment details, random values, uploads, and stored input.
The service code is unreleased. Its result therefore does not report the
released package version `0.2.0` as though that artifact contained Gate 1.
Schema and algorithm versions identify this contract independently; the exact
source commit is the review and reproduction authority until a separate release
is approved.

## Quality Gate

Every service result must satisfy:

- `density_l2_rel < 1.0e-8`;
- `density_max_rel_window < 1.0e-8`;
- `abs(density_norm_trapz - 1.0) < 5.0e-5` across the supported alpha interval;
- `potential_l2_rel_window < 1.0e-3`; and
- `potential_max_abs_window < 1.0e-3`.

An internal non-finite, missing, mismatched, or out-of-tolerance result fails
closed with `CalculationInvariantError`.

The established `alpha=1.0` public benchmark retains its tighter documented
density-normalization threshold of `2.0e-5`.

### Metric definitions

- `density_l2_rel` is the relative L2 error between reconstructed and analytic
  reduced density across the full standard radial grid.
- `density_max_rel_window` is the maximum pointwise relative density error
  where the analytic reduced density is greater than `1.0e-5`.
- `density_norm_trapz` is the trapezoidal integral of reconstructed reduced
  density across the full standard radial grid.
- `potential_l2_rel_window` is the relative L2 error between reconstructed and
  analytic potential where `0.3 < r < 2.5` and the reconstructed potential is
  finite.
- `potential_max_abs_window` is the maximum absolute potential error over that
  same finite `0.3 < r < 2.5` window.

The service returns these scalar validation metrics, not the underlying grids
or arrays.

The supported interval was characterized at 101 evenly spaced values on the
fixed profile. The observed worst density-normalization error was `2.938e-5`
at `alpha=0.75`; the worst potential maximum absolute error was `7.160e-4` at
`alpha=1.25`. Both retain margin under the service thresholds. Values outside
the contract lose that margin: lower probes fail the finite-domain
normalization ceiling and `alpha=1.5` exceeds the potential maximum-absolute
error ceiling.

## Direct Local Use

```python
from gbm_inverse_potential import CalculationRequest, run_calculation

request = CalculationRequest(alpha=1.0)
result = run_calculation(request)
payload = result.to_dict()
print(payload["metrics"])
```

For the established flat CLI output:

```bash
python -m gbm_inverse_potential.cli --json
```

## Determinism And Limits

The same normalized request in the same dependency environment produces the
same normalized scientific result. Tests require repeat-call equality on the
review environment and numerical thresholds across the supported interval.
Cross-platform floating-point implementations may differ in their last bits,
so portability is governed by scientific tolerances rather than a universal
byte-for-byte promise.

This contract is limited to the analytic harmonic-oscillator ground-state form
factor and the documented finite-difference stable window. It is not a general
input solver, file-processing service, performance benchmark, or private GBM
research interface.
