import subprocess
import sys
from pathlib import Path


def test_provision_aws_help():
    script = Path(__file__).resolve().parent.parent / "tools" / "provision_and_run_aws.py"
    result = subprocess.run([sys.executable, str(script), "--help"], capture_output=True, text=True)
    assert result.returncode == 0
    assert "--region" in result.stdout
    assert "--project" in result.stdout
