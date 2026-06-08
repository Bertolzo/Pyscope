import subprocess
import sys
from pathlib import Path


def test_provision_oci_sdk_help():
    script = Path(__file__).resolve().parent.parent / "tools" / "provision_and_run_oci_sdk.py"
    result = subprocess.run([sys.executable, str(script), "--help"], capture_output=True, text=True)
    assert result.returncode == 0
    assert "--compartment-id" in result.stdout
    assert "--availability-domain" in result.stdout
