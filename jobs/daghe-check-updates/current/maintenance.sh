#!/usr/bin/env bash
# UK English spelling. Global maintenance script for the Zero-Sudo architecture.
set -euo pipefail

# BASE_DIR is injected by the generated wrapper
echo "[$(date)] Initialising dependency maintenance..."

MODULES=(
    "daghe-youtube-search-metadata"
)

for MODULE in "${MODULES[@]}"; do
    echo "Processing $MODULE..."
    # Call the orchestrator CLI directly
    uv run --project "${BASE_DIR}" "${BASE_DIR}/bin/daghe" upgrade "$MODULE"
done

"${BASE_DIR}/bin/telegram-notify.sh" "INFO" "DaGhE Maintenance: Automated upgrades for ${#MODULES[@]} modules completed."
echo "[$(date)] Maintenance cycle finished."
