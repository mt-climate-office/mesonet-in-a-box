# mesonet-in-a-box
An All-In-One Tool for Managing Mesonets. Each directory starting with `mbx-` is a standalone module that can be spun up as a docker-compose service. Each `mbx-` directory is a git submodule that is pointing to another repository. To make sure submodules are up-to-date, run the following steps when cloning or pulling:

1. Clone the repository: `git clone https://github.com/mt-climate-office/mesonet-in-a-box.git`
2. Initialize the submodules and get them up to date: 
```bash
git submodule sync --recursive
git submodule update --init --remote --recursive
```
3. Alternatively, you can run `./pull.sh`, which will both pull from the main repo, and run the above two commands.

# Start All Services
1. Run `docker network create web`
2. Run `docker compose up --build -d`
3. Install [uv](https://docs.astral.sh/uv/) to manage python dependencies: `curl -LsSf https://astral.sh/uv/install.sh | sh`
4. Initialize virtual environment with `uv sync`.
5. Configure the `mbx` command line tool by running: `uv run mbx --no-check configure`.


# To Migrate from AirTable:
1. On home AirTable page, click the `...` next to the Montana Mesonet base and click "Duplicate base". Name the new base "mbx_copy".
2. Make sure you have an AirTable [API token](https://support.airtable.com/docs/creating-personal-access-tokens) with read/write permissions to the mbx_copy base.
    - Store the key as an environment variable called "AIRTABLE_API_KEY".
3. Open the new base, and click the `Share` icon in the top right corner of the screen. `Share publicly` > `Enable shared base link (read-only)`. Copy the URL that is generated.
4. Edit every `id` field that is a formula type. Formulas aren't supported in AirTable > NocoDB migrations. For each table, right click the formula field > Edit Field > Change the dropdown to "Autonumber".
5. Go to [http://localhost:8080](http://localhost:8080) or whatever domain NocoDB is being hosted on and login.
    - On the homepage, click `Create Base` and name it `Montana Mesonet`.
    - In the new base, click the `Import Data` button and choose `AirTable`.
    - Paste in the url generated above and your API key. Uncheck `Import Secondary Views`.
    - Click `Import`.
6. Run `uv run mbx create-schema-from-existing` and select the "Montana Mesonet" base when prompted. This will print out a file path. Copy this path for the next step.
7. Run `uv run mbx clean-nc-tables the/path/you/copied.json`. This command re-creates old formulas, sets primary column values, and rolls all columns that aren't used in mesonet-in-a-box into a JSON column so that information is maintained.    