from pathlib import Path

from tools.freetier_adapter import (
    get_cached_promotions,
    refresh_free_tier_promotions,
    is_local_host_insufficient,
)


def test_get_cached_promotions_returns_default_when_missing(tmp_path: Path):
    cache_file = tmp_path / "missing_cache.json"
    promotions = get_cached_promotions(path=cache_file)
    assert promotions
    assert any(p.provider == "AWS" for p in promotions)


def test_refresh_free_tier_promotions_writes_cache(tmp_path: Path):
    cache_file = tmp_path / "promotions.json"
    promotions = refresh_free_tier_promotions(path=cache_file, timeout=1)
    assert promotions
    assert cache_file.exists()
    loaded = get_cached_promotions(path=cache_file)
    assert len(loaded) == len(promotions)


def test_is_local_host_insufficient_handles_edge_cases():
    assert is_local_host_insufficient(0, 0)
    assert is_local_host_insufficient(7 * 1024 ** 3, 4)
    assert not is_local_host_insufficient(8 * 1024 ** 3, 4)
