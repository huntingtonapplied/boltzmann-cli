# Changelog

All notable changes to the Boltzmann CLI will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.0.3] - 2026-10-14

### Fixed
- The update check no longer queries PyPI. `boltzmann-cli` is not published there and the PyPI name may belong to an unrelated project, so the old check could report a stranger's version and suggest installing it. It now reads the latest GitHub release of huntingtonapplied/boltzmann-cli and suggests `pip install --upgrade git+https://github.com/huntingtonapplied/boltzmann-cli`, only when that release is newer.

## [1.0.2] - 2026-10-13

### Changed
- README: describes the hosted API only (removed the self-hosted backend wording; the backend is not distributed).

## [1.1.0] - Unreleased

### Added
- `--output/-o {table,json,yaml}` global flag for output format
- `--no-color` flag (also honors the `NO_COLOR` env var)
- `--verbose/-v` flag for INFO-level logging to stderr
- `--debug` flag for DEBUG-level logging (HTTP requests)
- `--ci` flag for CI/CD usage (no color, no spinners, no prompts); auto-detected from `CI`, `GITHUB_ACTIONS`, `GITLAB_CI`
- `boltzmann doctor` command — checks Python, config, API connectivity, auth, and shell completion
- `boltzmann completion` command — generate/install shell completion for bash, zsh, fish
- Distinct exit codes: 2 (auth), 3 (not found), 4 (validation), 5 (network), 6 (server), 7 (duplicate), 130 (SIGINT), 143 (SIGTERM)
- Config validation with typo detection (`did you mean 'api_key'?`) on startup
- SIGTERM signal handling across all commands (clean exit with code 143)
- Top-level KeyboardInterrupt handler as a safety net for all commands
- Non-blocking version update check (background thread, 24h throttle, disabled in CI; disable with `BOLTZMANN_NO_UPDATE_CHECK`)
- Infra modules `exit_codes.py`, `log.py`, `output.py`, `update_check.py`
- Standalone binary + wheel packaging (`Makefile`, `scripts/`), SEGA publish docs (`.sega/README.md`)
- Test suite (`tests/`) with pytest

### Changed
- Entry point now wraps the CLI group with signal/exception handling (`boltzmann_cli.main:main`)
- Version is derived from package metadata (`importlib.metadata`) instead of being hardcoded
- Logging now routes through the `boltzmann` logger to stderr (keeps stdout clean for piped output)

## [1.0.0] - 2026-01-01

### Added
- Initial release with `login`, `simulations`, `projects`, `jobs`, `config`, `auth`, and `api-keys` commands
- Tabular output via `tabulate`
- Retry logic with exponential backoff for transient HTTP errors (429, 500, 502, 503, 504) and network failures; configurable via `BOLTZMANN_MAX_RETRIES`
- Bearer (JWT) and ApiKey authentication schemes
