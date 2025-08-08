from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Literal

import keyring
import typer


class KeyNotFoundError(Exception): ...


@dataclass
class Config:
    directory: Path = Path.home() / ".config" / "mbx"
    file: Path = directory / "config.json"
    env_file: Path = Path.cwd() / ".env"
    inventory_backend: Literal["airtable", "nocodb", "baserow"] = "airtable"
    backend_token: str = ""
    backend_base_id: str = ""

    def __post_init__(self):
        self.directory = self.parse_as_path(self.directory)
        self.file = self.parse_as_path(self.file)
        self.env_file = self.parse_as_path(self.env_file)

    @staticmethod
    def parse_as_path(f: Path | str | None) -> Path:
        try:
            return Path(f)
        except TypeError:
            return None

    def write(self) -> None:
        with open(self.file.expanduser(), "w") as json_file:
            out = {}
            for k, v in asdict(self).items():
                if isinstance(v, Path):
                    v = str(v)

                if k == "backend_token":
                    keyring.set_password("mbx", "backend_token", v)
                else:
                    out[k] = v

            json.dump(
                out,
                json_file,
            )

    def create(self) -> Path:
        try:
            self.directory.mkdir(parents=True, exist_ok=False)
        except FileExistsError:
            typer.echo(f"{self.directory} already exists. Skipping creation.\n")

        return self.directory

    @property
    def exists(self) -> bool:
        return self.file.exists()

    @classmethod
    def load(cls, file) -> Config:
        try:
            with open(file, "r") as json_file:
                data = json.load(json_file)
        except (TypeError, FileNotFoundError):
            data = {}

        backend_token = keyring.get_password("mbx", "backend_token")

        if backend_token:
            data.update({"backend_token": backend_token})

        return cls(**data)
