# DaGhE: Data Gathering Environment

**DaGhE** is a production-grade automation system designed to manage automation jobs on a systemd-based Linux VPS. It utilises **systemd user instances** to provide a secure, self-contained environment that requires **zero sudo/root privileges** after initial setup.

---

## 🏗 Philosophy: Zero-Sudo & Absolute Confinement

*   **Security**: The `daghe` user manages its own lifecycle independently.
*   **Portability**: The entire system is confined to `/opt/daghe`.
*   **Isolation**: Every module lives in its own `uv` environment.

---

## 🚀 Initial Installation (VPS)

### 1. Create the System User (As root/sudo)
```bash
sudo useradd -m -d /opt/daghe -s /bin/bash daghe
sudo mkdir -p /opt/daghe
sudo chown daghe:daghe /opt/daghe
```

### 2. Enable Persistent User Services (As root/sudo)
This ensures DaGhE timers start at boot and continue running without an active session.
```bash
sudo loginctl enable-linger daghe
```

### 3. Deploy Orchestration (As daghe user)
```bash
sudo -u daghe -i
cd /opt/daghe
git clone <orchestration-repo-url> .
uv sync
chmod +x bin/daghe bin/telegram-notify.sh
```

---

## 📦 Module Lifecycle Management

Deploy your module repository to `jobs/<module-name>/current` and run:

```bash
# Register, sync venv, and enable timers
uv run bin/daghe install <module-name>
```

### Operational Commands
| Command | Action |
| :--- | :--- |
| `uv run bin/daghe status` | View active timers and next runs. |
| `systemctl --user list-units auto-*` | Check status of user-level units. |
| `journalctl --user -u auto-<name>.service -f` | Monitor real-time logs. |

---

## 🧪 Testing

DaGhE supports **Testing Mode**. If you run the CLI outside `/opt/daghe` (e.g., on your local PC), it will generate all wrappers and unit files in `bin/generated/` and `systemd/` for inspection, but it will **not** attempt to modify your user session or system configuration.

---

## 📂 Directory Structure
*   `bin/`: Orchestrator CLI and generated wrappers.
*   `jobs/`: Isolated modules (code and data repositories).
*   `.config/systemd/user/`: Active systemd unit symlinks (Self-contained).
*   `logs/`: Centralised operational logs.
```

---

### 5. Migration Guide for your VPS

1.  **Remove Old Files**: Delete `/etc/sudoers.d/daghe` and any DaGhE files in `/etc/systemd/system/`.
2.  **Linger**: Run `sudo loginctl enable-linger daghe`.
3.  **Clean Setup**: Ensure `/opt/daghe` is clean, clone the orchestration repo, and run `uv sync`.
4.  **Install**: For each job, run `uv run bin/daghe install <job-name>`.

Your system is now a masterpiece of Linux engineering: **secure, portable, and fully automated.**
