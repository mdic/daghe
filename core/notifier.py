import logging
import subprocess
from pathlib import Path

from core.system import get_clean_env

logger = logging.getLogger("daghe.notifier")


def send_notification(level: str, message: str) -> None:
    """
    UK English spelling. A minimal Python wrapper for bin/telegram-notify.sh.
    Ensures that notification failures do not interrupt the caller's execution.
    """
    # Resolve the absolute path to the shared bash helper
    # Based on current structure: /opt/daghe/core/notifier.py -> /opt/daghe/bin/
    base_dir = Path(__file__).resolve().parent.parent
    helper_path = base_dir / "bin" / "telegram-notify.sh"

    if not helper_path.exists():
        logger.warning(
            f"Telegram helper not found at {helper_path}. Skipping notification."
        )
        return

    try:
        # Standardised invocation: telegram-notify.sh <level> <message>
        # We use capture_output to keep the orchestrator logs clean
        subprocess.run(
            [str(helper_path), level, message],
            env=get_clean_env(),
            check=True,
            capture_output=True,
            text=True,
        )
    except subprocess.CalledProcessError as e:
        # The bash helper already outputs specific errors to stderr on exit 1
        # We capture and log them here without re-raising
        err_msg = e.stderr.strip() if e.stderr else "Unknown error"
        logger.error(f"Telegram notification dispatch failed: {err_msg}")
    except Exception as e:
        # Catch any unexpected OS or permission errors
        logger.error(f"Unexpected error in notifier wrapper: {e}")
