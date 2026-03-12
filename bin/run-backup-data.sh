#!/usr/bin/env bash
set -euo pipefail

source "/opt/automation/config/global.env"
JOB_NAME="backup-data"
LOCK_FILE="${STATE_DIR}/${JOB_NAME}.lock"
JOB_ROOT="${BASE_DIR}/jobs/${JOB_NAME}"

exec 9>"$LOCK_FILE"
if ! flock -n 9; then
    exit 0
fi

# 1. Environment Loading (Job specific)
if [[ -f "${CONFIG_DIR}/jobs/${JOB_NAME}.env" ]]; then
    source "${CONFIG_DIR}/jobs/${JOB_NAME}.env"
fi

# 2. Execution of External Payload
# Expects run.py to exist in current/
PAYLOAD="${JOB_ROOT}/current/run.py"

if [[ -f "$PAYLOAD" ]]; then
    # We pass the data directory as an environment variable to the script
    export DATA_DIR="${JOB_ROOT}/data"
    python3 "$PAYLOAD"
else
    "${BIN_DIR}/telegram-notify.sh" "ERROR" "Backup failed: Payload $PAYLOAD not found."
    exit 1
fi
