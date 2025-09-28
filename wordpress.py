import requests

from config import WP_APP_PASS, WP_URL, WP_USER


def publish_to_wordpress(
    title: str,
    content_html: str,
    status: str = "draft",
    categories: list[int] = None,
) -> dict:
    if not (WP_URL and WP_USER and WP_APP_PASS):
        raise RuntimeError("Missing WordPress credentials in config")
    endpoint = f"{WP_URL.rstrip('/')}/wp-json/wp/v2/posts"
    auth = (WP_USER, WP_APP_PASS)
    payload = {"title": title, "content": content_html, "status": status}
    if categories:
        payload["categories"] = categories
    resp = requests.post(endpoint, json=payload, auth=auth, timeout=10)
    resp.raise_for_status()
    return resp.json()


def check_wordpress_connection(timeout: int = 10) -> dict:
    """
    Quick connectivity check against WordPress using basic auth and the users/me endpoint.

    Returns a dictionary with keys:
    - ok: bool
    - status_code: int | None
    - user: dict | None (when ok)
    - error: str | None (when not ok)
    - url: str (endpoint used)
    """
    if not (WP_URL and WP_USER and WP_APP_PASS):
        return {
            "ok": False,
            "status_code": None,
            "user": None,
            "error": "Missing WordPress credentials in config (.env)",
            "url": None,
        }

    endpoint = f"{WP_URL.rstrip('/')}/wp-json/wp/v2/users/me"
    auth = (WP_USER, WP_APP_PASS)
    try:
        resp = requests.get(
            endpoint,
            auth=auth,
            headers={"Accept": "application/json"},
            timeout=timeout,
        )
        content = None
        try:
            content = resp.json()
        except Exception:  # noqa: BLE001
            content = {"raw": (resp.text[:500] if resp.text else "")}

        if resp.ok:
            return {
                "ok": True,
                "status_code": resp.status_code,
                "user": content,
                "error": None,
                "url": endpoint,
            }
        return {
            "ok": False,
            "status_code": resp.status_code,
            "user": None,
            "error": content,
            "url": endpoint,
        }
    except requests.RequestException as exc:  # network, SSL, timeout, etc.
        return {
            "ok": False,
            "status_code": None,
            "user": None,
            "error": str(exc),
            "url": endpoint,
        }
