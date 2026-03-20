#!/usr/bin/env bash
# DaGhE Telegram Notifier - Batch 4.1.b
# UK English spelling. Robust error detection for both transport and API levels.
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

# 4. Load Templates (Optional defines prefixes per level)
if [[ -f "${BASE_DIR}/config/telegram-templates-v2.sh" ]]; then
    source "${BASE_DIR}/config/telegram-templates-v2.sh"
elif [[ -f "${BASE_DIR}/config/telegram-templates.sh" ]]; then
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

# 8. Dispatch and API Failure Detection
# Capture response to check for API-level errors
RESPONSE=$(curl -s -X POST "https://api.telegram.org/bot${TELEGRAM_BOT_TOKEN}/sendMessage" \
    -d "chat_id=${TELEGRAM_CHAT_ID}" \
    -d "text=${PAYLOAD}")
CURL_STATUS=$?

# Check for Transport failure (curl exit code)
if [[ $CURL_STATUS -ne 0 ]]; then
    echo "Telegram notification failed (Transport error: exit code $CURL_STATUS)" >&2
    exit 1
fi

# Check for Telegram API failure (JSON response "ok": false)
# We use Bash string matching to avoid a 'jq' dependency
if [[ "$RESPONSE" != *'"ok":true'* ]]; then
    echo "Telegram notification failed (API error: $RESPONSE)" >&2
    exit 1
fi

# 9. Optional Verbosity
if [[ "${DGH_NOTIFY_VERBOSE:-0}" == "1" ]]; then
    echo "Notification dispatched: [${LEVEL_UPPER}]"
fi
