"""
Pytest configuration shared across tests.

Ensures the repository root is on sys.path so modules like `linker` and
`output` can be imported when pytest is invoked with `testpaths = tests`.
This mirrors how developers typically run tests locally from the project root.
"""

from __future__ import annotations

import sys
from pathlib import Path


def _ensure_project_root_on_syspath() -> None:
    # tests/ -> repo root
    repo_root = Path(__file__).resolve().parents[1]
    repo_root_str = str(repo_root)
    if repo_root_str not in sys.path:
        sys.path.insert(0, repo_root_str)


_ensure_project_root_on_syspath()
