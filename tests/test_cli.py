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
