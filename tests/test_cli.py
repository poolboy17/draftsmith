import sys
import types


def _install_fake_openrouter():
    class _FakeCompletions:
        def create(self, model, messages):  # noqa: ARG002
            return types.SimpleNamespace(
                choices=[types.SimpleNamespace(message=types.SimpleNamespace(content="stubbed"))]
            )

    class _FakeClient:
        def __init__(self, api_key=None):  # noqa: ARG002
            self.chat = types.SimpleNamespace(completions=_FakeCompletions())

    sys.modules["openrouter"] = types.SimpleNamespace(OpenRouterClient=_FakeClient)


def test_cli_generates_markdown(tmp_path, monkeypatch):
    # Ensure config import doesn't crash
    monkeypatch.setenv("OPENROUTER_API_KEY", "DUMMY")

    # Install fake openrouter before importing cli (cli imports hydrate/scaffold)
    _install_fake_openrouter()
    import cli

    # Stub model functions to avoid external calls
    monkeypatch.setattr(
        cli,
        "scaffold_article",
        lambda prompt, links=None, model=None: "# Outline\n\n- A\n- B",
    )
    monkeypatch.setattr(
        cli,
        "hydrate_article",
        lambda outline, model=None: "# Article\n\nHello world",
    )

    out_file = tmp_path / "article.md"
    argv = [
        "cli.py",
        "--prompt",
        "Test Title",
        "--output",
        str(out_file),
    ]

    monkeypatch.setenv("PYTHONWARNINGS", "ignore")
    monkeypatch.setattr(sys, "argv", argv)
    cli.main()

    text = out_file.read_text(encoding="utf-8")
    assert "# Article" in text and "Hello world" in text


def test_cli_no_cache(tmp_path, monkeypatch):
    monkeypatch.setenv("OPENROUTER_API_KEY", "DUMMY")
    _install_fake_openrouter()
    import importlib

    import cli as _cli

    importlib.reload(_cli)
    calls = {"scaffold": 0, "hydrate": 0}

    def _scaffold(*a, **kw):  # noqa: ANN001, ANN002
        calls["scaffold"] += 1
        return "outline"

    def _hydrate(*a, **kw):  # noqa: ANN001, ANN002
        calls["hydrate"] += 1
        return "article"

    monkeypatch.setattr(_cli, "scaffold_article", _scaffold)
    monkeypatch.setattr(_cli, "hydrate_article", _hydrate)

    out_file = tmp_path / "a.md"
    argv = [
        "cli.py",
        "--prompt",
        "Title",
        "--output",
        str(out_file),
        "--no-cache",
    ]
    monkeypatch.setattr(sys, "argv", argv)
    _cli.main()
    assert calls["scaffold"] == 1 and calls["hydrate"] == 1


def test_cli_cache_dir(tmp_path, monkeypatch):
    monkeypatch.setenv("OPENROUTER_API_KEY", "DUMMY")
    _install_fake_openrouter()
    import importlib

    import cli as _cli

    importlib.reload(_cli)

    # Force deterministic output for caching
    monkeypatch.setattr(_cli, "scaffold_article", lambda *a, **k: "outline")
    monkeypatch.setattr(_cli, "hydrate_article", lambda *a, **k: "article")

    cache_dir = tmp_path / "cache"
    out_file1 = tmp_path / "first.md"
    argv = [
        "cli.py",
        "--prompt",
        "Title",
        "--output",
        str(out_file1),
        "--cache-dir",
        str(cache_dir),
    ]
    monkeypatch.setattr(sys, "argv", argv)
    _cli.main()

    # Second run should reuse cache (no assertions on calls as we stubbed deterministic functions)
    out_file2 = tmp_path / "second.md"
    argv2 = [
        "cli.py",
        "--prompt",
        "Title",
        "--output",
        str(out_file2),
        "--cache-dir",
        str(cache_dir),
    ]
    monkeypatch.setattr(sys, "argv", argv2)
    _cli.main()
    assert out_file1.exists() and out_file2.exists()
