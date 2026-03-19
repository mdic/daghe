import json
import logging
from pathlib import Path
from typing import Any, Dict, Optional

logger = logging.getLogger(__name__)


def get_state_path(state_dir: Path, module_name: str) -> Path:
    """
    Constructs the absolute path to the module's JSON state file.
    UK English spelling.
    """
    return state_dir / f"{module_name}.json"


def write_state(state_dir: Path, module_name: str, state_data: Dict[str, Any]) -> None:
    """
    Writes the provided state dictionary to the module's state file atomically.
    """
    path = get_state_path(state_dir, module_name)
    tmp_path = path.with_suffix(".tmp")
    try:
        # Write to temporary file first to ensure atomicity
        with open(tmp_path, "w", encoding="utf-8") as f:
            json.dump(state_data, f, indent=4, ensure_ascii=False)

        # Atomic replace
        tmp_path.replace(path)
    except Exception as e:
        logger.warning(f"Could not update state file at {path}: {e}")
        if tmp_path.exists():
            tmp_path.unlink()


def read_state(state_dir: Path, module_name: str) -> Optional[Dict[str, Any]]:
    """
    Reads the module's state file. Returns None if the file is missing.
    """
    path = get_state_path(state_dir, module_name)
    if not path.exists():
        return None
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        logger.warning(f"Could not read state file at {path}: {e}")
        return None
