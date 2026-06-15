# Examples

The public examples are intentionally small and deterministic.

## Harmonic-Oscillator Demo

```bash
python examples/harmonic_oscillator_demo.py
python -m gbm_inverse_potential.cli --json
```

This runs the reference density inversion and potential reconstruction smoke
path.

## Moment-Series Comparison

```bash
python examples/moment_series_comparison.py --json
```

This compares the even-moment Taylor form-factor approximation with the
analytic oscillator form factor near the origin.

## Alpha Sweep

```bash
python examples/alpha_sweep_smoke.py --json
```

This runs the same public smoke path across a short list of oscillator `alpha`
values and reports the resulting error metrics.

## Public Demo Figure

```bash
python scripts/reproduce_public_demo_figure.py --output /tmp/gbm_public_demo_density.svg
```

This produces the public harmonic-oscillator reduced-density figure. It is not
a paper-figure reproduction claim; see [Figure Provenance](figure_provenance.md).
