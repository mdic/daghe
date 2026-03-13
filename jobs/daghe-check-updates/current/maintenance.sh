#!/usr/bin/env bash
# UK English spelling.
set -euo pipefail

# BASE_DIR is provided by the generated wrapper
echo "[$(date)] Starting global maintenance..."

# We call 'uv run bin/daghe' from the root of the orchestrator
# This ensures we use the orchestrator's environment
ORCHESTRATOR_ROOT="${BASE_DIR}"

MODULES=(
    "daghe-youtube-search-metadata"
)

for MODULE in "${MODULES[@]}"; do
    echo "Updating $MODULE..."
    cd "$ORCHESTRATOR_ROOT"
    uv run bin/daghe upgrade "$MODULE"
done

echo "[$(date)] All modules processed."
