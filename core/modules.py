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
