# A Simulation Optimization Decision Framework for Composite Tunnel Support Design Using FEM, Particle Swarm Optimization, and Multi-Criteria Decision-Making


## Composite Tunnel-Support Optimization with PLAXIS 2D and PSO

Research software for exploring composite tunnel-support configurations formed by shotcrete and steel sets. The workflow links PLAXIS 2D remote scripting, staged finite-element analysis, Particle Swarm Optimization (PSO), structural capacity checks, and result visualization.

## Scientific scope

The model evaluates combinations of shotcrete thickness and one of 40 steel profiles. For each candidate, it calculates equivalent plate properties, executes the staged tunnel model, redistributes moment, thrust, and shear between steel and shotcrete, and verifies M–N and Q–N capacity envelopes at a factor of safety of 1.5. Feasible alternatives are ranked using crown displacement within the PSO fitness value.

## Repository structure

```text
config/                         experiment template
data/geometry/                  DXF geometry
data/input/                     steel-profile catalog and names
docs/                           architecture, reproducibility, licenses
notebooks/                      historical experimental notebooks
scripts/run_pso.bat             Windows entry point
scripts/run_pso_legacy.py       preserved experimental PSO driver
src/tunnel_support_optimization/ maintained configuration and PLAXIS model
vendor/plaxis_support_capacity/ original PLAXIS capacity tools
results/                        generated CSV files (not versioned)
figures/                        generated figures (not versioned)
```

## Important prerequisites

- Windows and a licensed installation of **PLAXIS 2D 2023.2**.
- Remote scripting enabled for PLAXIS Input and Output.
- Python **3.8.x**.
- The topographic file `SeccionSMIG.dxf`, which was referenced by the supplied model but was not included in the source files.

The repository includes `SeccionSMIGTunelVer02a.dxf`, but the model cannot be reproduced numerically until the missing topographic DXF is placed in `data/geometry/`.

## Installation

```powershell
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
pip install -e .
copy .env.example .env
```

Edit `.env` and provide a **new** PLAXIS remote-scripting password. Do not reuse or publish the password that existed in the original research script.

## Configuration

At minimum, verify:

```dotenv
PLAXIS_HOME=C:\Program Files\Seequent\PLAXIS 2D 2023.2
PLAXIS_PASSWORD=your_new_password
PLAXIS_TOPOGRAPHY_DXF=data\geometry\SeccionSMIG.dxf
PLAXIS_TUNNEL_DXF=data\geometry\SeccionSMIGTunelVer02a.dxf
```

## Running the experiment

From a Windows command prompt:

```bat
scripts\run_pso.bat
```

The scientific parameters in `scripts/run_pso_legacy.py` are preserved from the supplied experiment. Inspect particle and iteration values before starting, because each objective-function evaluation launches an expensive PLAXIS calculation.

## Static validation without PLAXIS

```powershell
python scripts/check_repository.py
pytest
```

These checks validate Python syntax, notebook JSON, expected files, and accidental inclusion of the removed password. They do not validate the numerical model.

## Model-specific limitations

The PLAXIS automation uses generated identifiers for polygons, interfaces, plates, phases, and a crown node. Those identifiers are sensitive to geometry, mesh, PLAXIS version, and construction sequence. See `docs/REPRODUCIBILITY.md` before changing any of them.

## Licensing

The original PLAXIS support-capacity utilities and adapted derivative routines are governed by the **Plaxis Public License**. See `LICENSES/PPL-1.0.txt` and `docs/THIRD_PARTY_NOTICES.md`. PLAXIS itself is proprietary software and is not included.

## Citation

Citation metadata is provided in `CITATION.cff`. Cite the associated paper in addition to the software repository.
