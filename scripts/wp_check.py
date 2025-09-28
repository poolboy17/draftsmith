#!/usr/bin/env python3
"""Quick WordPress connectivity check using .env credentials.

Exits with code 0 on success, 1 on failure. Prints a JSON summary.
"""

import json
import sys
from pathlib import Path

from dotenv import load_dotenv

# Ensure project root is on sys.path so we can import 'wordpress'
ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

load_dotenv()

try:
    from wordpress import check_wordpress_connection
except Exception as exc:  # noqa: BLE001
    print(json.dumps({"ok": False, "error": f"Import error: {exc}"}, indent=2))
    sys.exit(1)

result = check_wordpress_connection()
print(json.dumps(result, indent=2))
sys.exit(0 if result.get("ok") else 1)
