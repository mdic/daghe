from dataclasses import dataclass
from pathlib import Path

import yaml


@dataclass
class JobConfig:
    raw: dict

    @property
    def data_dir(self) -> Path:
        return Path(self.raw["paths"]["data_dir"])

    @property
    def archive_file(self) -> Path:
        return Path(self.raw["paths"]["archive_file"])

    @property
    def telegram_helper(self) -> str:
        return self.raw["paths"]["telegram_helper"]

    def get(self, *keys, default=None):
        data = self.raw
        for key in keys:
            if isinstance(data, dict):
                data = data.get(key)
            else:
                return default
        return data if data is not None else default


def load_config(path: str) -> JobConfig:
    with open(path, "r") as f:
        return JobConfig(yaml.safe_load(f))
