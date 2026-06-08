import subprocess
import sys
from pathlib import Path


def test_remote_runner_help():
    script = Path(__file__).resolve().parent.parent / "tools" / "remote_runner.py"
    result = subprocess.run([sys.executable, str(script), "--help"], capture_output=True, text=True)
    assert result.returncode == 0
    assert "--host" in result.stdout
