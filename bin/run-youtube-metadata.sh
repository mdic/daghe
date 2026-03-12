#!/usr/bin/env bash
set -euo pipefail

# 1. Carica configurazioni globali
source "/opt/automation/config/global.env"

# 2. Definisci variabili specifiche del job
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
