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


def get_user_bus_env() -> Dict[str, str]:
    """
    Returns an environment mapping configured for systemd user-bus access.
    UK English spelling. Replicates legacy _get_user_bus_env logic exactly.
    """
    # 1. Start with the cleaned environment (isolation logic)
    env = get_clean_env()

    # 2. Programmatically discover the current user's UID
    uid = os.getuid()
    runtime_dir = f"/run/user/{uid}"

    # 3. Inject the specific variables required for user-instance systemctl
    env["XDG_RUNTIME_DIR"] = runtime_dir
    env["DBUS_SESSION_BUS_ADDRESS"] = f"unix:path={runtime_dir}/bus"

    return env
