import os
from typing import Dict


def get_clean_env() -> Dict[str, str]:
    """
    Returns a copy of environment variables stripped of Python-specific vars.
    UK English spelling. Matches legacy _get_clean_env logic exactly.
    """
    env = os.environ.copy()

    # Remove variables that would cause virtual environment nesting
    env.pop("VIRTUAL_ENV", None)
    env.pop("PYTHONPATH", None)
    env.pop("__PYVENV_LAUNCHER__", None)

    return env
