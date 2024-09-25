from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Optional

import keyring
import typer


class KeyNotFoundError(Exception): ...


@dataclass
class Config:
    directory: Path = Path.home() / ".config" / "mbx"
    file: Path = directory / "config.json"
    nocodb_token: Optional[str] = ""
    nocodb_url: Optional[str] = "http://localhost:8080"

    def __post_init__(self):
        self.directory = self.parse_as_path(self.directory)
        self.file = self.parse_as_path(self.file)

    @staticmethod
    def parse_as_path(f: Path | str | None) -> Path:
        try:
            return Path(f)
        except TypeError:
            return None

    def read(self) -> dict[str, str]:
        with open(self.file, "r") as json_file:
            dat = json.load(json_file)

        return dat

    def write(self) -> None:
        with open(self.file.expanduser(), "w") as json_file:
            out = {}
            for k, v in asdict(self).items():
                if isinstance(v, Path):
                    v = str(v)

                if "key" not in k:
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

        nocodb_token = keyring.get_password("mbx", "nocodb_token")

        if nocodb_token:
            data.update({"nocodb_token": nocodb_token})

        return cls(**data)
