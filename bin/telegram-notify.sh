#!/usr/bin/env bash
# DaGhE Telegram Notifier - Batch 4.1.a
# UK English spelling. Robust, silent by default, and hardened.
set -euo pipefail

# 1. Dynamic Path Discovery
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BASE_DIR="$(cd "${SCRIPT_DIR}/.." && pwd)"

# 2. Input Handling
IN_LEVEL="${1:-"INFO"}"
MESSAGE="${2:-""}"
# Fix 3: Use environment variable if available, otherwise call hostname
HOSTNAME="${HOSTNAME:-$(hostname)}"
# Fix 2: Modern Bash native uppercasing
LEVEL_UPPER="${IN_LEVEL^^}"

# 3. Load Secrets
if [[ -f "${BASE_DIR}/config/telegram.env" ]]; then
    source "${BASE_DIR}/config/telegram.env"
else
    # Maintain existing behaviour: skip silently if config is missing
    echo "Telegram config missing at ${BASE_DIR}/config/telegram.env. Skipping."
    exit 0
fi

# 4. Load Templates (Optional defines prefixes per level)
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
# Indirect expansion for prefix lookup
PREFIX="${!VAR_NAME:-${DGH_NOTIFY_DEFAULT:-"[${LEVEL_UPPER}]"}}"

# 7. Payload Construction
# Fix 4: Safe newline handling using ANSI-C quoting
PAYLOAD="${PREFIX} [${HOSTNAME}]"$'\n'"${MESSAGE}"

# 8. Dispatch
# Fix 5: Basic curl failure handling
if ! curl -s -X POST "https://api.telegram.org/bot${TELEGRAM_BOT_TOKEN}/sendMessage" \
    -d "chat_id=${TELEGRAM_CHAT_ID}" \
    -d "text=${PAYLOAD}" > /dev/null; then
    echo "Telegram notification failed" >&2
    exit 1
fi

# 9. Optional Verbosity
# Fix 1: Silent by default, enabled via DGH_NOTIFY_VERBOSE=1
if [[ "${DGH_NOTIFY_VERBOSE:-0}" == "1" ]]; then
    echo "Notification dispatched: [${LEVEL_UPPER}]"
fi
