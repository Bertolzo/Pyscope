import subprocess
import sys
from pathlib import Path


def test_mcp_register_help():
    script = Path(__file__).resolve().parent.parent / "tools" / "mcp_register.py"
    result = subprocess.run([sys.executable, str(script), "--help"], capture_output=True, text=True)
    assert result.returncode == 0
    assert "--interactive" in result.stdout
