from mbx_inventory import create_db_schema as create
from mbx_inventory.schemas import TABLES, BaseSchema
from .config import Config

import typer
from dotenv import load_dotenv
import os
import keyring

load_dotenv()
CONFIG = Config.load(Config.file)

app = typer.Typer(rich_markup_mode="rich")


@app.command()
def configure():
    """Create a configuration file that all other `mbx` commands will reference.
    Please run this command before running any other `mbx` commands.
    """
    CONFIG.create()
    nocodb_key = os.getenv("NOCODB_TOKEN")
    if not nocodb_key:
        nocodb_key = typer.prompt(
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
        api_key=nocodb_key, nocodb_url=CONFIG.nocodb_url
    )

    if not key_works:
        typer.echo(
            f"Not able to communicate with NocoDB using provided token at {nocodb_host}. Terminating configuration."
        )
        typer.Abort()

    keyring.set_password("mbx", "nocodb_key", nocodb_key)

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
        api_key=CONFIG.nocodb_key,
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
        api_key=CONFIG.nocodb_key,
        nocodb_url=CONFIG.nocodb_url,
        db_base_name=base_name,
    )

    tables = create.create_base_tables(
        tables=TABLES,
        base_id=base_id,
        api_key=CONFIG.nocodb_key,
        nocodb_url=CONFIG.nocodb_url,
    )

    base_schema = BaseSchema(tables)
    base_schema.match_relationship_column_ids()
    base_schema = create.populate_table_relationships(
        base_schema=base_schema, api_key=CONFIG.nocodb_key, nocodb_url=CONFIG.nocodb_url
    )
