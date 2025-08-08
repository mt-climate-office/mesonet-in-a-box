import click

from mbx_db.cli import app as db_app
from mbx_inventory import backends
from .config import Config

import typer
from pathlib import Path


def callback():
    """
    Command line interface for all Mesonet-in-a-Box utilities.
    """
    ...


app = typer.Typer(rich_markup_mode="rich", callback=callback)
app.add_typer(db_app, name="db")


@app.command()
def wipe():
    """Wipe current configuration file. Recommended to use after major changes that could
    break package functionality.
    """
    f = Config.file
    if f.exists():
        f.unlink()
        typer.echo(f"Deleted configuration file: {f}")
    else:
        typer.echo("No configuration file found to delete.")


@app.command()
def configure():
    """Create a configuration file that all other `mbx` commands will reference.
    Please run this command before running any other `mbx` commands.
    """
    CONFIG = Config.load(Config.file)

    CONFIG.create()
    if not CONFIG.env_file:
        env_file = typer.prompt(
            "Please enter the path to the .env file for your project...", type=Path
        )
        CONFIG.env_file = env_file

    if not CONFIG.env_file.exists():
        typer.echo(
            f"{CONFIG.env_file} does not exist. Please either create or modify path. Exiting..."
        )
        raise typer.Exit()

    backend_choices = click.Choice(["airtable", "nocodb", "baserow"])
    backend: click.Choice = typer.prompt(
        "Which inventory backend are you using.", "airtable", type=backend_choices
    )

    token = typer.prompt("Please enter your API token for your selected backend...")
    base_id = typer.prompt("Please enter the ID of your backend's base")
    CONFIG.inventory_backend = backend
    CONFIG.backend_token = token
    CONFIG.backend_base_id = base_id

    match backend:
        case "airtable":
            backend = backends.AirtableBackend(token, base_id)
        case "nocodb":
            backend = backends.NocoDBBackend(token, base_id)
        case "baserow":
            backend = backends.BaserowBackend(token, base_id)

    if not backend.validate():
        typer.echo(
            "Inventory backend validation failed. Please check your token and base ID"
        )
        raise typer.Exit()

    typer.echo(f"Your config file has been written to {CONFIG.file.expanduser()}.")
