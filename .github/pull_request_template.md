# Pull Request

## Summary

Describe the change and why it’s needed.

## Changes

-

## How to test

Provide steps to validate locally, including any environment variables (use DRY_RUN where applicable):

```pwsh
# example
pre-commit run --all-files
pytest -q --cov --cov-report=term-missing
```

## Screenshots (optional)

## Checklist

- [ ] My commit(s) follow Conventional Commits (e.g., `feat(scope): ...`, `fix: ...`).
- [ ] I ran pre-commit hooks locally (`pre-commit run --all-files`).
- [ ] I added/updated tests for user-visible changes.
- [ ] I updated `CHANGELOG.md` under `## [Unreleased]` if appropriate.
- [ ] Secrets are not committed; `.env` used for local dev only.
- [ ] DRY_RUN behavior considered/implemented for external calls (LLM, links, publish).
