#!/usr/bin/env bash
set -euo pipefail

# Trova la cartella dove risiede questo script (bin/)
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Carica global.env usando il percorso relativo (va indietro di uno e entra in config/)
if [[ -f "${SCRIPT_DIR}/../config/global.env" ]]; then
    source "${SCRIPT_DIR}/../config/global.env"
else
    echo "Errore: Impossibile trovare ${SCRIPT_DIR}/../config/global.env"
    exit 1
fi

# Ora tutte le variabili (BASE_DIR, JOB_ROOT, ecc.) sono basate sul path reale
JOB_NAME="youtube-search-metadata"
LOCK_FILE="${STATE_DIR}/${JOB_NAME}.lock"
JOB_ROOT="${BASE_DIR}/jobs/${JOB_NAME}"
CONFIG_FILE="${JOB_ROOT}/current/config/job.yaml"

# 3. Protezione: evita esecuzioni sovrapposte
exec 9>"$LOCK_FILE"
if ! flock -n 9; then
    echo "[$(date)] Job ${JOB_NAME} già in esecuzione. Salto."
    exit 0
fi

# 4. Carica variabili d'ambiente specifiche (se esistono)
if [[ -f "${CONFIG_DIR}/jobs/${JOB_NAME}.env" ]]; then
    source "${CONFIG_DIR}/jobs/${JOB_NAME}.env"
fi

# 5. ESECUZIONE
echo "[$(date)] Inizio job ${JOB_NAME}..."

cd "${JOB_ROOT}/current"

# Fondamentale: permette a Python di trovare il modulo nella cartella src
export PYTHONPATH="src"

# Esegui tramite uv
uv run python -m youtube_search_metadata.cli --config "$CONFIG_FILE"

echo "[$(date)] Job ${JOB_NAME} completato con successo."
