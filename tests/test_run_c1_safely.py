import subprocess
import sys
from pathlib import Path


def test_run_c1_safely_help():
    script = Path(__file__).resolve().parent.parent / "tools" / "run_c1_safely.py"
    result = subprocess.run([sys.executable, str(script), "--help"], capture_output=True, text=True)
    assert result.returncode == 0
    assert "Run a C1 observation with safe local execution" in result.stdout
