# Architecture

```text
DXF geometry + geotechnical parameters
                │
                ▼
      PLAXIS 2D model generation
                │
      staged excavation without support
                │
      convergence–confinement estimate
                │
      composite support installation
                │
      M–N and Q–N capacity verification
                │
      feasible/penalized PSO fitness
                │
                ▼
             CSV results
                │
                ▼
       post-processing and figures
```

The PLAXIS model is intentionally kept close to the validated experimental script because phase, polygon, interface, and node identifiers are model-specific. Configuration and credentials were externalized without changing those scientific assumptions.
