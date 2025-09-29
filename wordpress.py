from __future__ import annotations

import mimetypes
import os
import urllib.parse

import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

from config import MAX_MEDIA_BYTES, USER_AGENT, WP_APP_PASS, WP_URL, WP_USER


def _session_with_retries() -> requests.Session:
    s = requests.Session()
    try:
        retries = Retry(
            total=3,
            connect=3,
            read=3,
            backoff_factor=0.5,
            status_forcelist=[429, 500, 502, 503, 504],
            allowed_methods=["GET", "POST"],
            raise_on_status=False,
        )
    except TypeError:
        # Fallback for older urllib3 where 'allowed_methods' may be 'method_whitelist'
        retries = Retry(
            total=3,
            connect=3,
            read=3,
            backoff_factor=0.5,
            status_forcelist=[429, 500, 502, 503, 504],
            method_whitelist=["GET", "POST"],
            raise_on_status=False,
        )
    adapter = HTTPAdapter(max_retries=retries)
    s.mount("http://", adapter)
    s.mount("https://", adapter)
    s.headers.update({"User-Agent": USER_AGENT, "Accept": "application/json"})
    return s


def _api_url(path: str) -> str:
    return f"{WP_URL.rstrip('/')}{path}"


def _auth():
    return (WP_USER, WP_APP_PASS)


def _find_or_create_terms(
    taxonomy: str, names: list[str] | None, create_missing: bool = True
) -> list[int]:
    if not names:
        return []
    session = _session_with_retries()
    auth = _auth()
    ids: list[int] = []
    for name in names:
        name = name.strip()
        if not name:
            continue
        # search existing
        search_ep = _api_url(f"/wp-json/wp/v2/{taxonomy}")
        r = session.get(
            search_ep,
            params={"search": name, "per_page": 100},
            auth=auth,
            timeout=10,
        )
        r.raise_for_status()
        results = r.json()
        match = next(
            (t for t in results if t.get("name", "").strip().lower() == name.lower()),
            None,
        )
        if match:
            ids.append(int(match["id"]))
            continue
        if create_missing:
            cr = session.post(search_ep, json={"name": name}, auth=auth, timeout=10)
            cr.raise_for_status()
            ids.append(int(cr.json()["id"]))
    return ids


ALLOWED_MEDIA_TYPES = {
    "image/jpeg",
    "image/png",
    "image/gif",
    "image/webp",
}


def _upload_featured_media(image: str | None) -> int | None:
    if not image:
        return None
    session = _session_with_retries()
    auth = _auth()
    filename = None
    content: bytes | None = None
    if image.startswith("http://") or image.startswith("https://"):
        filename = urllib.parse.unquote(image.split("/")[-1]) or "image"
        r = session.get(image, timeout=20, stream=True)
        r.raise_for_status()
        # Enforce max size
        chunks = []
        total = 0
        for chunk in r.iter_content(chunk_size=8192):
            if not chunk:
                continue
            total += len(chunk)
            if total > MAX_MEDIA_BYTES:
                raise ValueError("Featured image exceeds size limit")
            chunks.append(chunk)
        content = b"".join(chunks)
    else:
        filename = os.path.basename(image)
        with open(image, "rb") as f:
            content = f.read()
    mime, _ = mimetypes.guess_type(filename)
    if not mime:
        mime = "application/octet-stream"
    if mime not in ALLOWED_MEDIA_TYPES:
        raise ValueError(f"Unsupported featured image content-type: {mime}")
    files = {"file": (filename, content, mime)}
    ep = _api_url("/wp-json/wp/v2/media")
    resp = session.post(ep, files=files, auth=auth, timeout=30)
    resp.raise_for_status()
    return int(resp.json().get("id"))


def _merge_terms(
    existing: list[int] | None, names: list[str] | None, taxonomy: str
) -> list[int] | None:
    if not names and not existing:
        return None
    resolved = _find_or_create_terms(taxonomy, names) if names else []
    merged = list({int(x) for x in (existing or []) + resolved})
    return merged or None


def _compute_preview_link(status: str, post_id: int, link: str | None) -> str:
    if status == "publish" and link:
        return link
    return f"{WP_URL.rstrip('/')}/?p={post_id}&preview=true"


def _dry_run_response(status: str) -> dict:
    fake_id = 0
    if status != "publish":
        preview = f"{WP_URL.rstrip('/')}/?p={fake_id}&preview=true"
    else:
        preview = f"{WP_URL.rstrip('/')}/posts/{fake_id}"
    return {
        "id": fake_id,
        "status": status,
        "link": preview,
        "preview_link": preview,
    }


def _build_payload(
    title: str,
    content_html: str,
    status: str,
    categories: list[int] | None,
    tags: list[int] | None,
    featured_media_id: int | None,
) -> dict:
    payload: dict = {"title": title, "content": content_html, "status": status}
    if categories:
        payload["categories"] = categories
    if tags:
        payload["tags"] = tags
    if featured_media_id:
        payload["featured_media"] = featured_media_id
    return payload


def publish_to_wordpress(
    title: str,
    content_html: str,
    status: str = "draft",
    categories: list[int] | None = None,
    category_names: list[str] | None = None,
    tags: list[int] | None = None,
    tag_names: list[str] | None = None,
    featured_image: str | None = None,
) -> dict:
    # DRY_RUN path returns deterministic stub
    if os.getenv("DRY_RUN") == "1":
        return _dry_run_response(status)

    if not (WP_URL and WP_USER and WP_APP_PASS):
        raise RuntimeError("Missing WordPress credentials in config")

    session = _session_with_retries()
    auth = _auth()

    # Resolve categories/tags by name if provided
    categories = _merge_terms(categories, category_names, "categories")
    tags = _merge_terms(tags, tag_names, "tags")

    # Upload featured image if provided
    featured_media_id = _upload_featured_media(featured_image)

    payload = _build_payload(title, content_html, status, categories, tags, featured_media_id)

    endpoint = _api_url("/wp-json/wp/v2/posts")
    resp = session.post(endpoint, json=payload, auth=auth, timeout=20)
    resp.raise_for_status()
    data = resp.json()
    post_id = int(data.get("id"))
    link = data.get("link")
    preview_link = _compute_preview_link(status, post_id, link)
    data["preview_link"] = preview_link
    return data


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
