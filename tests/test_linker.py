from unittest import mock

import linker


def test_fetch_links_stub_when_dry_run(monkeypatch):
    monkeypatch.setenv("DRY_RUN", "1")
    # Ensure SERPAPI_KEY empty path
    with mock.patch("linker.SERPAPI_KEY", ""):
        links = linker.fetch_links("python", max_links=2)
        assert links == [
            "https://example.com/article-1",
            "https://example.com/article-2",
        ]


def test_fetch_links_handles_no_results(monkeypatch):
    monkeypatch.delenv("DRY_RUN", raising=False)
    with mock.patch("linker.SERPAPI_KEY", "fake-key"):
        with mock.patch("requests.get") as mget:
            mresp = mock.MagicMock()
            mresp.json.return_value = {"organic_results": []}
            mresp.raise_for_status.return_value = None
            mget.return_value = mresp
            out = linker.fetch_links("python", max_links=3)
            assert out == []
            mget.assert_called_once()
