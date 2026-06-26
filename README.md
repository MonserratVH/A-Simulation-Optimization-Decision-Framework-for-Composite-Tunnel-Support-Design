## Composite Tunnel-Support Optimization with PLAXIS 2D and PSO

Research software for the numerical analysis and optimization of composite tunnel-support systems formed by shotcrete and steel sets. The project integrates PLAXIS 2D remote scripting, staged finite-element analysis, Particle Swarm Optimization (PSO), structural capacity verification, and result visualization in a reproducible computational workflow.


## Project overview

This research project addresses the selection of composite support configurations for road tunnels excavated in rock masses. The proposed workflow evaluates combinations of shotcrete thickness and steel-set profiles under different geotechnical conditions, with the objective of reducing crown displacement while maintaining structural safety.

For each candidate configuration, the software:

1. builds and executes a staged two-dimensional tunnel model in PLAXIS 2D;
2. calculates the equivalent axial and flexural stiffness of the composite support;
3. redistributes moment, thrust, and shear between the steel sets and shotcrete;
4. verifies the structural demand against M–N and Q–N capacity envelopes;
5. applies a factor of safety of 1.5;
6. records feasible and non-feasible alternatives; and
7. supports comparative analysis through CSV outputs and two- and three-dimensional visualizations.

The optimization stage explores shotcrete thicknesses and a catalog of 40 steel profiles using PSO. The resulting set of feasible alternatives can subsequently support engineering comparison and multicriteria decision-making.

## Scientific scope

The model evaluates combinations of shotcrete thickness and one of 40 steel profiles. For each candidate, it calculates equivalent plate properties, executes the staged tunnel model, redistributes moment, thrust, and shear between steel and shotcrete, and verifies M–N and Q–N capacity envelopes at a factor of safety of 1.5. Feasible alternatives are ranked using crown displacement within the PSO fitness value.

## Researchers

- **José Miguel León Ruiz** — ORCID: [0009-0000-2376-9486](https://orcid.org/0009-0000-2376-9486)
- **Carlos Chávez Negrete** — ORCID: [0000-0002-3932-6943](https://orcid.org/0000-0002-3932-6943)
- **José Eleazar Arreygue Rocha** — ORCID: [0000-0002-5889-7661](https://orcid.org/0000-0002-5889-7661)
- **Francisco Domínguez Mota** — ORCID: [0000-0001-6837-172X](https://orcid.org/0000-0001-6837-172X)
- **Monserrat Vázquez-Hernández** — ORCID: [0000-0001-9206-5706](https://orcid.org/0000-0001-9206-5706)
- **Luis Alberto Morales Rosales** — ORCID: [0000-0002-4753-9375](https://orcid.org/0000-0002-4753-9375)

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

## Reference environment used in the project

The research project was developed and tested using the following environment:

| Component | Reported version or configuration |
|---|---|
| Operating system | Windows |
| PLAXIS 2D | 2023.2.1.1079 |
| Python | 3.8.1 |
| Jupyter Notebook server | 6.4.11 |
| IPython kernel | 8.12.1 |
| PLAXIS Input remote-scripting port | 10000 |
| PLAXIS Output remote-scripting port | 10001 in the supplied source code |
| Processor | Intel Xeon E3-1240 v5 @ 3.5 GHz |
| Memory | 8 GB RAM |

The processor and memory values describe the original experimental machine; they are not strict installation requirements. Runtime increases substantially with the number of PSO particles and iterations.

## Software prerequisites

- Windows.
- A valid, licensed installation of **PLAXIS 2D 2023.2**. The exact build used in the project is **2023.2.1.1079**.
- PLAXIS Input and Output with Remote Scripting enabled.
- Python **3.8.x**. For the closest reproduction of the original project environment, use **Python 3.8.1**.
- The geometry files:
  - `SeccionSMIG.dxf`
  - `SeccionSMIGTunelVer02a.dxf`

## Python dependencies

The project uses the following libraries:

| Package or module | Purpose | Installation source |
|---|---|---|
| `plxscripting` | PLAXIS Input/Output remote scripting | Supplied by the PLAXIS installation; do not install from PyPI |
| `pyswarms` | Particle Swarm Optimization | `requirements.txt` |
| `numpy` | Numerical arrays and calculations | `requirements.txt` |
| `pandas` | CSV input/output and tabular processing | `requirements.txt` |
| `matplotlib` | Two-dimensional plots and capacity envelopes | `requirements.txt` |
| `plotly` | Interactive three-dimensional result plots | `requirements.txt` |
| `kaleido` | Static image export for Plotly | `requirements.txt` |
| `shapely` | Point-in-polygon checks for structural capacity envelopes | `requirements.txt` |
| `easygui` | Legacy dialogs used by the supplied scripts | `requirements.txt` |
| `PySide2` | PLAXIS capacity-tool graphical interface | Normally supplied by the PLAXIS Python runtime |
| `py_package_decryptor` | Internal dependency of the supplied PLAXIS utility | Supplied by PLAXIS |
| `python-dotenv` | Local configuration without publishing credentials | `requirements.txt` |
| `PyYAML` | Experiment configuration files | `requirements.txt` |
| `notebook` | Notebook server matching the project environment | `requirements.txt` |
| `ipython` | Kernel matching the project environment | `requirements.txt` |

The standard-library modules `os`, `sys`, `subprocess`, `time`, `json`, `random`, and `math` require no separate installation.

## Installation

### 1. Install PLAXIS 2D

Install and license PLAXIS 2D 2023.2 on Windows. The default path used by the repository is:

```text
C:\Program Files\Seequent\PLAXIS 2D 2023.2
```

A different installation directory can be supplied through `PLAXIS_HOME` in `.env`.

### 2. Create the Python environment

For the closest match to the original project environment, create the environment with Python 3.8.1:

```powershell
py -3.8 -m venv .venv
.venv\Scripts\activate
python -m pip install --upgrade pip
pip install -r requirements.txt
pip install -e .
copy .env.example .env
```

### 3. Configure PLAXIS Remote Scripting

The repository launches PLAXIS Input and Output using their application-server arguments. Confirm that:

1. Remote Scripting is allowed by the PLAXIS installation and license.
2. The password in `.env` is a new local password and matches the password used for the PLAXIS servers.
3. Ports `10000` and `10001` are available locally.
4. Windows Firewall does not block the local Input and Output server processes.

The default configuration is:

```dotenv
PLAXIS_HOME=C:\Program Files\Seequent\PLAXIS 2D 2023.2
PLAXIS_PASSWORD=replace_with_a_new_remote_scripting_password
PLAXIS_INPUT_PORT=10000
PLAXIS_OUTPUT_PORT=10001
PLAXIS_INPUT_EXECUTABLE=Plaxis2DXInput.exe
PLAXIS_OUTPUT_EXECUTABLE=Plaxis2DOutput.exe
PLAXIS_TOPOGRAPHY_DXF=data\geometry\SeccionSMIG.dxf
PLAXIS_TUNNEL_DXF=data\geometry\SeccionSMIGTunelVer02a.dxf
RESULTS_DIR=results
FIGURES_DIR=figures
```

Never commit `.env` or any real password.

### 4. Make the PLAXIS Python modules available

`plxscripting`, `PySide2`, and `py_package_decryptor` are tied to the PLAXIS installation. The maintained launcher searches the PLAXIS installation configured by `PLAXIS_HOME`. If these modules are not importable from the virtual environment, run the workflow through the Python environment bundled with PLAXIS or add the corresponding PLAXIS `tools\pythonlib` directory to `PYTHONPATH`.

The original support-capacity utilities are retained in:

```text
vendor/plaxis_support_capacity/
```

They may also be executed manually from PLAXIS through:

```text
Expert > Run Python script > Open...
```

The original Bentley instructions are preserved in `vendor/plaxis_support_capacity/README.md`.

### 5. Add the geometry files

Place the required geometry files in:

```text
data\geometry\SeccionSMIG.dxf
data\geometry\SeccionSMIGTunelVer02a.dxf
```

## Running the experiment

From a Windows command prompt with the virtual environment activated:

```bat
scripts\run_pso.bat
```

The scientific parameters in `scripts/run_pso_legacy.py` are preserved from the supplied experiment. Inspect the number of particles and iterations before starting because every objective-function evaluation executes a PLAXIS calculation. The project considers PSO experiments based on 10 particles and 20, 40, or 60 iterations, corresponding to 200, 400, and 600 evaluations.

## Running the notebooks

The project uses Jupyter Notebook server 6.4.11 and IPython 8.12.1. After installation:

```powershell
jupyter notebook
```

Open the notebooks in `notebooks/`. These notebooks are retained as experimental records; the maintained command-line workflow is the preferred execution path.

## Static validation without PLAXIS

```powershell
python scripts/check_repository.py
pytest
```

These checks validate Python syntax, notebook JSON, expected files, and accidental inclusion of the removed password. They do not validate the numerical model or PLAXIS API compatibility.

## Expected inputs and outputs

Inputs include:

- topographic geometry (`SeccionSMIG.dxf`);
- tunnel cross-section (`SeccionSMIGTunelVer02a.dxf`);
- geotechnical parameters such as `Erm`, `GSI`, `mi`, `D`, and unit weight;
- shotcrete mechanical properties and thickness bounds;
- the catalog of 40 steel profiles;
- PSO particles, iterations, inertia, and acceleration coefficients.

Generated outputs include:

- CSV files with candidate configurations, equivalent properties, crown displacement, and structural-feasibility values;
- two-dimensional comparison plots;
- three-dimensional Plotly plots;
- capacity-envelope visualizations.

Generated CSV and image files are written to `results/` and `figures/` and are excluded from version control by default.

## Model-specific limitations

The PLAXIS automation uses generated identifiers for polygons, interfaces, plates, phases, and a crown node. Those identifiers are sensitive to geometry, mesh, PLAXIS version, and construction sequence. See `docs/REPRODUCIBILITY.md` before changing any of them.

The exact numerical results also depend on the PLAXIS build, mesh generation, stochastic PSO initialization, geometry files, and the availability of the same material and phase definitions. A successful installation therefore does not by itself guarantee bit-for-bit reproduction.

## Licensing

The original PLAXIS support-capacity utilities and adapted derivative routines are governed by the **Plaxis Public License**. See `LICENSES/PPL-1.0.txt` and `docs/THIRD_PARTY_NOTICES.md`. PLAXIS itself is proprietary software and is not included.

## Citation

Citation metadata is provided in `CITATION.cff`. Cite the associated paper in addition to the software repository.
