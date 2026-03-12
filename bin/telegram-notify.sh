#!/usr/bin/env bash
set -euo pipefail

# Shared Telegram helper
# Usage: ./telegram-notify.sh "level" "message"

LEVEL=${1:-"INFO"}
MESSAGE=${2:-""}
HOSTNAME=$(hostname)

# Load secrets
if [[ -f "/opt/automation/config/telegram.env" ]]; then
    source "/opt/automation/config/telegram.env"
else
    echo "Telegram config missing. Skipping notification."
    exit 0
fi

if [[ -z "$MESSAGE" ]]; then
    echo "Empty message. Skipping."
    exit 1
fi

PAYLOAD="[${LEVEL}] [${HOSTNAME}]
${MESSAGE}"

curl -s -X POST "https://api.telegram.org/bot${TELEGRAM_BOT_TOKEN}/sendMessage" \
    -d "chat_id=${TELEGRAM_CHAT_ID}" \
    -d "text=${PAYLOAD}" > /dev/null
