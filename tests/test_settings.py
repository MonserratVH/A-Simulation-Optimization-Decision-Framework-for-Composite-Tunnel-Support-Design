from pathlib import Path

def test_expected_geometry_is_versioned():
    root = Path(__file__).resolve().parents[1]
    assert (root / "data" / "geometry" / "SeccionSMIGTunelVer02a.dxf").exists()
