"""Boltzmann CLI - Auth commands"""

import requests
import click

from boltzmann_cli.client import BoltzmannClient, AuthError, APIError


def check_auth_status(client: BoltzmannClient):
    if not client.token and not client.api_key:
        click.echo("Not authenticated. Set BOLTZMANN_API_KEY or run 'boltzmann login'.")
        return
    try:
        data = client.get("/v1/auth/me")
        click.echo(f"Authenticated as: {data.get('email', 'unknown')}")
        click.echo(f"User ID:          {data.get('sub', data.get('id', 'unknown'))}")
        click.echo(f"Auth method:      {'API key' if client.api_key else 'Bearer token'}")
    except (AuthError, APIError) as e:
        click.echo(str(e), err=True)


def get_token(api_url, email, password):
    """Get a Bearer token via email/password login."""
    try:
        response = requests.post(
            f"{api_url}/v1/auth/login",
            headers={"Content-Type": "application/json"},
            json={"email": email, "password": password},
            timeout=10,
        )
        response.raise_for_status()
        data = response.json()
        token = data.get("access_token") or data.get("token")
        if token:
            click.echo("Authentication successful!")
            return token
        click.echo("No token in response.", err=True)
        return None
    except requests.RequestException as e:
        click.echo(f"Authentication failed: {e}", err=True)
        return None
