#!/usr/bin/env bash
set -euo pipefail

# 1. Setup Environment
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "${SCRIPT_DIR}/../config/global.env"

JOB_NAME="check-updates"
LOCK_FILE="${STATE_DIR}/${JOB_NAME}.lock"
APP_DIR="${BASE_DIR}/apps/check-updates"

# 2. Prevent overlapping execution
exec 9>"$LOCK_FILE"
if ! flock -n 9; then
    echo "Job ${JOB_NAME} is already running. Exiting."
    exit 0
fi

echo "Starting ${JOB_NAME}..."

# 3. Execution
cd "$APP_DIR"
# Use uv to run the internal app
# Output is captured for Telegram if needed
REPORT=$(uv run src/check_updates.py 2>&1)
echo "$REPORT"

# 4. Notifications (Optional on success)
# "${BIN_DIR}/telegram-notify.sh" "INFO" "Update Check Report:
# $REPORT"

echo "${JOB_NAME} finished successfully."
