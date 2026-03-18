"""
DaGhE Core Utilities
UK English spelling.
Shared helper functions for path and string manipulation.
"""

from pathlib import Path


def sanitise_module_name(name: str) -> str:
    """
    Isolates the module name from a provided string or path.
    Matches legacy behaviour: handles trailing slashes and empty inputs.
    """
    if not name:
        return ""
    # Get only the last part of the path and strip trailing slashes
    return Path(name).name
