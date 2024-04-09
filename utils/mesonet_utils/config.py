from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Optional

import typer


@dataclass
class Config:
    directory: Path = Path.home() / ".config" / "mesonet"
    file: Path = Path.home() / ".config" / "mesonet/config.json"
    airtable_token: Optional[str] = None
    data_dir: Optional[Path] = None

    def __post_init__(self):
        self.directory = self.parse_as_path(self.directory)
        self.file = self.parse_as_path(self.file)
        self.data_dir = self.parse_as_path(self.data_dir)

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
            json.dump(
                {
                    k: str(v) if isinstance(v, Path) else v
                    for k, v in asdict(self).items()
                },
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

        return cls(**data)
