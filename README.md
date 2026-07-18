# Boltzmann CLI

Command-line interface for the Boltzmann multiphysics simulation platform.

## Install

```bash
pip install -e cli/    # from boltzmann repo root
# or
pip install boltzmann-cli   # from PyPI (when published)
```

Standalone binary (no Python required):

```bash
curl -fsSL https://downloads.boltzmann.app/cli/install.sh | bash -s -- --version <version>
```

## Quick Start

```bash
# Authenticate
boltzmann login
# Enter your API key from app.boltzmann.ai → Account → Developer

# Check your setup
boltzmann doctor

# List your simulations
boltzmann simulations list

# Create a simulation
boltzmann simulations create my-sim --type electromagnetic

# Check simulation status
boltzmann simulations status <simulation_id>

# List your projects
boltzmann projects list

# Manage API keys
boltzmann api-keys list
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

## Global Options

- `--output/-o {table,json,yaml}` — output format (default: table)
- `--no-color` — disable colored output (also honors `NO_COLOR`)
- `--verbose/-v` — INFO-level logging to stderr
- `--debug` — DEBUG-level logging (HTTP requests)
- `--ci` — CI mode: no color, no spinners, no prompts (auto-detected from `CI`, `GITHUB_ACTIONS`, `GITLAB_CI`)

## Configuration

Config stored in `~/.boltzmann/config.yaml`:

```yaml
api_key: bz_live_abc123...
api_url: http://localhost:8009  # optional, for self-hosted
```

Environment variables override config:
- `BOLTZMANN_API_KEY` — API key
- `BOLTZMANN_API_URL` — API base URL
- `BOLTZMANN_MAX_RETRIES` — retry attempts for transient failures (default: 3)
- `BOLTZMANN_TIMEOUT` — request timeout in seconds (default: 30)
- `BOLTZMANN_NO_UPDATE_CHECK` — disable the background version check

## Exit Codes

| Code | Meaning |
|------|---------|
| 0 | Success |
| 1 | General error |
| 2 | Authentication error |
| 3 | Not found |
| 4 | Validation error |
| 5 | Network error |
| 6 | Server error |
| 7 | Duplicate |
| 130 | Interrupted (SIGINT) |
| 143 | Terminated (SIGTERM) |

## Development

```bash
# Install in dev mode
pip install -e cli/

# Run tests
cd cli/
pip install -e ".[test]"
pytest -q

# Lint
ruff check boltzmann_cli/
```

## Distribution

```bash
make build-binary   # standalone binary into dist/ (PyInstaller)
make build-wheel    # wheel/sdist into dist/
make smoke          # build binary and run --help
```

See [`.sega/README.md`](.sega/README.md) for publishing binaries via SEGA.
