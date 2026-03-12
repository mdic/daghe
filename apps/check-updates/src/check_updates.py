import os
import sys
from pathlib import Path

import httpx


def get_latest_version(package_name):
    try:
        response = httpx.get(f"https://pypi.org/pypi/{package_name}/json", timeout=10)
        if response.status_code == 200:
            return response.json()["info"]["version"]
    except Exception:
        return "Unknown"
    return "Not Found"


def main():
    config_path = Path(
        "/opt/automation/apps/check-updates/config/packages-to-check.txt"
    )
    if not config_path.exists():
        print(f"Error: {config_path} not found.")
        sys.exit(1)

    packages = [
        line.strip()
        for line in config_path.read_text().splitlines()
        if line.strip() and not line.startswith("#")
    ]

    print(f"{'Package':<25} | {'Latest Version':<15}")
    print("-" * 45)

    updates_found = []
    for pkg in packages:
        latest = get_latest_version(pkg)
        print(f"{pkg:<25} | {latest:<15}")
        updates_found.append(f"{pkg}: {latest}")

    # The wrapper captures this output and can pass it to Telegram.
    if updates_found:
        print("\nUpdate check complete.")


if __name__ == "__main__":
    main()
