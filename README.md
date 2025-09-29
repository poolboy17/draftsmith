# Draftsmith

[![CI](https://github.com/poolboy17/draftsmith/actions/workflows/ci.yml/badge.svg?branch=main)](https://github.com/poolboy17/draftsmith/actions/workflows/ci.yml)
[![Release](https://github.com/poolboy17/draftsmith/actions/workflows/release.yml/badge.svg?branch=main)](https://github.com/poolboy17/draftsmith/actions/workflows/release.yml)

Generate, format, and optionally publish articles via CLI.

## Setup

1. Clone repo:

    ```powershell
    git clone https://github.com/poolboy17/draftsmith.git
    cd draftsmith
    ```

2. Install dependencies (runtime only):

    ```powershell
    pip install -r requirements.txt
    ```

   For development (tests, linting, hooks), also install dev dependencies:

    ```powershell
    pip install -r requirements-dev.txt
    ```

3. Copy `.env.example` to `.env` and fill in your keys.

## Usage

Basic generation to Markdown:

```powershell
python cli.py --prompt "My Topic" --output out.md
```

Fetch top links (requires SERPAPI_KEY) and include references:

```powershell
python cli.py --prompt "My Topic" --fetch-links --max-links 3 --output out.md
```

Dry run (no external calls; fast & safe):

```powershell
python cli.py --prompt "My Topic" --dry-run --output out.md
```

Publish to WordPress as draft (requires WP_* env vars):

```powershell
python cli.py --prompt "My Post" --fetch-links --publish --status draft --categories 5 7
```

### Flags

- `--dry-run`: Skip LLM/SerpAPI/WP network calls; uses deterministic stubs
- `--fetch-links`: Use SerpAPI to get links (needs `SERPAPI_KEY`)
- `--max-links N`: Limit number of links fetched (default from config)
- `--format md|html`: Output format (default `md`)
- `--publish`: Publish to WordPress
- `--status draft|publish`: WordPress post status (default `draft`)
- `--categories <ids...>`: WordPress category IDs
- `--cache-dir PATH`: Directory for simple file cache (default `.cache`)
- `--no-cache`: Disable file cache for scaffold/hydrate

### Cache clearing

- `--clear-cache` clears the in-memory LRU caches for outline and hydration. After an internal refactor, the cache is applied to a helper inside `scaffold.py`; the CLI clears the correct cached function under the hood.

### DRY_RUN behavior

- When `--dry-run` is used, or `DRY_RUN=1` is set in the environment:
  - LLM calls return deterministic stub content prefixed with `[DRY_RUN:<model>]` and echo the last user message.
  - Link fetching returns stub links if `SERPAPI_KEY` is missing.
  - WordPress publishing is skipped.

### Env

- `OPENROUTER_API_KEY` (required unless `--dry-run`)
- `SERPAPI_KEY` (required if using `--fetch-links`)
- `WP_URL`, `WP_USER`, `WP_APP_PASS` (required if using `--publish`)

## Development

- Run tests:

    ```powershell
    pytest
    ```

- Format and lint:

    ```powershell
    black .
    flake8 .
    ```

- Enable git hooks (once):

    ```powershell
    pre-commit install --hook-type pre-commit --hook-type commit-msg
    ```

CI runs formatting, linting, and tests with coverage; a `coverage.xml` report is uploaded per job.

## Contributing

Please see [CONTRIBUTING.md](CONTRIBUTING.md) for local setup, Conventional Commits, testing, and release workflow details.
