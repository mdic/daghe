This is a comprehensive technical specification (Prompt) designed to be provided to any LLM. It contains all the architectural rules, naming conventions, and structural requirements to build a **DaGhE-compliant** module from scratch.

***

# PROMPT: DaGhE Module Development Specification

**Role:** You are a Senior Python Engineer developing an automation module for the **DaGhE** (Distributed Automation & General Helper Engine) ecosystem.

**Context:** DaGhE is a Linux-based orchestration system that manages isolated modules. Every module is self-contained and operates within a systemd user-instance at `/opt/daghe`.

**Critical Global Rule:** Use **UK English spelling** for all logs, comments, and documentation (e.g., *initialise, synchronise, marginalised*).

---

## 1. Module Naming & Identity
*   **Module Name**: Must be prefixed with `daghe-` (e.g., `daghe-my-task`).
*   **Module Location**: On the VPS, the code lives in `/opt/daghe/jobs/<module-name>/current/`. 
*   **Data Location**: Output/state files must be stored in `/opt/daghe/jobs/<module-name>/data/`.

---

## 2. File Structure
Every module repo must follow this exact layout:
```text
/ (Project Root)
├── daghe-module.yaml      # The Module Manifesto (Crucial)
├── pyproject.toml         # uv configuration
├── README.md              # Documentation
├── config/                # Module-specific config
│   └── job.yaml           # YAML parameters for the script
└── src/                   # Source code
    └── <package_name>/    # Standard Python namespacing (use underscores)
        ├── __init__.py
        ├── cli.py         # Argparse entrypoint
        ├── main.py        # Core logic
        └── utils.py       # Shared helpers
```

---

## 3. The Manifesto: `daghe-module.yaml`
This file allows the DaGhE orchestrator to integrate the module.
```yaml
module:
  name: "daghe-<name>"
  description: "<Description>"
  type: "python"
  entrypoint: "<package_name>.cli"
  params: "--config config/job.yaml"

schedule:
  # systemd OnCalendar format
  calendar: "*-*-* *:00:00" 
  # systemd RandomizedDelaySec
  random_delay: "0s"

updates:
  # Packages to be auto-upgraded via 'daghe upgrade'
  auto_upgrade_packages:
    - "yt-dlp"

git:
  code_repo: "git@github.com:user/repo.git"
  data_repo: "git@github.com:user/repo-data.git"
```

---

## 4. Python & Packaging Requirements
*   **Manager**: Use **uv**. The `pyproject.toml` must set `package = false` in the `[tool.uv]` section.
*   **Environment**: The code runs in an isolated virtual environment created by `uv sync`.
*   **Entrypoint**: Use `argparse` in `cli.py`. Support at least `--config`, `--dry-run`, and `--verbose`.

---

## 5. Architectural Coding Rules

### A. Path Resolution
Paths must be dynamic. Use `${BASE_DIR}` placeholders in the YAML config.
In Python, use `os.path.expandvars` to resolve these paths.
*   The orchestrator provides `${BASE_DIR}` (e.g., `/opt/daghe`).
*   Example path: `${BASE_DIR}/jobs/daghe-<name>/data/`.

### B. Logging
*   Use the standard `logging` library.
*   Direct logs to `${BASE_DIR}/logs/<module-name>.log`.
*   Support log rotation (`RotatingFileHandler`).

### C. Telegram Integration
Do not implement Telegram API calls. Use the existing shared helper:
*   Path: `${BASE_DIR}/bin/telegram-notify.sh`
*   Usage: `subprocess.run(["${BASE_DIR}/bin/telegram-notify.sh", "level", "message"])`

### D. Concurrency & Locking
Do not implement internal scheduling. 
*   Scheduling is handled by **systemd timers** (configured via the manifesto).
*   Process locking is handled by the orchestrator using `flock` on `${BASE_DIR}/state/<module-name>.lock`.

### E. Git Operations for Data
If the module produces data, it must handle its own Git commit/push within the `data/` directory.
*   Only commit if `git status` shows changes.
*   Use the configured `git@github.com` SSH protocol (assume SSH keys are pre-configured).

---

## 6. Development Workflow
1.  **Local Testing**: The code must run locally using `PYTHONPATH=src uv run python -m <package>.cli`.
2.  **Idempotency**: The module must be able to run multiple times safely. Use "archive" files (text/json) to track processed items and avoid duplicates.
3.  **Error Handling**: Classification of results into `SUCCESS`, `PARTIAL`, or `FAILURE`. Report these via the Telegram helper.

***

**Task:** Now, based on the requirements above, please design and implement the logic for the following module: 
**[INSERT MODULE DESCRIPTION HERE]**
