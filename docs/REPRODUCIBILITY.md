# Reproducibility notes

## Exact prerequisites

- Windows.
- Licensed PLAXIS 2D 2023.2, matching the supplied experimental environment.
- PLAXIS Remote Scripting enabled.
- Python 3.8.x.
- The missing topographic geometry `SeccionSMIG.dxf`.

## Model-specific assumptions

The current implementation references PLAXIS-generated object names such as `Polygon_1_1`, `NegativeInterface_13_1`, `Plate_10_1`, phases `Phase_3` and `Phase_7`, and node `7889`. These identifiers depend on the imported geometry, mesh, PLAXIS version, and construction sequence. Changing geometry or meshing can invalidate them.

## Stochastic behavior

The steel profile is selected randomly within each objective-function evaluation. For strict repeatability, add a controlled NumPy seed and record it with each experiment. The supplied scientific script did not fix a seed, so its original behavior is preserved.

## Validation boundary

Static syntax and repository checks can run without PLAXIS. Numerical validation requires the licensed application and original geometry; it was not possible in the packaging environment.
