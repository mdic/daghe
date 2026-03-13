# DaGhE: Data Gathering Environment

**DaGhE** is a production-grade orchestration system designed to manage, schedule, and maintain multiple Python and Bash automation jobs on a systemd-based Linux VPS. 

It follows a **Hybrid Manifest** architecture: each automation "module" is self-contained with its own configuration, while a centralised CLI handles system integration, isolated environment management (via `uv`), and automated maintenance.

---

## 🏗 Core Architecture

DaGhE enforces a strict separation of concerns across three distinct layers:

1.  **Orchestration Layer (`/opt/daghe`)**: The "brain" of the system. Contains the `daghe` CLI, systemd templates, and global configurations.
2.  **Module Layer (`jobs/<name>/current`)**: The operational logic. Each module is its own Git repository containing a `daghe-module.yaml` manifesto.
3.  **Data Layer (`jobs/<name>/data`)**: The operational output. Each module's data is stored in a separate directory, typically synchronised with its own dedicated Git repository.

---

## 🛠 System Requirements

*   **Linux VPS** (Systemd-based, e.g., Ubuntu, Debian, Rocky).
*   **Python 3.11+**.
*   **[uv](https://github.com/astral-sh/uv)**: Used for high-performance Python environment and dependency management.
*   **Git**: For versioning orchestration, code, and data.

---

## 🚀 Initial Installation (VPS)

### 1. Create the DaGhE User
For security, the entire ecosystem runs under a dedicated, non-privileged system user.

```bash
sudo useradd -m -d /opt/daghe -s /bin/bash daghe
sudo mkdir -p /opt/daghe
sudo chown daghe:daghe /opt/daghe
```

### 2. Deploy Orchestration
Switch to the `daghe` user and clone this repository:

```bash
sudo -u daghe -i
cd /opt/daghe
git clone <orchestration-repo-url> .
```

### 3. Initialise the Orchestrator Environment
DaGhE uses its own isolated environment to manage other jobs.

```bash
uv sync
chmod +x bin/daghe bin/telegram-notify.sh
```

### 4. Configure Secrets
Create the Telegram notification environment file (not tracked by Git):

```bash
cp config/telegram.env.example config/telegram.env
# Edit with your BOT_TOKEN and CHAT_ID
nano config/telegram.env
chmod 600 config/*.env
```

---

## 📦 Module Management

### 1. Adding a New Module
To add a module (e.g., `daghe-youtube-search-metadata`):

1.  **Clone the code**: 
    ```bash
    cd /opt/daghe/jobs/daghe-youtube-search-metadata/current
    git clone <code-repo-url> .
    ```
2.  **Clone the data** (if applicable):
    ```bash
    cd /opt/daghe/jobs/daghe-youtube-search-metadata/data
    git clone <data-repo-url> .
    ```
3.  **Install/Register with DaGhE**:
    ```bash
    # From the /opt/daghe root
    uv run bin/daghe install daghe-youtube-search-metadata
    ```

### 2. The `daghe-module.yaml` Manifesto
Every module must have this file in its `current/` directory. It defines the identity and schedule of the job:

```yaml
module:
  name: "daghe-youtube-search-metadata"
  description: "Downloads YouTube metadata"
  type: "python" # or "bash"
  entrypoint: "youtube_search_metadata.cli"
  params: "--config config/job.yaml"

schedule:
  calendar: "*-*-1/2 04:00:00" # Every two days at 4 AM
  random_delay: "4h"           # Start window: 4 AM to 8 AM

updates:
  auto_upgrade_packages:
    - "yt-dlp"
```

---

## ⚙️ The `daghe` CLI Commands

The `daghe` script is a location-agnostic tool. It detects if it is running in **Testing Mode** (local PC) or **Production Mode** (VPS).

| Command | Description |
| :--- | :--- |
| `uv run bin/daghe install <name>` | Synchronises the module's `uv` environment, generates wrappers, and enables systemd timers. |
| `uv run bin/daghe upgrade <name>` | Forcefully upgrades the Python packages listed in the module's manifesto. |
| `uv run bin/daghe status` | Lists all active DaGhE timers and their next scheduled runs. |
| `journalctl -u auto-<name>.service -f` | (Standard Linux) View real-time logs for a specific job. |

---

## 🔄 Automated Maintenance

DaGhE is designed to be self-maintaining. By creating a module named `daghe-check-updates`, you can schedule a weekly task that calls `daghe upgrade` on your other modules. This ensures that fast-moving libraries like `yt-dlp` are always kept up to date without manual intervention.

---

## 💻 Local Development & Testing

You can clone this entire orchestration repository onto your local machine for testing. 

*   **Dynamic Paths**: The CLI uses `BASE_DIR` auto-discovery. Generated scripts will point to your local folders (e.g., `/home/user/git/daghe/...`).
*   **Safety**: If the CLI detects it is not in `/opt/daghe`, it will **not** attempt to use `sudo` or modify `/etc/systemd/system/`. It will only generate the files for inspection.

---

## 📂 Directory Structure Convention

```text
/opt/daghe
├── bin/
│   ├── daghe                # The Orchestrator CLI
│   ├── generated/           # Auto-generated Bash wrappers
│   └── telegram-notify.sh   # Shared notification utility
├── config/
│   ├── global.env           # Global environment variables
│   └── telegram.env         # Secrets (Untracked)
├── templates/               # Blueprints for system generation
├── systemd/                 # Master copies of .service and .timer files
├── jobs/
│   └── <module-name>/
│       ├── current/         # Operational code repository
│       └── data/            # Operational data repository
├── logs/                    # Centralised log collection
└── state/                   # Runtime lock files
```
