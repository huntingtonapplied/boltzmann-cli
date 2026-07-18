"""Boltzmann CLI - Projects commands"""

import click
from tabulate import tabulate

from boltzmann_cli.client import BoltzmannClient, AuthError, APIError


def list_projects(client: BoltzmannClient, visibility, limit):
    try:
        params = {"limit": limit}
        if visibility:
            params["visibility"] = visibility
        data = client.get("/v1/projects", params=params)
        projects = data.get("projects", data.get("items", []))
        if not projects:
            click.echo("No projects found.")
            return
        rows = [
            [p.get("id", "")[:8], p.get("name", ""), p.get("visibility", ""), p.get("created_at", "")]
            for p in projects
        ]
        click.echo(tabulate(rows, headers=["ID", "Name", "Visibility", "Created"]))
    except (AuthError, APIError) as e:
        click.echo(str(e), err=True)


def create_project(client: BoltzmannClient, name, description, visibility):
    try:
        payload = {"name": name, "visibility": visibility}
        if description:
            payload["description"] = description
        data = client.post("/v1/projects", data=payload)
        click.echo(f"Project created: {data.get('id', 'unknown')}")
    except (AuthError, APIError) as e:
        click.echo(str(e), err=True)
