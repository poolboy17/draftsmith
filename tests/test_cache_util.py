from pathlib import Path

from cache_util import cache_read, cache_write


def test_cache_read_miss(tmp_path: Path):
    val = cache_read(str(tmp_path), "ns", ["a", "b"])
    assert val is None


def test_cache_write_and_read(tmp_path: Path):
    cache_dir = str(tmp_path)
    cache_write(cache_dir, "ns", ["p1", "p2"], "VALUE")
    got = cache_read(cache_dir, "ns", ["p1", "p2"])
    assert got == "VALUE"


def test_cache_is_keyed_by_parts(tmp_path: Path):
    cache_dir = str(tmp_path)
    cache_write(cache_dir, "ns", ["x"], "VX")
    cache_write(cache_dir, "ns", ["y"], "VY")
    assert cache_read(cache_dir, "ns", ["x"]) == "VX"
    assert cache_read(cache_dir, "ns", ["y"]) == "VY"
