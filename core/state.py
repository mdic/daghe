import fcntl
import json
import logging
import os
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


def is_module_running(state_dir: Path, module_name: str) -> bool:
    """
    UK English: Checks if a module is running by probing the exclusion lock.
    Returns True if the lock is held by any active process in the chain.
    """
    lock_path = state_dir / f"{module_name}.lock"
    if not lock_path.exists():
        return False

    fd = None
    try:
        # Open the lockfile for probing
        fd = os.open(lock_path, os.O_RDONLY)
        # Attempt to acquire an exclusive non-blocking lock
        fcntl.flock(fd, fcntl.LOCK_EX | fcntl.LOCK_NB)

        # If we reach here, we acquired the lock: the module is IDLE
        fcntl.flock(fd, fcntl.LOCK_UN)
        return False
    except (BlockingIOError, IOError):
        # Lock is held: the module is RUNNING
        return True
    except Exception:
        return False
    finally:
        if fd is not None:
            os.close(fd)
