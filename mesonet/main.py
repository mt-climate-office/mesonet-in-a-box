from mesonet_utils import Config, check_airtable_token
from typing import Optional
from pathlib import Path

import os
from shutil import copy


import typer

CONFIG = Config.load(Config.file)


def callback(
    check: Optional[bool] = typer.Option(
        True,
        "--check/--no-check",
        help="Should GitHub and AirTable credentials be checked before running the command?",
    ),
):
    """
    Configuration and deployment of LoggerNet stations to the Montana Mesonet LoggerNet server, AirTable, database, and API.

    [bold]Note:[/bold] You must have an AirTable Personal Access Token to use this application (learn more [link=https://support.airtable.com/docs/creating-and-using-api-keys-and-access-tokens#personal-access-tokens-basic-actions]here[/link]).
    The token must be stored as an environment variable called "AIRTABLE_API_KEY" (learn more [link=https://www.twilio.com/blog/2017/01/how-to-set-environment-variables.html]here[/link]).
    """

    if check:
        typer.echo("Checking that AirTable key works...\n")
        if not check_airtable_token(CONFIG.airtable_token):
            typer.echo(
                "AirTable API key is not valid. Please reset with `mesonet --no-check configure`."
            )
            raise typer.Abort()


app = typer.Typer(rich_markup_mode="rich", callback=callback)


@app.command()
def configure(
    data_dir: Path = typer.Option(
        default=None, help="Optional path where project data will be stored."
    ),
):
    """A command to configure global settings to be used in the `mesonet-config` project. Run this command
    before using any of `mesonet-config`'s other functionality.
    """

    CONFIG.create()

    api_key = os.getenv("AIRTABLE_API_KEY")

    if not api_key:
        api_key = typer.prompt(
            "No environment variable called 'AIRTABLE_API_KEY' was found. Please provide your AirTable read/write token"
        )
    else:
        typer.echo("An AirTable API token was found in your environment variables!\n")

    CONFIG.airtable_token = api_key
    if data_dir is None:
        while True:
            data_dir = typer.prompt(
                "Please enter the path to the directory you would like to store app data in. Defaults to",
                default=CONFIG.directory,
            )

            data_dir = Path(data_dir).expanduser()
            if data_dir.exists():
                break
            else:
                typer.echo(
                    f"{data_dir} does not exist. Please enter a valid directory."
                )

    proceed = typer.confirm(
        f"\nA folder called 'assets' will be created in {data_dir}. If one already exists, it will be deleted. Do you want to proceed?"
    )

    if not proceed:
        typer.echo("Stopping configuration. Please repeat using a new data directory.")
        typer.Abort()

    CONFIG.data_dir = data_dir

    at_schema = typer.prompt(
        "Where is the `at_schema.json` file defining your AirTable schema located? Defaults to",
        default="./at_schema.json",
    )

    copy(Path(at_schema).expanduser(), CONFIG.directory)

    env_file = typer.prompt(
        "Where is the .env file located that has all tokens and passwords needed for your project? Defaults to",
        default="./.env",
    )

    CONFIG.env_file = Path(env_file).absolute()
    CONFIG.write()
