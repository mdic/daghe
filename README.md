# DaGhE: Data Gathering Environment

DaGhE is an orchestration system for managing and monitoring automated data gathering jobs on a Linux server.

---

## 1. What you can do with DaGhE

*   **Automate Tasks**: Run and manage multiple jobs (modules) independently.
*   **Monitor Health**: Use a real-time TUI dashboard to check the status of all modules.
*   **Manage Environments**: Automatically handle Python dependencies and isolated environments.
*   **Stay Informed**: Receive instant alerts via Telegram when tasks succeed or fail.

---

## 2. Installation (Minimal)

1.  **Prepare System**: Ensure `python3`, `uv`, `ffmpeg`, and `deno` are installed.
2.  **Create User**:
    ```bash
    sudo useradd -m -d /opt/daghe -s /bin/bash daghe
    sudo loginctl enable-linger daghe
    ```
3.  **Deploy**: Clone the orchestration repository directly into `/opt/daghe` and ensure the `daghe` user owns the directory.
4.  **Initialise**: Switch to the `daghe` user and run `uv sync`.

---

## 3. Basic Usage

Use the `dgh` CLI (the main DaGhE command-line tool) for day-to-day management:

*   **Check Status**: `uv run bin/dgh status`
*   **Register Module**: `uv run bin/dgh install <module-name>`
*   **Run Job Manually**: `uv run bin/dgh run <module-name>`
*   **Update Dependencies**: `uv run bin/dgh upgrade <module-name>`
*   **View Module Logs**: `uv run bin/dgh logs <module-name>`

---

## 4. TUI Quick Guide

The Terminal User Interface (TUI) provides a live overview of your automation suite.

*   **Launch**: `uv run python -m tui.app`
*   **Sidebar**: Navigate through installed modules using the arrow keys.
*   **Detail View**: View the configuration, last-run outcome, and recent logs for the selected module.
*   **Refresh**: Press `R` to reload the state of all modules and indicators.
*   **Quit**: Press `Q` to exit.

---

## 5. Notifications (Telegram)

DaGhE is configured to send critical maintenance and job updates to a Telegram channel.

*   **Configuration**: Set your bot credentials in `config/telegram.env`.
*   **Templates**: Customise alert prefixes and emojis in `config/telegram-templates.sh`.
*   **Purpose**: Receive notifications for important system events such as task outcomes and maintenance operations.

---

## 6. Logs & Troubleshooting

*   **Application Logs**: Module output is stored in the `logs/` directory inside the DaGhE installation.
*   **System Logs**: Use `journalctl --user` to inspect system-level execution logs if applicable.
*   **Live View**: Use the `run` command via CLI to see immediate output in your terminal.

---

## 7. Where to go next

For advanced configuration and technical details, refer to the following documents:

*   **Technical Architecture**: `docs/ARCHITECTURE.md`
*   **AI Protocol & Development**: `docs/LLM_PLAYBOOK.md`
*   **Future Roadmap**: `docs/ROADMAP.md`
