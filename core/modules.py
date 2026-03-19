from pathlib import Path
from typing import List

from core.manifest import get_manifest_path


def list_module_dirs(jobs_dir: Path) -> List[str]:
    """
    Shallow discovery: Returns names of all directories starting with 'daghe-'.
    UK English spelling. Used for broad scanning and autocompletion.
    """
    if not jobs_dir.exists():
        return []
    return [
        d.name for d in jobs_dir.iterdir() if d.is_dir() and d.name.startswith("daghe-")
    ]


def list_valid_modules(jobs_dir: Path) -> List[str]:
    """
    Strict discovery: Returns names of 'daghe-' directories that contain a manifest.
    UK English spelling. Used for operational status and execution.
    """
    candidates = list_module_dirs(jobs_dir)
    valid = []
    for name in candidates:
        manifest_path = get_manifest_path(jobs_dir, name)
        if manifest_path.exists():
            valid.append(name)
    return valid


def get_testing_status_names(jobs_dir: Path) -> List[str]:
    """
    Returns the names of valid modules for testing-mode status reporting.
    UK English spelling. Delegates to internal validation logic.
    """
    return list_valid_modules(jobs_dir)


def get_module_log_path(log_dir: Path, module_name: str) -> Path:
    """
    UK English: Resolves the expected log file path for a sanitised module name.
    Preserves the legacy convention of stripping the 'daghe-' prefix.
    """
    return log_dir / f"{module_name.replace('daghe-', '')}.log"
