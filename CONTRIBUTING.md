# Contributing to Draftsmith

Thanks for your interest in contributing! This guide covers local setup, coding standards, commit conventions, testing, and releases.

## Local setup

Recommended: Python 3.12+

1. Create and activate a virtual environment

```pwsh
python -m venv .venv
.venv\Scripts\Activate.ps1
```

1. Install dependencies

```pwsh
pip install -r requirements.txt
```

1. Install pre-commit hooks (format, lint, hygiene, conventional commits)

```pwsh
pre-commit install --hook-type pre-commit --hook-type commit-msg
```

1. Environment variables

- Use a local `.env` file. Do not commit secrets.
- DRY_RUN=true is supported for safe local development and tests.

## Workflow and quality gates

- Formatting: Black is enforced via pre-commit.
- Linting: Flake8 is enforced via pre-commit.
- Tests: Pytest with coverage. Coverage threshold ≥ 85%.

Run all checks locally:

```pwsh
pre-commit run --all-files
pytest --maxfail=1 -q --cov --cov-report=term-missing
```

## Conventional Commits

This repo uses Conventional Commits to drive semantic-release.

Format:

```text
<type>(<scope>): <short summary>

<body>

BREAKING CHANGE: <description>
```

Common types:

- feat: a new feature
- fix: a bug fix
- docs: documentation only changes
- style: formatting, missing semi colons, etc.; no code change
- refactor: code change that neither fixes a bug nor adds a feature
- perf: performance improvement
- test: adding or correcting tests
- build: build system or external dependencies
- ci: CI configuration and scripts
- chore: other changes that don't modify src or tests
- revert: reverts a previous commit

Examples:

- `feat(cli): add --no-cache flag`
- `fix(linker): handle empty results from SerpAPI`
- `docs(readme): add usage examples`
- `ci: run tests with coverage`

Breaking changes:

- Add `!` after type, or include a `BREAKING CHANGE:` footer.
  - Example: `feat!: drop support for Python 3.9`

## Changelog

- Edit the `## [Unreleased]` section in `CHANGELOG.md` during development.
- Use categories like Added, Changed, Fixed, Docs, CI, Refactor, etc.
- The release automation moves notes into a new versioned section.

## Releases

- `main` branch is protected and uses semantic-release via GitHub Actions.
- Version, tag, GitHub Release, and changelog entries are created automatically based on commit history.
- Ensure all commits follow Conventional Commits so the correct version bump occurs.

## Pull Requests

- Keep PRs focused and small where possible.
- Ensure pre-commit checks and tests pass locally.
- Add or update tests for user-visible changes.
- Update `CHANGELOG.md` under Unreleased when applicable.

## Running in DRY_RUN mode

- Set `DRY_RUN=true` to avoid external calls (LLM, link fetching, publishing) and get deterministic outputs.
- Some integrations (e.g., WordPress) require secrets; keep them in `.env` for local runs and never commit them.
