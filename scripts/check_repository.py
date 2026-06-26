"""Static checks that do not require PLAXIS."""
from pathlib import Path
import ast
import json
import sys

ROOT = Path(__file__).resolve().parents[1]
errors = []
for path in list((ROOT / "src").rglob("*.py")) + list((ROOT / "scripts").glob("*.py")):
    try:
        ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
    except SyntaxError as exc:
        errors.append(f"{path.relative_to(ROOT)}: {exc}")
for path in (ROOT / "notebooks").glob("*.ipynb"):
    try:
        json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        errors.append(f"{path.relative_to(ROOT)}: {exc}")
forbidden_assignments = ("plaxispw=", "plaxispw =")
for path in ROOT.rglob("*"):
    if path.is_file() and path.suffix.lower() in {".py", ".pyw", ".ipynb", ".md", ".txt", ".env"}:
        try:
            text = path.read_text(encoding="utf-8", errors="ignore")
            if path.name != "check_repository.py" and any(token in text.replace(" ", "") for token in ("plaxispw=",)):
                errors.append(f"hard-coded PLAXIS password assignment remains in {path.relative_to(ROOT)}")
        except OSError:
            pass
if errors:
    print("Repository checks failed:")
    print("\n".join(f"- {e}" for e in errors))
    sys.exit(1)
print("Repository static checks passed.")
