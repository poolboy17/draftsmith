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
