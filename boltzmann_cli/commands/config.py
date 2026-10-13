"""
Boltzmann CLI - Config commands
"""

import os
import yaml
from pathlib import Path
import httpx
import click


def show_config(section=None):
    """Show current configuration."""
    from boltzmann_cli.config import CONFIG_FILE, load_config

    # Show persistent config from ~/.boltzmann/config.yaml
    stored = load_config()
    if stored:
        click.echo(f"~/.boltzmann/config.yaml:")
        for key, value in stored.items():
            if key == "api_key":
                display = f"{value[:12]}..." if value else "<empty>"
            else:
                display = value or "<empty>"
            click.echo(f"  {key}={display}")
    else:
        click.echo(f"~/.boltzmann/config.yaml: (not set — run 'boltzmann api-keys create')")

    # Also show relevant env/dotenv vars
    env_file = Path(__file__).parent.parent.parent.parent / ".env"
    if not env_file.exists():
        return

    config = {}
    with open(env_file) as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith("#"):
                if "=" in line:
                    key, value = line.split("=", 1)
                    config[key.strip()] = value.strip()

    if not config:
        return

    if section:
        relevant_keys = {
            "api": ["API_URL", "BOLTZMANN_API_URL", "AUTH0_DOMAIN", "AUTH0_AUDIENCE"],
            "auth": ["AUTH0_DOMAIN", "AUTH0_CLIENT_ID", "DEV_AUTH_BYPASS", "BOLTZMANN_API_KEY"],
            "database": ["DATABASE_URL", "REDIS_URL", "TIMESCALEDB_URL"],
        }

        keys = relevant_keys.get(section, [])
        shown = False
        for key in keys:
            if key in config:
                if not shown:
                    click.echo("\n.env:")
                    shown = True
                display_value = config[key]
                if "PASSWORD" in key or "SECRET" in key or "API_KEY" in key:
                    display_value = "***"
                click.echo(f"  {key}={display_value}")
    else:
        click.echo("\n.env:")
        for key, value in config.items():
            if "PASSWORD" in key or "SECRET" in key or "API_KEY" in key:
                display_value = "***"
            else:
                display_value = value if value else "<empty>"
            click.echo(f"  {key}={display_value}")


def validate_config(api_url):
    """Validate configuration by checking API health."""
    try:
        response = httpx.get(f"{api_url}/health", timeout=5, follow_redirects=True)
        response.raise_for_status()

        data = response.json()
        click.echo(f"API Status: {data.get('status', 'unknown')}")
        click.echo("Configuration is valid.")

    except httpx.HTTPError as e:
        click.echo(f"Configuration validation failed: {e}", err=True)