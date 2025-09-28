# Draftsmith

Generate, format, and optionally publish articles via CLI.

## Setup

1. Clone repo:

    ```powershell
    git clone <repo-url>
    cd article-generator
    ```

2. Install dependencies:

    ```powershell
    pip install -r requirements.txt
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

CI runs formatting, linting, and tests with coverage; a `coverage.xml` report is uploaded per job.
