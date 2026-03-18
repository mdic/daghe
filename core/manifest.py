from pathlib import Path
from typing import Any

import yaml


class ManifestError(Exception):
    """Base exception for manifest-related errors."""

    pass


class ManifestNotFoundError(ManifestError):
    """Raised when the manifest file does not exist on disk."""

    pass


class ManifestEmptyError(ManifestError):
    """Raised when the manifest file is empty or invalid."""

    pass


def load_manifest_file(path: Path) -> Any:
    """
    Low-level helper to open and parse a YAML file.
    UK English spelling. Returns the parsed object (usually a dict)
    or None if the file is empty.
    """
    with open(path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def get_manifest_path(jobs_dir: Path, module_name: str) -> Path:
    """
    Construct the absolute path to a module's manifest file.
    UK English spelling. Assumes module_name is already sanitised.
    """
    return jobs_dir / module_name / "current" / "daghe-module.yaml"


def load_module_manifest(jobs_dir: Path, module_name: str) -> dict:
    """
    High-level loader for a module manifest.
    UK English spelling. Aggregates path resolution, existence check, and parsing.
    Assumes module_name is already sanitised.
    Raises ManifestNotFoundError or ManifestEmptyError on failure.
    """
    path = get_manifest_path(jobs_dir, module_name)

    if not path.exists():
        raise ManifestNotFoundError(f"Manifest missing at: {path}")

    data = load_manifest_file(path)

    if data is None:
        raise ManifestEmptyError(f"Manifest file is empty: {path}")

    # Standardise return type to dict as per current CLI expectations
    if not isinstance(data, dict):
        raise ManifestEmptyError(f"Manifest at {path} did not parse as a dictionary")

    return data
