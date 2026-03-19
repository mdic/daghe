import subprocess
from pathlib import Path
from typing import List

from core.system import get_clean_env


def sync_module_venv(
    module_path: Path, capture: bool = False
) -> subprocess.CompletedProcess:
    """
    Synchronises the uv virtual environment for a module.
    UK English spelling. Uses cleaned environment for isolation.
    """
    return subprocess.run(
        ["uv", "sync"],
        cwd=module_path,
        env=get_clean_env(),
        capture_output=capture,
        text=capture,
    )


def upgrade_module_packages(
    module_path: Path, packages: List[str], capture: bool = False
) -> bool:
    """
    Upgrades specific packages within a module's uv environment.
    UK English spelling. Returns True if all packages succeeded, False otherwise.
    """
    env = get_clean_env()
    all_success = True
    for pkg in packages:
        res = subprocess.run(
            ["uv", "add", "--upgrade", pkg],
            cwd=module_path,
            env=env,
            capture_output=capture,
            text=capture,
        )
        if res.returncode != 0:
            all_success = False
    return all_success


def run_wrapper_script(wrapper_path: Path) -> subprocess.CompletedProcess:
    """
    Executes a generated module wrapper script.
    UK English spelling. Streams output directly to the terminal.
    """
    env = get_clean_env()
    return subprocess.run([str(wrapper_path)], env=env)
