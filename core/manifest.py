from pathlib import Path
from typing import Any

import yaml


def load_manifest_file(path: Path) -> Any:
    """
    Low-level helper to open and parse a YAML file.
    UK English spelling. Returns the parsed object (usually a dict)
    or None if the file is empty.
    """
    with open(path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)
