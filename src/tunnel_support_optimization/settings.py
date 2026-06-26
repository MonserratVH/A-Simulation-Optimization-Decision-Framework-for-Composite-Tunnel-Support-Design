"""Configuration loading and validation for the PLAXIS workflow."""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import os

try:
    from dotenv import load_dotenv
except ImportError:  # pragma: no cover
    load_dotenv = None


PROJECT_ROOT = Path(__file__).resolve().parents[2]
if load_dotenv is not None:
    load_dotenv(PROJECT_ROOT / ".env")


def _env_path(name: str, default: Path) -> Path:
    raw = os.getenv(name)
    return Path(raw).expanduser().resolve() if raw else default.resolve()


@dataclass(frozen=True)
class Settings:
    project_root: Path = PROJECT_ROOT
    plaxis_home: Path = _env_path(
        "PLAXIS_HOME", Path(r"C:\Program Files\Seequent\PLAXIS 2D 2023.2")
    )
    plaxis_password: str = os.getenv("PLAXIS_PASSWORD", "")
    input_port: int = int(os.getenv("PLAXIS_INPUT_PORT", "10000"))
    output_port: int = int(os.getenv("PLAXIS_OUTPUT_PORT", "10001"))
    input_executable: str = os.getenv("PLAXIS_INPUT_EXECUTABLE", "Plaxis2DXInput.exe")
    output_executable: str = os.getenv("PLAXIS_OUTPUT_EXECUTABLE", "Plaxis2DOutput.exe")
    topography_dxf: Path = _env_path(
        "PLAXIS_TOPOGRAPHY_DXF", PROJECT_ROOT / "data" / "geometry" / "SeccionSMIG.dxf"
    )
    tunnel_section_dxf: Path = _env_path(
        "PLAXIS_TUNNEL_DXF", PROJECT_ROOT / "data" / "geometry" / "SeccionSMIGTunelVer02a.dxf"
    )
    results_dir: Path = _env_path("RESULTS_DIR", PROJECT_ROOT / "results")
    figures_dir: Path = _env_path("FIGURES_DIR", PROJECT_ROOT / "figures")

    def validate(self, *, require_geometry: bool = True) -> None:
        errors: list[str] = []
        if not self.plaxis_password:
            errors.append("PLAXIS_PASSWORD is not defined in .env")
        if not self.plaxis_home.exists():
            errors.append(f"PLAXIS_HOME does not exist: {self.plaxis_home}")
        if require_geometry and not self.topography_dxf.exists():
            errors.append(f"Topography DXF not found: {self.topography_dxf}")
        if require_geometry and not self.tunnel_section_dxf.exists():
            errors.append(f"Tunnel-section DXF not found: {self.tunnel_section_dxf}")
        if errors:
            raise RuntimeError("Configuration error:\n- " + "\n- ".join(errors))
        self.results_dir.mkdir(parents=True, exist_ok=True)
        self.figures_dir.mkdir(parents=True, exist_ok=True)


settings = Settings()
