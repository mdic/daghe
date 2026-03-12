# daghe

# Installation Steps
## Preparation:
  - Create a dedicated user: `sudo useradd -m -d /opt/automation automation-user`.
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
