<div align="center">
  <img src=".readme/logo.png" alt="Boltzmann CLI" width="360"><br><br>
</div>

[![Python](https://img.shields.io/badge/python-3.10+-blue.svg)](https://python.org)
[![License](https://img.shields.io/badge/license-MIT-blue.svg)](#license)
[![Status](https://img.shields.io/badge/status-active-success.svg)](#)

-----------------

**Boltzmann CLI** is the command-line client for the Boltzmann multiphysics simulation platform — authenticate with an API key and drive simulations, projects, and jobs from your terminal or CI pipeline.

It is a thin client: it talks to the hosted Boltzmann API (or a self-hosted backend on `http://localhost:8009`), so no local physics engine or database is required to manage simulations.

## Install

Standalone binary (no Python required; verifies SHA256 before installing):

```bash
curl -fsSL https://downloads.boltzmann.app/cli/install.sh | bash
```

Pin a release, or install without sudo into `~/.local/bin`:

```bash
curl -fsSL https://downloads.boltzmann.app/cli/install.sh | bash -s -- --version 1.0.0
curl -fsSL https://downloads.boltzmann.app/cli/install.sh | bash -s -- --install-dir ~/.local/bin
```

From source (a clone of this repo):

```bash
pip install -e .
```

## Quick Start

```bash
# Authenticate — paste the API key from app.boltzmann.app → Account → Developer
boltzmann login

# Diagnose setup & connectivity
boltzmann doctor

# Manage simulations
boltzmann simulations list
boltzmann simulations create my-sim --type electromagnetic
boltzmann simulations status <simulation_id>
```

## Commands

| Command | Description |
|---------|-------------|
| `boltzmann login` | Authenticate and save your API key |
| `boltzmann simulations list/create/status/stop` | Manage simulations |
| `boltzmann projects list/create` | Manage projects |
| `boltzmann jobs list/status` | Manage background jobs |
| `boltzmann api-keys list/create/rotate/update/revoke/delete/stats` | Manage API keys |
| `boltzmann auth status/token` | Authentication commands |
| `boltzmann config show/validate` | Configuration management |
| `boltzmann doctor` | Diagnose CLI setup and connectivity |
| `boltzmann completion <shell>` | Generate / install shell completion |

### Global options

- `--output/-o {table,json,yaml}` — output format (default: `table`)
- `--no-color` — disable colored output (also honors `NO_COLOR`)
- `--verbose/-v` — INFO-level logging to stderr
- `--debug` — DEBUG-level logging (HTTP requests)
- `--ci` — CI mode: no color, no spinners, no prompts (auto-detected from `CI`, `GITHUB_ACTIONS`, `GITLAB_CI`)

## Configuration

Config is stored in `~/.boltzmann/config.yaml`:

```yaml
api_key: bz_live_abc123...
api_url: http://localhost:8009   # optional, for self-hosted
```

Environment variables override config:

- `BOLTZMANN_API_KEY` — API key
- `BOLTZMANN_API_URL` — API base URL
- `BOLTZMANN_MAX_RETRIES` — retry attempts for transient failures (default: 3)
- `BOLTZMANN_TIMEOUT` — request timeout in seconds (default: 30)
- `BOLTZMANN_NO_UPDATE_CHECK` — disable the background version check

### Exit codes

| Code | Meaning | | Code | Meaning |
|------|---------|-|------|---------|
| 0 | Success | | 5 | Network error |
| 1 | General error | | 6 | Server error |
| 2 | Authentication error | | 7 | Duplicate |
| 3 | Not found | | 130 | Interrupted (SIGINT) |
| 4 | Validation error | | 143 | Terminated (SIGTERM) |

## Development

```bash
pip install -e cli/            # install in dev mode
cd cli/
pip install -e ".[test]"
pytest -q                      # tests
ruff check boltzmann_cli/      # lint
```

### Distribution

```bash
make build-binary   # standalone binary into dist/ (PyInstaller)
make build-wheel    # wheel/sdist into dist/
make smoke          # build binary and run --help
```

## Documentation & resources

- Root README — platform overview
- Backend README — the API this CLI talks to
- `.sega/README.md` — publishing binaries via SEGA
- Hosted app: [app.boltzmann.app](https://app.boltzmann.app)

## License

This project is licensed under the MIT License.
