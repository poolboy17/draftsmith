import importlib
import types


def test_wordpress_session_headers():
    import wordpress

    s = wordpress._session_with_retries()
    assert "User-Agent" in s.headers and "Accept" in s.headers


def test_cache_corrupt_entry_cleanup(tmp_path):
    from cache_util import cache_read, cache_write

    cache_dir = tmp_path / "cache"
    ns = "ns"
    parts = ["one"]
    cache_write(str(cache_dir), ns, parts, "ok")
    # Find the created file and corrupt it
    files = list((cache_dir / ns).glob("*.json"))
    assert files, "expected a cache file"
    fname = files[0]
    fname.write_text("{broken", encoding="utf-8")
    # Read should return None and cleanup the corrupt file
    out = cache_read(str(cache_dir), ns, parts)
    assert out is None
    assert not fname.exists()


def test_linker_quick_paths(monkeypatch):
    import linker

    # empty query returns []
    assert linker.fetch_links("") == []
    # DRY_RUN stub returns deterministic list
    monkeypatch.setenv("DRY_RUN", "1")
    out = linker.fetch_links("x", max_links=2)
    assert out and len(out) == 2


def test_llm_normal_flow(monkeypatch):
    # Ensure module picks up env
    monkeypatch.setenv("OPENROUTER_API_KEY", "DUMMY")
    monkeypatch.delenv("DRY_RUN", raising=False)
    import llm as _llm

    importlib.reload(_llm)

    class _FakeCompletions:
        def create(self, model, messages):  # noqa: ARG002
            return types.SimpleNamespace(
                choices=[types.SimpleNamespace(message=types.SimpleNamespace(content="ok"))]
            )

    class _FakeClient:
        def __init__(self):
            self.chat = types.SimpleNamespace(completions=_FakeCompletions())

    # Bypass actual client creation
    monkeypatch.setattr(_llm.client, "_ensure", lambda: _FakeClient())
    out = _llm.client.chat("m", messages=[{"role": "user", "content": "hi"}])
    assert out == "ok"
