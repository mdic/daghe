# daghe

# Create the 'daghe' system user
sudo useradd -m -d /opt/daghe -s /bin/bash daghe

# Initialise the directory structure
sudo mkdir -p /opt/daghe/{bin,config,templates,jobs,systemd,state,logs}
sudo chown -R daghe:daghe /opt/daghe

# Installation Steps
## Preparation:
  - Create a dedicated user: `sudo useradd -m -d /opt/daghe -s /bin/bash daghe`.
  - Ensure uv is installed: `curl -LsSf https://astral.sh/uv/install.sh | sh`.
  - Clone this orchestration repo into `/opt/automation`.
  - Ensure permissions: `sudo chown -R automation-user:automation-user /opt/automation`.

## Internal App Setup:
  - `cd /opt/automation/apps/check-updates`
  - `uv sync` (Creates the isolated environment).

## Secrets:
  - `cp /opt/automation/config/telegram.env.example /opt/automation/config/telegram.env`
  - Edit telegram.env with your bot credentials.

Edit telegram.env with your bot credentials.

## Systemd Integration:
  - Link units: `sudo ln -s /opt/automation/systemd/auto-* /etc/systemd/system/`
  - Link target: `sudo ln -s /opt/automation/systemd/automation.target /etc/systemd/system/`
  - Reload: sudo systemctl daemon-reload

# Operational Commands
- To start the entire ecosystem: `/opt/automation/bin/manage-jobs.sh enable-all`
- To check a specific job's logs: `/opt/automation/bin/manage-jobs.sh logs backup-data`
- To manually trigger a job run: `sudo systemctl start auto-fetch-api-data.service`

# Notes on Extending the System
## Adding a New External Job

1. Code Deployment: Clone the external operational script repo into `/opt/automation/jobs/<new-job>/current/`.
2. Data Setup: Initialize a separate Git repo in `/opt/automation/jobs/<new-job>/data/`.
3. Wrapper: Copy `bin/run-backup-data.sh` to `bin/run-<new-job>.sh` and point the PAYLOAD variable to the entrypoint of the new script.
4. Systemd: Create a new `.service` and `.timer` in `systemd/` following the existing patterns.
5. Manager: Add the job name to the `JOBS` array in `bin/manage-jobs.sh`.

### Update Checking

To add a new package to the check-list, simply edit `/opt/automation/apps/check-updates/config/packages-to-check.txt`. The daily run will automatically report its status via journald (and optionally Telegram).


This is the professional English documentation for your orchestration system. You can append this directly to your `README.md`.

It covers the architecture, the "Zero-Effort" systemd deployment, and the standardized Python workflow we developed.

---

## 🚀 Systemd Orchestration & Job Management

This repository uses a **Symlink-based Orchestration** strategy. All systemd unit files are tracked in this repository but are linked to the system directory for execution. This ensures that your automation logic remains under version control while being fully integrated with the Linux service manager.

### 🏗 Architecture Overview

1.  **Source of Truth**: All `.service`, `.timer`, and `.target` files are stored in `/opt/automation/systemd/`.
2.  **System Integration**: Units are symlinked to `/etc/systemd/system/`.
3.  **Group Control**: All jobs are bound to `automation.target`. Starting/Stopping the target affects the entire suite.
4.  **Isolation**: Python jobs use `uv` in "non-package" mode (`package = false`) for maximum stability on the VPS.

---

### 🛠 Automated Deployment (`install-units.sh`)

To avoid manual configuration, we use an automated installer. The script `bin/install-units.sh`:
*   Scans `/opt/automation/systemd/` for any `auto-*.{service,timer}` files.
*   Creates/updates symbolic links in `/etc/systemd/system/`.
*   Performs a `systemctl daemon-reload`.
*   Automatically enables all timers and the global target.

**Usage:**
```bash
# Sync all systemd units and enable timers
/opt/automation/bin/manage-jobs.sh install
```

---

### 📝 Workflow: Adding a New Job

To add a new job (e.g., `db-backup`) to the system, follow these 4 steps:

#### 1. Prepare the Payload
Deploy your code to: `/opt/automation/jobs/db-backup/current/`.
If it's a Python job, ensure the structure is:
```text
current/
├── pyproject.toml  # Must contain [tool.uv] package = false
└── src/
    └── db_backup/
        └── main.py
```

#### 2. Create the Wrapper
Create `/opt/automation/bin/run-db-backup.sh`:
```bash
#!/usr/bin/env bash
set -euo pipefail
source "/opt/automation/config/global.env"

# Standard locking & PYTHONPATH setup
cd "/opt/automation/jobs/db-backup/current"
export PYTHONPATH="src"

uv run python -m db_backup.main --config config/job.yaml
```

#### 3. Define Systemd Units
Create the service and timer in `/opt/automation/systemd/`:
*   `auto-db-backup.service`: Points to your new wrapper.
*   `auto-db-backup.timer`: Defines the schedule (e.g., `OnCalendar=hourly`).

#### 4. Register the Job
Simply run the management command:
```bash
/opt/automation/bin/manage-jobs.sh install
```

---

### 🖥 Operational CLI

The `manage-jobs.sh` script is your primary interface for daily operations:

| Command | Description |
| :--- | :--- |
| `install` | Syncs systemd units from the repo to the system and enables timers. |
| `refresh` | Reloads the systemd daemon (useful after manual file edits). |
| `status` | Shows the status of all timers and services. |
| `list` | Lists all configured jobs in the suite. |
| `start <job>` | Manually triggers a specific job immediately. |
| `logs <job>` | Streams real-time logs (journald) for a specific job. |
| `enable-all` | Starts the global automation target and all timers. |
| `disable-all` | Stops everything and disables all timers. |

---

### 🐍 Python Environment Notes

For performance and reliability on the VPS, we use **uv** in non-package mode.
*   **No Build Step**: `uv sync` manages dependencies without building a wheel.
*   **Fast Execution**: The code is run directly from the `src/` directory.
*   **Requirement**: Every Python wrapper must `export PYTHONPATH="src"` before calling `uv run`.

---

### 📂 Directory Structure Reminder

```text
/opt/automation
├── bin/          # Wrappers and Management scripts (Tracked)
├── config/       # Global and Job-specific configs (Tracked/Templates)
├── systemd/      # Systemd Unit Sources (Tracked)
├── jobs/
│   └── <name>/
│       ├── current/  # External Job Code (Not tracked here)
│       └── data/     # External Job Data (Not tracked here)
└── state/        # Runtime locks and PID files (Ignored)
```
