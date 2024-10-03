from mbx_inventory import create_db_schema as create
from mbx_inventory.schemas import TABLES, BaseSchema
from mbx_inventory.at_migration import nc
from .config import Config

import typer
from dotenv import load_dotenv
import os
import keyring
from typing import Optional
from typing_extensions import Annotated
import httpx
from pathlib import Path

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
    [bold]Note:[/bold] You must have a NocoDB access toekn to use this application.
    The token should be stored in a .env file or as an environment variable called `NOCODB_TOKEN`.
    """

    if check:
        typer.echo("Checking that NocoDB key works...\n")
        try:
            create.get_nocodb_bases(
                nocodb_token=CONFIG.nocodb_token, nocodb_url=CONFIG.nocodb_url
            )
        except httpx.RequestError:
            typer.echo(
                f"Unable to access NocoDB at {CONFIG.nocodb_url}. Please rerun `mbx --no-check configure`."
            )
            raise typer.Abort()


app = typer.Typer(rich_markup_mode="rich", callback=callback)


@app.command()
def configure():
    """Create a configuration file that all other `mbx` commands will reference.
    Please run this command before running any other `mbx` commands.
    """
    CONFIG.create()
    nocodb_token = os.getenv("NOCODB_TOKEN")
    if not nocodb_token:
        nocodb_token = typer.prompt(
            "No environment variable called 'NOCODB_TOKEN' was found. Please provide your NocoDB read/write token"
        )

    change_host = typer.confirm(
        "NocoDB url defaults to 'http://localhost:8080'. Do you want to change the host url?"
    )

    if change_host:
        nocodb_host = typer.prompt(
            "Please enter the URL where your NocoDB container is hosted"
        )

        CONFIG.nocodb_url = nocodb_host

    key_works = create.get_nocodb_bases(
        nocodb_token=nocodb_token, nocodb_url=CONFIG.nocodb_url
    )

    if not key_works:
        typer.echo(
            f"Not able to communicate with NocoDB using provided token at {nocodb_host}. Terminating configuration."
        )
        raise typer.Abort()

    keyring.set_password("mbx", "nocodb_token", nocodb_token)

    CONFIG.write()
    typer.echo(f"Your config file has been written to {CONFIG.file.expanduser()}.")


@app.command()
def init_nocodb(
    base_name: str = typer.Argument(
        "Mesonet",
        help="The name that will be assigned to your NocoDB base storing all mesonet-related tables.",
    ),
):
    """Initialize NocoDB mesonet dashboard with all necessary tables and relationships."""

    existing_bases = create.get_nocodb_bases(
        nocodb_token=CONFIG.nocodb_token,
        nocodb_url=CONFIG.nocodb_url,
    )

    for base in existing_bases.json()["list"]:
        base_title = base["title"]
        base_id = base["id"]
        if base_title == base_name:
            rename_base = typer.confirm(
                f"An existing base with name {base_title} and id {base_id} was found. Would you like to continue (new name required)?"
            )
            if rename_base:
                base_name = typer.prompt("Please enter the new base name")

                assert (
                    base_name != base_title
                ), "New base name is still equal to existing name."

    base_id = create.create_mesonet_base(
        nocodb_token=CONFIG.nocodb_token,
        nocodb_url=CONFIG.nocodb_url,
        db_base_name=base_name,
    )

    tables = create.create_base_tables(
        tables=TABLES,
        base_id=base_id,
        nocodb_token=CONFIG.nocodb_token,
        nocodb_url=CONFIG.nocodb_url,
    )

    base_schema = BaseSchema(
        base_id,
        tables
    )

    base_schema.match_relationship_column_ids()
    base_schema = create.populate_relationships_lookups_formulas(
        column_type="relationships",
        base_schema=base_schema,
        nocodb_token=CONFIG.nocodb_token,
        nocodb_url=CONFIG.nocodb_url,
    )

    base_schema.match_lookup_column_ids()
    base_schema = create.populate_relationships_lookups_formulas(
        column_type="lookups",
        base_schema=base_schema,
        nocodb_token=CONFIG.nocodb_token,
        nocodb_url=CONFIG.nocodb_url,
    )
    base_schema = create.populate_relationships_lookups_formulas(
        column_type="formulas",
        base_schema=base_schema,
        nocodb_token=CONFIG.nocodb_token,
        nocodb_url=CONFIG.nocodb_url,
    )

    create.create_primary_columns(
        base_schema=base_schema,
        nocodb_token=CONFIG.nocodb_token,
        nocodb_url=CONFIG.nocodb_url,
    )

    base_schema.save(Path(CONFIG.directory) / f"{base_schema.base_id}.json")


@app.command()
def create_schema_from_existing():
    bases = create.list_bases(
        nocodb_token=CONFIG.nocodb_token, nocodb_url=CONFIG.nocodb_url
    )

    options = [x["title"] for x in bases["list"]]
    options = [f"{idx}: {x}" for idx, x in enumerate(options)]
    choice = typer.prompt(
        f"Please choose one of the following bases to build schema for:\n{'\n'.join(options)}\n",
        type=int,
        prompt_suffix="",
    )

    assert choice in range(
        len(options)
    ), f"Your choice must be in {range(len(options))}. Please try again."

    base_id = bases["list"][choice]["id"]
    tables = create.create_tables_from_base(
        base_id, nocodb_token=CONFIG.nocodb_token, nocodb_url=CONFIG.nocodb_url
    )

    base_schema = BaseSchema(base_id, tables)
    out_path = Path(CONFIG.directory) / f"{base_schema.base_id}.json"
    base_schema.save(out_path)

    typer.echo(f"Base shema has been saved to {out_path}")


@app.command()
def clean_nc_tables(pth: Annotated[Path, typer.Argument()]):
    base_schema = BaseSchema.load(pth)
    nc.fix_stations_table(base_schema=base_schema)


# configure()