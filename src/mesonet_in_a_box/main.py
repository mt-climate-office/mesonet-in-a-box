from mbx_db.cli import app as db_app
from .config import Config

import typer
from pathlib import Path
from dotenv import load_dotenv
from typing import Optional

load_dotenv()
CONFIG = Config.load(Config.file)


def callback(
    check: Optional[bool] = typer.Option(
        True,
        "--check/--no-check",
        help="Should your NocoDB token be checked before running a command?",
    ),
):
    """
    Command line interface for all Mesonet-in-a-Box utilities.
    """
    ...


app = typer.Typer(rich_markup_mode="rich", callback=callback)
app.add_typer(db_app, name="db")

@app.command()
def configure():
    """Create a configuration file that all other `mbx` commands will reference.
    Please run this command before running any other `mbx` commands.
    """
    CONFIG.create()
    if not CONFIG.env_file:
        env_file = typer.prompt("Please enter the path to the .env file for your project...", type=Path)
        CONFIG.env_file = env_file
    
    if not CONFIG.env_file.exists():
        typer.echo(f"{CONFIG.env_file} does not exist. Please either create or modify path. Exiting...")
        raise typer.Exit()
    
    CONFIG.write()
    typer.echo(f"Your config file has been written to {CONFIG.file.expanduser()}.")
