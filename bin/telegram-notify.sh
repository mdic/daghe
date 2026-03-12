#!/usr/bin/env bash
set -euo pipefail

# Rilevamento dinamico della posizione
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BASE_DIR="$(cd "${SCRIPT_DIR}/.." && pwd)"

LEVEL=${1:-"INFO"}
MESSAGE=${2:-""}
HOSTNAME=$(hostname)

# Carica i segreti usando il path dinamico
if [[ -f "${BASE_DIR}/config/telegram.env" ]]; then
    source "${BASE_DIR}/config/telegram.env"
else
    echo "Telegram config missing at ${BASE_DIR}/config/telegram.env. Skipping."
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
