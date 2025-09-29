class DummyResp:
    def __init__(self, data, status_code=200, content=None):
        self._data = data
        self.status_code = status_code
        # Some code paths (media download) access .content on the response
        if content is not None:
            self.content = content
        elif isinstance(data, (bytes, bytearray)):
            self.content = data
        else:
            self.content = None

    def raise_for_status(self):
        return None

    def json(self):
        return self._data


class FakeSession:
    def __init__(self):
        self.posts = []
        self.gets = []

    def get(self, url, params=None, auth=None, timeout=None):  # noqa: D401
        self.gets.append((url, params))
        # WP API endpoints contain /wp-json/; return JSON structures
        if "/wp-json/" in url:
            # Terms search endpoints return empty by default (forces create)
            return DummyResp([])
        # Otherwise treat as media download (return bytes in .content)
        return DummyResp(b"img-bytes")

    def post(self, url, json=None, files=None, auth=None, timeout=None):  # noqa: A002
        # Media upload
        if url.endswith("/wp-json/wp/v2/media"):
            assert files and "file" in files
            return DummyResp({"id": 77})
        # Term create (categories or tags)
        if url.endswith("/wp-json/wp/v2/categories"):
            return DummyResp({"id": 33})
        if url.endswith("/wp-json/wp/v2/tags"):
            return DummyResp({"id": 44})
        # Posts endpoint
        if url.endswith("/wp-json/wp/v2/posts"):
            self.posts.append(json or {})
            return DummyResp({"id": 123, "status": (json or {}).get("status", "draft")})
        raise AssertionError(f"Unexpected POST url: {url}")


def _prep_env(monkeypatch):
    monkeypatch.setenv("OPENROUTER_API_KEY", "DUMMY")
    monkeypatch.setenv("WP_URL", "https://example.com")
    monkeypatch.setenv("WP_USER", "user")
    monkeypatch.setenv("WP_APP_PASS", "pass")


def test_publish_with_ids(monkeypatch):
    _prep_env(monkeypatch)
    import wordpress  # noqa: WPS433

    wordpress.WP_URL = "https://example.com"
    wordpress.WP_USER = "user"
    wordpress.WP_APP_PASS = "pass"

    fake = FakeSession()
    monkeypatch.setattr(wordpress, "_session_with_retries", lambda: fake)

    out = wordpress.publish_to_wordpress(
        title="Title",
        content_html="<p>x</p>",
        status="draft",
        categories=[1, 2],
        tags=[5],
    )
    assert out["id"] == 123 and out["status"] == "draft"
    assert fake.posts[-1]["categories"] == [1, 2]
    assert fake.posts[-1]["tags"] == [5]
    assert "preview_link" in out and "?p=123" in out["preview_link"]


def test_publish_with_names_creates_terms(monkeypatch):
    _prep_env(monkeypatch)
    import wordpress  # noqa: WPS433

    wordpress.WP_URL = "https://example.com"
    wordpress.WP_USER = "user"
    wordpress.WP_APP_PASS = "pass"

    fake = FakeSession()
    monkeypatch.setattr(wordpress, "_session_with_retries", lambda: fake)

    out = wordpress.publish_to_wordpress(
        title="Title",
        content_html="<p>x</p>",
        status="draft",
        category_names=["News"],
        tag_names=["Tips"],
    )
    assert out["id"] == 123
    assert fake.posts[-1]["categories"] == [33]
    assert fake.posts[-1]["tags"] == [44]


def test_publish_with_featured_image_url(monkeypatch):
    _prep_env(monkeypatch)
    import wordpress  # noqa: WPS433

    wordpress.WP_URL = "https://example.com"
    wordpress.WP_USER = "user"
    wordpress.WP_APP_PASS = "pass"

    fake = FakeSession()
    monkeypatch.setattr(wordpress, "_session_with_retries", lambda: fake)

    out = wordpress.publish_to_wordpress(
        title="Title",
        content_html="<p>x</p>",
        status="publish",
        featured_image="https://cdn.example.com/img.jpg",
    )
    assert out["id"] == 123
    # Ensure featured_media is included in the payload used for the post
    assert fake.posts[-1]["featured_media"] == 77


def test_publish_dry_run(monkeypatch):
    _prep_env(monkeypatch)
    import os

    os.environ["DRY_RUN"] = "1"
    import wordpress  # noqa: WPS433

    wordpress.WP_URL = "https://example.com"

    out = wordpress.publish_to_wordpress(
        title="X",
        content_html="<p>x</p>",
        status="draft",
    )
    assert out["id"] == 0
    assert "preview_link" in out
