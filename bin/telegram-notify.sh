#!/usr/bin/env bash
# DaGhE Telegram Notifier - Batch 4.1.d
# UK English spelling. Clean separation of Transport and API/HTTP failures.
set -euo pipefail

# 1. Dynamic Path Discovery
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BASE_DIR="$(cd "${SCRIPT_DIR}/.." && pwd)"

# 2. Input Handling
IN_LEVEL="${1:-"INFO"}"
MESSAGE="${2:-""}"
HOSTNAME="${HOSTNAME:-$(hostname)}"
LEVEL_UPPER="${IN_LEVEL^^}"

# 3. Load Secrets
if [[ -f "${BASE_DIR}/config/telegram.env" ]]; then
    source "${BASE_DIR}/config/telegram.env"
else
    echo "Telegram config missing at ${BASE_DIR}/config/telegram.env. Skipping."
    exit 0
fi

# 4. Load Templates
if [[ -f "${BASE_DIR}/config/telegram-templates.sh" ]]; then
    source "${BASE_DIR}/config/telegram-templates.sh"
fi

# 5. Empty Message Check
if [[ -z "$MESSAGE" ]]; then
    echo "Empty message. Skipping." >&2
    exit 1
fi

# 6. Prefix Resolution
VAR_NAME="DGH_NOTIFY_${LEVEL_UPPER}"
PREFIX="${!VAR_NAME:-${DGH_NOTIFY_DEFAULT:-"[${LEVEL_UPPER}]"}}"

# 7. Payload Construction
PAYLOAD="${PREFIX} [${HOSTNAME}]"$'\n'"${MESSAGE}"

# 8. Dispatch and Failure Detection
# -sS: Silent, but show transport errors to stderr
# -w "\n%{http_code}": Append HTTP status code on a new line to the response body
# We use 'if !' to handle curl exit codes (transport level) without triggering 'set -e'
if ! RAW_RESPONSE=$(curl -sS -w "\n%{http_code}" -X POST "https://api.telegram.org/bot${TELEGRAM_BOT_TOKEN}/sendMessage" \
    -d "chat_id=${TELEGRAM_CHAT_ID}" \
    -d "text=${PAYLOAD}" 2>&1); then
    echo "Telegram notification failed (Transport error: $RAW_RESPONSE)" >&2
    exit 1
fi

# Parse RAW_RESPONSE: last line is the HTTP code, the rest is the body
HTTP_CODE=$(echo "$RAW_RESPONSE" | tail -n1)
RESPONSE_BODY=$(echo "$RAW_RESPONSE" | sed '$d')

# 9. HTTP/API Error Inspection
# Check if HTTP status is 200 AND body contains '"ok":true'
if [[ "$HTTP_CODE" -ne 200 ]] || [[ "$RESPONSE_BODY" != *'"ok":true'* ]]; then
    echo "Telegram notification failed (API error, HTTP $HTTP_CODE: $RESPONSE_BODY)" >&2
    exit 1
fi

# 10. Optional Verbosity
if [[ "${DGH_NOTIFY_VERBOSE:-0}" == "1" ]]; then
    echo "Notification dispatched: [${LEVEL_UPPER}]"
fi
