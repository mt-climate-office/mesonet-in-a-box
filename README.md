# mesonet-in-a-box
An All-In-One Tool for Managing Mesonets. Each directory starting with `mbx-` is a standalone module that can be spun up as a docker-compose service. Each `mbx-` directory is a git submodule that is pointing to another repository. To make sure submodules are up-to-date, run the following steps when cloning or pulling:

1. Clone the repository: `https://github.com/mt-climate-office/mesonet-in-a-box.git`
2. Initialize the submodules and get them up to date: 
```bash
git submodule sync --recursive
git submodule update --init --remote --recursive
```

# Start All Services
1. Run `docker network create web`
2. Run `docker compose up --build -d`
3. Install [uv](https://docs.astral.sh/uv/) to manage python dependencies: `curl -LsSf https://astral.sh/uv/install.sh | sh`
4. Initialize virtual environment with `uv sync`.
5. Configure the `mbx` command line tool by running: `uv run mbx --no-check configure`.