import logging
import subprocess
from pathlib import Path

from core.system import get_clean_env

logger = logging.getLogger("daghe.notifier")


def send_notification(level: str, message: str) -> None:
    """
    UK English spelling. A minimal Python wrapper for bin/telegram-notify.sh.
    Harden with a 10-second timeout to prevent blocking the main engine.
    """
    base_dir = Path(__file__).resolve().parent.parent
    helper_path = base_dir / "bin" / "telegram-notify.sh"

    if not helper_path.exists():
        logger.warning(f"Telegram helper not found at {helper_path}. Skipping.")
        return

    try:
        # Standardised invocation with a safety timeout
        subprocess.run(
            [str(helper_path), level, message],
            env=get_clean_env(),
            check=True,
            capture_output=True,
            text=True,
            timeout=10,  # Fix 2: Safety timeout added
        )
    except subprocess.TimeoutExpired:
        logger.warning("Telegram notification timed out after 10 seconds.")
    except subprocess.CalledProcessError as e:
        err_msg = e.stderr.strip() if e.stderr else "Unknown error"
        logger.error(f"Telegram notification dispatch failed: {err_msg}")
    except Exception as e:
        logger.error(f"Unexpected error in notifier wrapper: {e}")
