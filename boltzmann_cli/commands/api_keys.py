"""Boltzmann CLI - API key management commands"""

import sys
from datetime import datetime, timezone, timedelta

import click
from tabulate import tabulate

from boltzmann_cli.client import BoltzmannClient, AuthError, APIError
from boltzmann_cli.config import set_api_key


def _require_auth(client: BoltzmannClient):
    if not client.token and not client.api_key:
        click.echo(
            "Not authenticated. Set BOLTZMANN_API_KEY or run 'boltzmann login'.",
            err=True,
        )
        sys.exit(1)


def list_api_keys(client: BoltzmannClient):
    _require_auth(client)
    try:
        data = client.get("/v1/api-keys")
        keys = data if isinstance(data, list) else data.get("items", data.get("api_keys", []))
        if not keys:
            click.echo("No API keys found.")
            return
        rows = [
            [
                k.get("id", "")[:8],
                k.get("name", ""),
                k.get("key_prefix", ""),
                k.get("status", ""),
                k.get("last_used_at") or "never",
                k.get("request_count", 0),
                str(k.get("expires_at") or "never"),
            ]
            for k in keys
        ]
        click.echo(tabulate(rows, headers=["ID", "Name", "Prefix", "Status", "Last Used", "Requests", "Expires"]))
    except (AuthError, APIError) as e:
        click.echo(str(e), err=True)


def create_api_key(client: BoltzmannClient, name, scopes, expires_in_days):
    _require_auth(client)
    try:
        payload: dict = {"name": name, "scopes": list(scopes)}
        if expires_in_days:
            expires_at = (datetime.now(timezone.utc) + timedelta(days=expires_in_days)).isoformat()
            payload["expires_at"] = expires_at

        data = client.post("/v1/api-keys", data=payload)
        key_value = data.get("key") or data.get("full_key")

        click.echo(f"API key created: {data.get('name', name)}")
        click.echo(f"ID:     {data.get('id', 'unknown')}")
        click.echo(f"Prefix: {data.get('key_prefix', '')}")
        if key_value:
            click.echo(f"\nKey (save this — shown only once):\n  {key_value}")

        if key_value and sys.stdout.isatty():
            if click.confirm("\nSave this key to ~/.boltzmann/config.yaml?", default=False):
                set_api_key(key_value)
                click.echo("Saved.")
    except (AuthError, APIError) as e:
        click.echo(str(e), err=True)


def rotate_api_key(client: BoltzmannClient, key_id):
    _require_auth(client)
    try:
        data = client.post(f"/v1/api-keys/{key_id}/rotate")
        key_value = data.get("key") or data.get("full_key")
        click.echo(f"API key rotated: {data.get('name', key_id)}")
        click.echo(f"New prefix: {data.get('key_prefix', '')}")
        if key_value:
            click.echo(f"\nNew key (save this — shown only once):\n  {key_value}")

        if key_value and sys.stdout.isatty():
            if click.confirm("\nUpdate ~/.boltzmann/config.yaml with the new key?", default=False):
                set_api_key(key_value)
                click.echo("Saved.")
    except (AuthError, APIError) as e:
        click.echo(str(e), err=True)


def update_api_key(client: BoltzmannClient, key_id, name):
    _require_auth(client)
    try:
        payload: dict = {}
        if name:
            payload["name"] = name
        if not payload:
            click.echo("Nothing to update — provide at least --name.", err=True)
            sys.exit(1)
        data = client.patch(f"/v1/api-keys/{key_id}", data=payload)
        click.echo(f"Updated: {data.get('name', key_id)}")
    except (AuthError, APIError) as e:
        click.echo(str(e), err=True)


def revoke_api_key(client: BoltzmannClient, key_id):
    _require_auth(client)
    try:
        client.delete(f"/v1/api-keys/{key_id}")
        click.echo(f"API key {key_id} revoked.")
    except (AuthError, APIError) as e:
        click.echo(str(e), err=True)


def delete_api_key_permanent(client: BoltzmannClient, key_id):
    _require_auth(client)
    try:
        client.delete(f"/v1/api-keys/{key_id}/permanent")
        click.echo(f"API key {key_id} permanently deleted.")
    except (AuthError, APIError) as e:
        click.echo(str(e), err=True)


def show_stats(client: BoltzmannClient):
    _require_auth(client)
    try:
        data = client.get("/v1/api-keys/stats/usage")
        click.echo(f"Total keys:    {data.get('total_keys', 0)}")
        click.echo(f"Active:        {data.get('active_keys', 0)}")
        click.echo(f"Revoked:       {data.get('revoked_keys', 0)}")
        click.echo(f"Total requests:{data.get('total_requests', 0)}")
    except (AuthError, APIError) as e:
        click.echo(str(e), err=True)
