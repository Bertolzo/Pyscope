from tools.resource_adapter import (
    recommend_limits,
    run_command_with_limits,
)
from tools.freetier_adapter import (
    is_local_host_insufficient,
    recommend_remote_fallback,
)


def test_recommend_limits_low_impact():
    rec = recommend_limits(prefer_low_impact=True)
    assert rec["recommended_nice"] == 10
    assert rec["recommended_cpu_percent"] <= 60
    assert isinstance(rec["recommended_memory_limit_bytes"], int)


def test_is_local_host_insufficient():
    assert is_local_host_insufficient(7 * 1024 ** 3, 4)
    assert is_local_host_insufficient(8 * 1024 ** 3 - 1, 4)
    assert is_local_host_insufficient(12 * 1024 ** 3, 3)
    assert not is_local_host_insufficient(12 * 1024 ** 3, 4)


def test_recommend_remote_fallback_uses_promotions():
    promotions = recommend_remote_fallback(
        total_memory_bytes=7 * 1024 ** 3,
        cpu_count=4,
        prefer_low_impact=True,
    )
    assert promotions
    assert any(p.provider == "AWS" for p in promotions)


def test_run_command_with_limits_returns_zero():
    rc = run_command_with_limits("echo test", cpu_percent=10, nice=10, timeout=5)
    assert rc == 0


def test_skip_if_insufficient_alias():
    import subprocess
    import sys

    result = subprocess.run(
        [sys.executable, "tools/resource_adapter.py", "--run", "echo alias-ok", "--skip-if-insufficient"],
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0
    assert "Skipping local execution because --skip-if-insufficient was set." in result.stdout
