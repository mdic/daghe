import subprocess
from pathlib import Path
from typing import List

from core.system import get_clean_env


def sync_module_venv(module_path: Path) -> subprocess.CompletedProcess:
    """
    Synchronises the uv virtual environment for a module.
    UK English spelling. Uses cleaned environment for isolation.
    """
    return subprocess.run(["uv", "sync"], cwd=module_path, env=get_clean_env())


def upgrade_module_packages(module_path: Path, packages: List[str]) -> None:
    """
    Upgrades specific packages within a module's uv environment.
    UK English spelling. Iterates through the package list and runs 'uv add --upgrade'.
    """
    env = get_clean_env()
    for pkg in packages:
        # Matches legacy behaviour: executes without forced check=True
        subprocess.run(["uv", "add", "--upgrade", pkg], cwd=module_path, env=env)
