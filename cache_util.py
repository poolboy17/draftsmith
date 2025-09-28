import hashlib
import json
from pathlib import Path


def _key(parts: list[str]) -> str:
    h = hashlib.sha256()
    for p in parts:
        h.update(p.encode("utf-8"))
        h.update(b"\0")
    return h.hexdigest()


def cache_read(cache_dir: str, namespace: str, parts: list[str]) -> str | None:
    base = Path(cache_dir) / namespace
    base.mkdir(parents=True, exist_ok=True)
    fname = base / f"{_key(parts)}.json"
    if not fname.exists():
        return None
    data = json.loads(fname.read_text(encoding="utf-8"))
    return data.get("value")


def cache_write(cache_dir: str, namespace: str, parts: list[str], value: str) -> None:
    base = Path(cache_dir) / namespace
    base.mkdir(parents=True, exist_ok=True)
    fname = base / f"{_key(parts)}.json"
    payload = {"value": value}
    fname.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
