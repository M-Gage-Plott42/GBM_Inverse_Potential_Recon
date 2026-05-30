# Theory Notes

Last updated: 2026-05-30

This public v0 focuses on one transparent path:

1. Use even radial moments to define a spherical form-factor series.
2. Invert the form factor into a reduced radial density.
3. Recover the radial potential from the reduced wavefunction.

For a spherically symmetric normalized density, the public smoke path uses

```text
F(q) = sum_n (-1)^n <r^(2n)> q^(2n) / (2n+1)!
```

and

```text
u(r)^2 = (2/pi) r^2 integral_0^infinity q^2 F(q) j0(qr) dq.
```

The potential smoke path uses the reduced radial equation

```text
[-d^2/dr^2 + V(r)] u(r) = E u(r)
```

so `V(r)=E+u''(r)/u(r)` away from zeros and endpoints.

## Limitations

- The current inverse transform is a direct grid quadrature, not an optimized
  oscillatory quadrature method.
- The public v0 benchmark is analytic and intentionally small.
- Padé selection, production run registries, and broader potential families are
  deferred until separate public-safety review.
