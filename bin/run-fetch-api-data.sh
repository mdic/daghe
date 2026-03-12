#!/usr/bin/env bash
set -euo pipefail

source "/opt/automation/config/global.env"
JOB_NAME="fetch-api-data"
LOCK_FILE="${STATE_DIR}/${JOB_NAME}.lock"
JOB_ROOT="${BASE_DIR}/jobs/${JOB_NAME}"

exec 9>"$LOCK_FILE"
if ! flock -n 9; then exit 0; fi

if [[ -f "${CONFIG_DIR}/jobs/${JOB_NAME}.env" ]]; then
    source "${CONFIG_DIR}/jobs/${JOB_NAME}.env"
fi

PAYLOAD="${JOB_ROOT}/current/run.sh"

if [[ -x "$PAYLOAD" ]]; then
    export DATA_DIR="${JOB_ROOT}/data"
    "$PAYLOAD"
else
    "${BIN_DIR}/telegram-notify.sh" "ERROR" "Fetch failed: Payload $PAYLOAD not found or not executable."
    exit 1
fi
