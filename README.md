# DaGhE: Dataa Gathering Environment

**DaGhE** is a production-grade orchestration platform for Linux VPS environments. It manages multiple Python and Bash jobs using a **Zero-Sudo** architecture. By leveraging **systemd user-instances**, DaGhE remains entirely confined to its own directory, requiring no root privileges for day-to-day operations, installation, or maintenance.

---

## 🏗 Architectural Principles

*   **Zero-Sudo**: Once the initial user and "linger" settings are configured, the orchestrator operates without elevated privileges.
*   **Location-Agnostic**: The system automatically discovers its `BASE_DIR`. It can be tested locally on a PC or deployed to `/opt/daghe` on a VPS.
*   **Isolated Environments**: Every Python module manages its own dependencies via `uv`, preventing version conflicts.
*   **Decoupled Data**: Operational code (`current/`) and collected data (`data/`) live in separate sub-directories, allowing independent Git versioning.

---

## 📂 Directory Structure

```text
/opt/daghe
├── bin/                 # Orchestrator CLI (daghe) and notification helper
├── config/              # Global environment variables and secrets
├── jobs/                # Modular tasks
│   └── <module-name>/
│       ├── current/     # Code repository (contains daghe-module.yaml)
│       └── data/        # Data repository (JSONs, CSVs, etc.)
├── logs/                # Centralised log collection
├── templates/           # Blueprints for generating wrappers and units
├── systemd/             # Master copies of generated .service and .timer files
├── state/               # Runtime locks to prevent overlapping executions
└── .config/systemd/user/ # Active systemd symlinks (managed by daghe CLI)
```

---

## 🚀 Initial VPS Setup (As Root/Sudo)

Before deploying the orchestrator, the host must be prepared to support persistent user-level services.

### 1. Create the DaGhE System User
```bash
sudo useradd -m -d /opt/daghe -s /bin/bash daghe
sudo mkdir -p /opt/daghe
sudo chown daghe:daghe /opt/daghe
```

### 2. Enable User Persistence (Linger)
By default, systemd user-instances stop when the user logs out. **Linger** ensures the user-instance starts at boot and stays alive indefinitely.
```bash
sudo loginctl enable-linger daghe
```

---

## 📦 Deployment (As the `daghe` User)

### 1. Initialise the Orchestrator
Switch to the `daghe` user and clone the orchestration repository:
```bash
sudo -u daghe -i
cd /opt/daghe
git clone <orchestration-repo-url> .

# Synchronise the orchestrator's Python environment
uv sync
chmod +x bin/daghe bin/telegram-notify.sh
```

### 2. Configure Secrets
```bash
cp config/telegram.env.example config/telegram.env
# Edit with your Telegram BOT_TOKEN and CHAT_ID
nano config/telegram.env
chmod 600 config/*.env
```

---

## ⚙️ Module Management

### Adding a New Module
1.  **Clone Repositories**: Deploy your code to `jobs/<module-name>/current` and your data to `jobs/<module-name>/data`.
2.  **Run Installation**:
    ```bash
    uv run bin/daghe install <module-name>
    ```
    *This command will automatically synchronise the module's `uv` environment, generate wrappers/units, and enable the timer.*

### CLI Reference
| Command | Action |
| :--- | :--- |
| `uv run bin/daghe install <name>` | Initialises venv and registers systemd user-timers. |
| `uv run bin/daghe upgrade <name>` | Force-upgrades Python packages defined in the manifest. |
| `uv run bin/daghe status` | Shows all active DaGhE timers and scheduled runs. |

---

## 🧪 Testing Strategies

### 1. Local Development (Testing Mode)
If you run `bin/daghe` outside the production path (`/opt/daghe`), it enters **TESTING MODE**. It will generate files for inspection in your local folders but will **not** attempt to modify your systemd session.

### 2. Integrated Wrapper Test
The best way to test a job on the VPS is to run the generated wrapper. This tests paths, locks, and environment isolation:
```bash
./bin/generated/run-<module-name>.sh
```

### 3. Manual Systemd Trigger
To force an immediate execution through systemd:
```bash
systemctl --user start auto-<module-name>.service
# Follow logs
journalctl --user -u auto-<module-name>.service -f
```

---

## ⚠️ Common Troubleshooting (The "Bus Connection" Issue)

When running `systemctl --user` commands via SSH or scripts, you might encounter:
`Failed to connect to bus: No medium found`.

**DaGhE** handles this automatically by calculating and injecting `XDG_RUNTIME_DIR` and `DBUS_SESSION_BUS_ADDRESS` into its subprocesses. If problems persist manually:
1.  Ensure `loginctl enable-linger daghe` was executed as root.
2.  Check that `/run/user/<UID>` exists (where UID is the result of `id -u daghe`).
3.  Include the following in your `.bashrc` for manual debugging:
    ```bash
    export XDG_RUNTIME_DIR="/run/user/$(id -u)"
    export DBUS_SESSION_BUS_ADDRESS="unix:path=${XDG_RUNTIME_DIR}/bus"
    ```

---

## 🔄 Automated Maintenance
Keep fast-breaking dependencies (like `yt-dlp`) updated by creating a maintenance module. In its `daghe-module.yaml`, define `auto_upgrade_packages`, and schedule a weekly task that runs:
```bash
uv run bin/daghe upgrade <your-module-name>
```

---

## ⚖️ Standards
*   **Language**: UK English spelling (`initialise`, `synchronise`, `standardised`).
*   **Security**: No `sudo` usage within the orchestrator logic.
*   **Reliability**: Atomic symlinking and automated environment isolation via `uv`.
