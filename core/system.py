import os
import subprocess
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


def get_user_timers_status(capture: bool = False) -> subprocess.CompletedProcess:
    """
    Executes systemctl to display the status of DaGhE user timers.
    UK English spelling. Streams output directly to the terminal and
    returns the completed process result.
    """
    bus_env = get_user_bus_env()
    return subprocess.run(
        ["systemctl", "--user", "list-timers", "auto-*"],
        env=bus_env,
        capture_output=capture,
        text=capture,
    )


def stream_user_journal(
    unit_name: str, lines: int = 20, capture: bool = False
) -> subprocess.CompletedProcess:
    """
    UK English: Streams the last N lines of a systemd user unit journal to stdout.
    Utilises the standardised user-bus environment.
    """
    bus_env = get_user_bus_env()
    return subprocess.run(
        ["journalctl", "--user", "-u", unit_name, "-n", str(lines)],
        env=bus_env,
        capture_output=capture,
        text=capture,
    )
