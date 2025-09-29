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
    try:
        data = json.loads(fname.read_text(encoding="utf-8"))
        return data.get("value")
    except json.JSONDecodeError:
        # Corrupt cache entry; remove and return miss
        try:
            fname.unlink(missing_ok=True)
        except Exception:  # noqa: BLE001
            pass
        return None


def cache_write(cache_dir: str, namespace: str, parts: list[str], value: str) -> None:
    base = Path(cache_dir) / namespace
    base.mkdir(parents=True, exist_ok=True)
    fname = base / f"{_key(parts)}.json"
    payload = {"value": value}
    tmp = fname.with_suffix(fname.suffix + ".tmp")
    tmp.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    tmp.replace(fname)
