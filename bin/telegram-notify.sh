#!/usr/bin/env bash
# DaGhE Telegram Notifier - Batch 4.1.c
# UK English spelling. Final robust error-handling and simplified config.
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

# 4. Load Templates (Simplified to one single file)
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

# 8. Dispatch and API Failure Detection
# Restructured to handle transport failure explicitly under set -e.
# Placing the assignment in an 'if' condition prevents the script from
# exiting immediately on curl error, allowing us to report it.
if ! RESPONSE=$(curl -s -f -X POST "https://api.telegram.org/bot${TELEGRAM_BOT_TOKEN}/sendMessage" \
    -d "chat_id=${TELEGRAM_CHAT_ID}" \
    -d "text=${PAYLOAD}"); then
    echo "Telegram notification failed (Transport error)" >&2
    exit 1
fi

# Transport succeeded, now check if the Telegram API returned "ok": true
if [[ "$RESPONSE" != *'"ok":true'* ]]; then
    echo "Telegram notification failed (API error: $RESPONSE)" >&2
    exit 1
fi

# 9. Optional Verbosity
if [[ "${DGH_NOTIFY_VERBOSE:-0}" == "1" ]]; then
    echo "Notification dispatched: [${LEVEL_UPPER}]"
fi
