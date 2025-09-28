import importlib
import os
from unittest import mock


def reload_llm_with_env(**env):
    """Utility to reload llm module with specific env vars."""
    with mock.patch.dict(os.environ, env, clear=False):
        # Ensure config and llm are reloaded to pick up env
        import config as _config

        importlib.reload(_config)
        with mock.patch.dict("sys.modules", {"config": _config}):
            import llm as _llm

            importlib.reload(_llm)
            return _llm


def test_llm_chat_dry_run_uses_last_user_content():
    llm = reload_llm_with_env(DRY_RUN="1", OPENROUTER_API_KEY="")
    with mock.patch.dict(os.environ, {"DRY_RUN": "1"}, clear=False):
        out = llm.client.chat(
            model="test-model",
            messages=[
                {"role": "system", "content": "sys"},
                {"role": "user", "content": "first"},
                {"role": "assistant", "content": "mid"},
                {"role": "user", "content": "last"},
            ],
        )
    assert out.startswith("[DRY_RUN:test-model]")
    assert out.endswith("last")


def test_llm_raises_when_no_key_and_not_dry_run():
    llm = reload_llm_with_env(DRY_RUN="0", OPENROUTER_API_KEY="")
    # Stub openrouter import so import path exists if reached; but we expect error before
    with mock.patch.dict("sys.modules", {"openrouter": mock.MagicMock()}):
        try:
            llm.client.chat(model="m", messages=[{"role": "user", "content": "x"}])
        except RuntimeError as e:
            assert "OPENROUTER_API_KEY" in str(e)
        else:
            raise AssertionError("Expected RuntimeError when key is missing")
