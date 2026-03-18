import subprocess
from pathlib import Path

from core.system import get_clean_env


def sync_module_venv(module_path: Path) -> subprocess.CompletedProcess:
    """
    Synchronises the uv virtual environment for a module.
    UK English spelling. Uses cleaned environment for isolation.
    """
    return subprocess.run(["uv", "sync"], cwd=module_path, env=get_clean_env())
