#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "${SCRIPT_DIR}/../config/global.env"

SOURCE_DIR="${BASE_DIR}/systemd"
TARGET_DIR="/etc/systemd/system"

# Assicurati di essere root (o usa sudo)
if [[ $EUID -ne 0 ]]; then
   echo "Questo script deve essere eseguito con sudo."
   exit 1
fi

echo "[+] Inizio sincronizzazione unità systemd..."

# 1. Trova tutti i file .service, .timer e .target nella cartella systemd del progetto
cd "$SOURCE_DIR"
UNITS=$(ls auto-*.{service,timer} automation.target 2>/dev/null || true)

if [[ -z "$UNITS" ]]; then
    echo "[!] Nessun file unit trovato in $SOURCE_DIR"
    exit 0
fi

for UNIT in $UNITS; do
    echo "    - Elaborazione: $UNIT"

    # Crea il link simbolico (forza se esiste già)
    #ln -sf "${SOURCE_DIR}/${UNIT}" "${TARGET_DIR}/${UNIT}"

    # Invece di un semplice ln -s, facciamo questo:
    sed "s|{{BASE_DIR}}|${BASE_DIR}|g" "${SOURCE_DIR}/${UNIT}" > "/tmp/${UNIT}"
    mv "/tmp/${UNIT}" "${TARGET_DIR}/${UNIT}"
done

# 2. Ricarica systemd per vedere i nuovi link
echo "[+] Ricaricamento demone systemd..."
systemctl daemon-reload

# 3. Abilitazione automatica dei timer
echo "[+] Abilitazione timer e target..."
for TIMER in $(ls auto-*.timer 2>/dev/null || true); do
    echo "    - Abilitazione timer: $TIMER"
    systemctl enable "$TIMER"
done

# Abilita il target centrale
systemctl enable automation.target

echo "[OK] Sincronizzazione completata!"
echo "Ora puoi usare 'manage-jobs.sh status' per verificare."
