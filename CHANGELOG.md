# Changelog

All notable changes to this project will be documented in this file.

## [Unreleased]

// Placeholder for upcoming changes. Categorize under Added/Changed/Fixed/Docs/CI as needed.

## [0.1.0] - 2025-09-27

### Added

- Initial public version: CLI orchestration, link fetching via SerpAPI, outline (grok-4-fast) and hydration (GPT-5), output to Markdown/HTML, optional WordPress publish.
- DRY_RUN mode for safe local runs and tests.
- File-based cache and LRU caches for scaffold/hydrate.
- Pre-commit hooks (Black, Flake8, hygiene), GitHub Actions CI with tests and coverage.

### Tests

- Unit tests covering output, CLI, LLM behavior, linker, scaffold/hydrate; overall coverage >90%.

### Docs

- README with setup, usage, flags, and environment variables.

 [Unreleased]: https://github.com/poolboy17/draftsmith/compare/v0.1.0...HEAD
 [0.1.0]: https://github.com/poolboy17/draftsmith/releases/tag/v0.1.0
