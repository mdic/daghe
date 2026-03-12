#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
# Carichiamo global.env per avere BASE_DIR, BIN_DIR, ecc.
source "${SCRIPT_DIR}/../config/global.env"

# Job Manager Utility
JOBS=("check-updates" "backup-data" "fetch-api-data" "youtube-search-metadata")

usage() {
    echo "Usage: $0 {list|status|enable|disable|start|stop|logs|install} [job_name]"
    exit 1
}

if [[ $# -lt 1 ]]; then usage; fi

COMMAND=$1
JOB=${2:-""}

case "$COMMAND" in
    install)
        sudo "${BASE_DIR}/install-units.sh"
        ;;
    refresh)
        sudo systemctl daemon-reload
        echo "Configurazioni ricaricate."
        ;;
    list)
        echo "Configured jobs:"
        for j in "${JOBS[@]}"; do echo " - $j"; done
        ;;
    status)
        systemctl status "auto-*.timer" "auto-*.service"
        ;;
    start)
        systemctl start "auto-${JOB}.service"
        ;;
    stop)
        systemctl stop "auto-${JOB}.service"
        ;;
    enable)
        systemctl enable --now "auto-${JOB}.timer"
        ;;
    disable)
        systemctl disable --now "auto-${JOB}.timer"
        ;;
    logs)
        journalctl -u "auto-${JOB}.service" -f
        ;;
    enable-all)
        for j in "${JOBS[@]}"; do systemctl enable "auto-${j}.timer"; done
        systemctl start automation.target
        ;;
    disable-all)
        systemctl stop automation.target
        for j in "${JOBS[@]}"; do systemctl disable "auto-${j}.timer"; done
        ;;
    *)
        usage
        ;;
esac
