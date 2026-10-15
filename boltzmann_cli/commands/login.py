"""Boltzmann CLI - login command"""

import click

from boltzmann_cli.config import set_api_key, set_api_url, get_api_url
from boltzmann_cli.client import BoltzmannClient, AuthError, APIError


@click.command()
@click.option("--key", default=None, help="API key (skips wizard)")
@click.option("--url", default=None, help="Custom API URL")
@click.pass_context
def login(ctx, key, url):
    """Authenticate with the Boltzmann platform.

    \b
    Examples:
        boltzmann login                        # interactive wizard
        boltzmann login --key bz_live_abc123   # non-interactive
    """
    if not key:
        click.echo()
        click.echo("  Welcome to Boltzmann CLI!")
        click.echo()
        click.echo("  To get your API key:")
        click.echo("    1. Go to app.boltzmann.app → Account → Developer")
        click.echo("    2. Click 'Create API Key'")
        click.echo("    3. Copy the key and paste it below")
        click.echo()
        key = click.prompt("  API Key", hide_input=True)
        if not url and click.confirm("  Use a custom API URL?", default=False):
            url = click.prompt("  API URL", default=get_api_url())

    key = key.strip()
    set_api_key(key)
    if url:
        set_api_url(url.strip())

    api_url = url or ctx.obj.get("API_URL") or get_api_url()
    click.echo(f"✓ API key saved to ~/.boltzmann/config.yaml")

    try:
        client = BoltzmannClient(api_url, api_key=key)
        data = client.get("/v1/auth/me")
        email = data.get("email", "unknown")
        click.echo(f"✓ Authenticated as {email}")
        click.echo()
        click.echo("  Next steps:")
        click.echo("    boltzmann simulations list   list your simulations")
        click.echo("    boltzmann projects list      list your projects")
        click.echo("    boltzmann api-keys list      manage API keys")
    except (AuthError, APIError) as e:
        click.echo(f"⚠ Key saved but verification failed: {e}", err=True)
        click.echo("  Check your key and try: boltzmann login --key <key>", err=True)
