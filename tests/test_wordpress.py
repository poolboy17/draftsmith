import types


class DummyResp:
    def __init__(self, data):
        self._data = data

    def raise_for_status(self):
        return None

    def json(self):
        return self._data


def test_publish_to_wordpress(monkeypatch):
    monkeypatch.setenv("OPENROUTER_API_KEY", "DUMMY")
    monkeypatch.setenv("WP_URL", "https://example.com")
    monkeypatch.setenv("WP_USER", "user")
    monkeypatch.setenv("WP_APP_PASS", "pass")

    import wordpress  # noqa: WPS433

    # Ensure module-level constants are what we expect even if config was imported earlier
    wordpress.WP_URL = "https://example.com"
    wordpress.WP_USER = "user"
    wordpress.WP_APP_PASS = "pass"

    def fake_post(url, json, auth, timeout):  # noqa: ARG001 (pytest style)
        assert url.endswith("/wp-json/wp/v2/posts")
        assert auth == ("user", "pass")
        assert json["title"] == "Title"
        return DummyResp({"id": 123, "status": "draft"})

    monkeypatch.setattr(wordpress, "requests", types.SimpleNamespace(post=fake_post))

    out = wordpress.publish_to_wordpress(
        title="Title", content_html="<p>x</p>", status="draft", categories=[1, 2]
    )
    assert out["id"] == 123 and out["status"] == "draft"
