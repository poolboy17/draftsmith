from fastapi.testclient import TestClient


def test_index_ok(monkeypatch):
    # Ensure DRY_RUN for deterministic behavior if any imports occur
    monkeypatch.setenv("DRY_RUN", "1")
    from app import app  # import after setting env

    client = TestClient(app)
    r = client.get("/")
    assert r.status_code == 200
    assert "Draftsmith" in r.text


def test_generate_without_links(monkeypatch):
    monkeypatch.setenv("DRY_RUN", "1")
    from app import app

    client = TestClient(app)
    r = client.post("/generate", data={"prompt": "Test Title"})
    assert r.status_code == 200
    # Prompt should appear on the page
    assert "Test Title" in r.text


def test_generate_with_links(monkeypatch):
    monkeypatch.setenv("DRY_RUN", "1")
    from app import app

    client = TestClient(app)
    r = client.post("/generate", data={"prompt": "Links Please", "fetch_links_flag": "on"})
    assert r.status_code == 200
    # References section should be present when links are included
    assert "References" in r.text


def test_health_wp_success(monkeypatch):
    # Mock the WP connectivity check to avoid real network calls
    monkeypatch.setenv("DRY_RUN", "1")
    import app as webapp

    monkeypatch.setattr(
        webapp,
        "check_wordpress_connection",
        lambda: {
            "ok": True,
            "status_code": 200,
            "url": "https://example.com/wp-json/wp/v2/users/me",
            "user": {"id": 123, "name": "tester"},
            "error": None,
        },
    )

    client = TestClient(webapp.app)
    r = client.get("/health/wp")
    assert r.status_code == 200
    data = r.json()
    assert data["ok"] is True
    assert data["status_code"] == 200
    assert data["url"].endswith("/users/me")
    assert data["user"] == {"id": 123, "name": "tester"}
