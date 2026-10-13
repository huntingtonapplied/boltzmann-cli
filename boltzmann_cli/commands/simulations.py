"""Boltzmann CLI - Simulations commands"""

import json
import click
from tabulate import tabulate

from boltzmann_cli.client import BoltzmannClient, AuthError, APIError


def list_simulations(client: BoltzmannClient, status, limit, offset):
    try:
        params = {"limit": limit, "offset": offset}
        if status:
            params["status"] = status
        data = client.get("/v1/simulations", params=params)
        # /v1/simulations returns a bare List[SimulationListItem]; guard the
        # dict-shaped fallback so `.get()` never runs on a list (U12 — mirrors
        # jobs.py/projects.py).
        simulations = data if isinstance(data, list) else data.get("simulations", data.get("items", []))
        if not simulations:
            click.echo("No simulations found.")
            return
        rows = [
            [s.get("id", "")[:8], s.get("name", ""), s.get("status", ""), s.get("created_at", "")]
            for s in simulations
        ]
        click.echo(tabulate(rows, headers=["ID", "Name", "Status", "Created"]))
    except (AuthError, APIError) as e:
        click.echo(str(e), err=True)


def create_simulation(client: BoltzmannClient, name, sim_type, config_file):
    try:
        payload = {"name": name, "type": sim_type}
        if config_file:
            with open(config_file) as f:
                payload["config"] = json.load(f)
        data = client.post("/v1/simulations", data=payload)
        click.echo(f"Simulation created: {data.get('id', 'unknown')}")
    except (AuthError, APIError) as e:
        click.echo(str(e), err=True)


def get_simulation_status(client: BoltzmannClient, simulation_id):
    try:
        data = client.get(f"/v1/simulations/{simulation_id}")
        click.echo(f"Simulation: {data.get('name', simulation_id)}")
        click.echo(f"Status:     {data.get('status', 'unknown')}")
        click.echo(f"Progress:   {data.get('progress', 0)}%")
        if data.get("error"):
            click.echo(f"Error: {data['error']}", err=True)
    except (AuthError, APIError) as e:
        click.echo(str(e), err=True)


def stop_simulation(client: BoltzmannClient, simulation_id):
    try:
        client.post(f"/v1/simulations/{simulation_id}/stop")
        click.echo(f"Simulation {simulation_id} stopped.")
    except (AuthError, APIError) as e:
        click.echo(str(e), err=True)
