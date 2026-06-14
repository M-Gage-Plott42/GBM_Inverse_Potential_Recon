# Public Smoke Benchmark

Last updated: 2026-06-14

This table is validation evidence for the public harmonic-oscillator smoke
demo only. It is not a broad research benchmark and should not be generalized
to the private research stack or unreleased cases.

## Command

```bash
python -m gbm_inverse_potential.cli --json
```

## Configuration

| Parameter | Value |
| --- | ---: |
| `alpha` | `1.0` |
| `r_points` | `400` |
| `q_points` | `4000` |
| `q_max` | `16.0` |

## Observed Metrics

| Metric | Observed value | Public smoke threshold |
| --- | ---: | ---: |
| `density_l2_rel` | `2.73858947190776e-16` | `< 1.0e-8` |
| `density_max_rel_window` | `9.375636558551197e-12` | `< 1.0e-8` |
| `density_norm_trapz` | `0.9999927119194942` | `abs(norm - 1.0) < 2.0e-5` |
| `potential_l2_rel_window` | `9.301565868161147e-05` | `< 1.0e-3` |
| `potential_max_abs_window` | `0.0004660347639350304` | `< 1.0e-3` |

The potential comparison is evaluated on the documented stable radial window,
matching the unit-test and CLI smoke path.
