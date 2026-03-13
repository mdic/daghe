# DaGhE: Data Gathering Environment

**DaGhE** is a production-grade orchestration platform for Linux VPS environments. It manages multiple Python and Bash jobs using a **Zero-Sudo** architecture. By leveraging **systemd user-instances**, DaGhE remains entirely confined to its own directory, requiring no root privileges for day-to-day operations.

---

## 🏗 Architectural Principles

*   **Zero-Sudo**: Once the initial "linger" is set, the orchestrator operates without elevated privileges.
*   **Location-Agnostic**: Automatically discovers `BASE_DIR` for local testing or VPS production.
*   **Isolated Environments**: Every module manages its own dependencies via `uv`.
*   **Decoupled Data**: Code (`current/`) and collected data (`data/`) live in separate repositories.

---

## 🚀 Initial VPS Setup (As Root/Sudo)

### 1. Create the DaGhE System User
```bash
sudo useradd -m -d /opt/daghe -s /bin/bash daghe
sudo mkdir -p /opt/daghe
sudo chown daghe:daghe /opt/daghe
```

### 2. Enable User Persistence (Linger)
Ensures the `daghe` user-instance starts at boot and stays alive after logout.
```bash
sudo loginctl enable-linger daghe
```

### 3. Configure Multi-user Access (ACLs)
To allow your personal admin account (e.g., `your_user`) to edit files in `/opt/daghe` without changing the primary owner, use **Access Control Lists**.

```bash
# Install the ACL utility
sudo apt update && sudo apt install acl -y

# Grant your user recursive rwx access to existing files
sudo setfacl -R -m u:your_user:rwx /opt/daghe

# Set default ACLs so NEW files inherit these permissions automatically
sudo setfacl -Rd -m u:your_user:rwx /opt/daghe
```

---

## 📦 Deployment (As the `daghe` User)

### 1. Initialise the Orchestrator
```bash
sudo -u daghe -i
cd /opt/daghe
git clone <orchestration-repo-url> .

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
1.  **Clone Repositories**: Deploy code to `jobs/<module-name>/current` and data to `jobs/<module-name>/data`.
2.  **Run Installation**:
    ```bash
    uv run bin/daghe install <module-name>
    ```

### CLI Reference
| Command | Action |
| :--- | :--- |
| `uv run bin/daghe install <name>` | Initialises venv and registers systemd user-timers. |
| `uv run bin/daghe upgrade <name>` | Force-upgrades Python packages defined in the manifest. |
| `uv run bin/daghe status` | Shows all active DaGhE timers and scheduled runs. |

---

## 🧪 Testing & Operation

### 1. Local Development (Testing Mode)
Running `bin/daghe` outside `/opt/daghe` triggers **TESTING MODE**. It generates files for inspection in local folders but does **not** modify systemd or the user session.

### 2. Manual Systemd Trigger (VPS)
To trigger a job immediately bypassing the timer:
```bash
systemctl --user start auto-<module-name>.service
# Monitor logs
journalctl --user -u auto-<module-name>.service -f
```

---

## ⚠️ Common Troubleshooting

### Bus Connection Issues
If `systemctl --user` fails with `Failed to connect to bus`:
1.  Ensure `loginctl enable-linger daghe` was executed.
2.  The `daghe` CLI automatically injects `XDG_RUNTIME_DIR`. If running commands manually, ensure these variables are exported:
    ```bash
    export XDG_RUNTIME_DIR="/run/user/$(id -u)"
    export DBUS_SESSION_BUS_ADDRESS="unix:path=${XDG_RUNTIME_DIR}/bus"
    ```

### Permission Issues
If you experience issues after editing files from an external account, re-apply the ACLs:
```bash
sudo setfacl -R -m u:your_user:rwx /opt/daghe
```

---

## 📂 Directory Structure
*   `bin/`: Orchestrator CLI and generated wrappers.
*   `jobs/`: Individual modules (code and data repositories).
*   `.config/systemd/user/`: Active systemd unit symlinks.
*   `logs/`: Centralised operational logs.
*   `templates/`: Blueprints for service/timer generation.

---

## 🔐 Private GitHub Repositories (SSH)

To allow DaGhE to push data to private GitHub repositories without manual intervention:

### 1. Initialise SSH
Run the following command as the `daghe` user:
```bash
uv run bin/daghe setup-ssh
```

### 2. Add the Key to GitHub
Copy the public key output by the command above. On GitHub:
*   **For the entire account**: Go to `Settings` -> `SSH and GPG keys` -> `New SSH key`.
*   **For a specific repo (Recommended)**: Go to the repository `Settings` -> `Deploy keys` -> `Add deploy key`. Ensure you tick **"Allow write access"**.

### 3. Use SSH URLs in Manifests
Ensure your `daghe-module.yaml` uses the SSH format:
`code_repo: git@github.com:username/repo.git`

### 4. Verify the Connection
```bash
ssh -T git@github.com
```
*If successful, GitHub will welcome you by your username.*
```

---

## ⚖️ Standards
*   **Language**: UK English spelling throughout.
*   **Security**: Minimalist privilege model with Zero-Sudo operation.
*   **Environment**: Full isolation via `uv`.
