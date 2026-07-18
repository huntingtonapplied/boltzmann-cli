"""Boltzmann CLI - Jobs commands"""

import click
from tabulate import tabulate

from boltzmann_cli.client import BoltzmannClient, AuthError, APIError


def list_jobs(client: BoltzmannClient, status, limit):
    try:
        params = {"limit": limit}
        if status:
            params["status"] = status
        data = client.get("/v1/orchestration/jobs", params=params)
        jobs = data.get("jobs", data.get("items", []))
        if not jobs:
            click.echo("No jobs found.")
            return
        rows = [
            [j.get("id", "")[:8], j.get("status", ""), j.get("type", ""), j.get("created_at", "")]
            for j in jobs
        ]
        click.echo(tabulate(rows, headers=["ID", "Status", "Type", "Created"]))
    except (AuthError, APIError) as e:
        click.echo(str(e), err=True)


def get_job_status(client: BoltzmannClient, job_id):
    try:
        data = client.get(f"/v1/orchestration/jobs/{job_id}")
        click.echo(f"Job:    {data.get('id', job_id)}")
        click.echo(f"Status: {data.get('status', 'unknown')}")
        click.echo(f"Type:   {data.get('type', 'unknown')}")
        if data.get("result"):
            click.echo(f"Result: {data['result']}")
        if data.get("error"):
            click.echo(f"Error:  {data['error']}", err=True)
    except (AuthError, APIError) as e:
        click.echo(str(e), err=True)
