from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Optional

import typer


@dataclass
class Config:
    directory: Optional[Path] = Path.home() / ".config" / "mesonet"
    file: Optional[Path] = Path.home() / ".config" / "mesonet/config.json"
    airtable_token: Optional[str] = None
    data_dir: Optional[Path] = None
    env_file: Optional[Path] = None

    def __post_init__(self) -> None:
        self.directory = self.parse_as_path(self.directory)
        self.file = self.parse_as_path(self.file)
        self.data_dir = self.parse_as_path(self.data_dir)
        self.env_file = self.parse_as_path(self.env_file)

    @staticmethod
    def parse_as_path(f: Optional[Path | str]) -> Optional[Path]:
        if f is None:
            return None

        try:
            return Path(f).absolute()
        except TypeError:
            return None

    def read(self) -> Optional[dict[str, str]]:
        if self.file is None:
            raise ValueError(
                "The file attribute if None. Please run `mesonet configure`."
            )
        with open(self.file, "r") as json_file:
            dat = json.load(json_file)

        return dat

    def write(self) -> None:
        if self.file is None:
            raise ValueError(
                "The file attribute if None. Please run `mesonet configure`."
            )
        with open(self.file.expanduser(), "w") as json_file:
            json.dump(
                {
                    k: str(v) if isinstance(v, Path) else v
                    for k, v in asdict(self).items()
                },
                json_file,
            )

    def create(self) -> Path:
        if self.directory is None:
            raise ValueError(
                "The directory attribute if None. Please run `mesonet configure`."
            )
        try:
            self.directory.mkdir(parents=True, exist_ok=False)
        except FileExistsError:
            typer.echo(f"{self.directory} already exists. Skipping creation.\n")

        return self.directory

    @property
    def exists(self) -> bool:
        if self.file is None:
            return False
        return self.file.exists()

    @classmethod
    def load(cls, file) -> Config:
        try:
            with open(file, "r") as json_file:
                data = json.load(json_file)
        except (TypeError, FileNotFoundError):
            data = {}

        return cls(**data)
