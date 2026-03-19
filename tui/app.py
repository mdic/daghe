import os
import subprocess  # Added for narrow exception handling
import sys
from datetime import datetime, timezone
from pathlib import Path

# --- Import Bridge ---
SCRIPT_PATH = Path(__file__).resolve()
BASE_DIR = SCRIPT_PATH.parent.parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

from textual import work
from textual.app import App, ComposeResult
from textual.binding import Binding
from textual.containers import Horizontal, ScrollableContainer, Vertical
from textual.widgets import Footer, Header, Label, ListItem, ListView, Static

from core.execution import sync_module_venv, upgrade_module_packages
from core.manifest import ManifestError, load_module_manifest
from core.modules import list_valid_modules
from core.state import is_module_running, read_state, write_state
from core.system import stream_user_journal

# Standard DaGhE Paths
JOBS_DIR = BASE_DIR / "jobs"
STATE_DIR = BASE_DIR / "state"
PRODUCTION_PATH = Path("/opt/daghe")


class ModuleItem(ListItem):
    """UK English: Custom item containing the module name and a status marker."""

    def __init__(self, module_name: str, is_active: bool) -> None:
        super().__init__()
        self.module_name = module_name
        self.is_active = is_active

    def compose(self) -> ComposeResult:
        yield Label(" • ", classes="running-marker")
        yield Label(self.module_name)
        if self.is_active:
            self.add_class("running-active")


class DagheTUI(App):
    """
    DaGhE TUI Dashboard - Batch 3.5
    UK English spelling. Refined non-blocking interaction model.
    """

    TITLE = "DaGhE Automation"
    CSS_PATH = "styles.tcss"

    BINDINGS = [
        Binding("q", "quit", "Quit"),
        Binding("r", "refresh_all", "Refresh"),
        Binding("s", "sync_env", "Sync Env"),
        Binding("u", "upgrade_deps", "Upgrade Deps"),
    ]

    def __init__(self):
        super().__init__()
        self.is_busy = False

    def compose(self) -> ComposeResult:
        is_prod = BASE_DIR == PRODUCTION_PATH
        mode_str = "PRODUCTION" if is_prod else "TESTING"
        mode_class = "mode-production" if is_prod else "mode-testing"

        yield Header()
        with Horizontal():
            with Vertical(id="sidebar"):
                yield Label("  MODULES", classes="section-title")
                yield ListView(id="module-list")
            with ScrollableContainer(id="detail-area"):
                yield Label(f"Current Mode: {mode_str}", classes=mode_class)
                yield Static(id="module-details")

                yield Label("STATUS", classes="section-title")
                yield Static(id="module-status")

                yield Label("MAINTENANCE ACTIONS", classes="section-title")
                yield Label("Idle", id="action-status")

                yield Label("LATEST LOGS", classes="section-title")
                yield Static(id="module-logs")
        yield Footer()

    def on_mount(self) -> None:
        self.action_refresh_all()

    def action_refresh_all(self) -> None:
        """UK English: Unified refresh path for the entire TUI state."""
        list_view = self.query_one("#module-list", ListView)

        # Save focus index
        current_index = list_view.index

        list_view.clear()
        modules = list_valid_modules(JOBS_DIR)
        for name in modules:
            # Item 1: Sidebar indicator logic
            active = is_module_running(STATE_DIR, name)
            list_view.append(ModuleItem(name, active))

        # Restore focus and update details
        if modules:
            list_view.index = current_index if current_index is not None else 0
            selected_name = list_view.highlighted_child.module_name
            self.update_view(selected_name)

    def on_list_view_highlighted(self, event: ListView.Highlighted) -> None:
        if event.item:
            self.update_view(event.item.module_name)

    def update_view(self, module_name: str) -> None:
        """UK English: Standardised detail refresh."""
        self.update_detail_view(module_name)
        self.update_status_view(module_name)
        self.update_logs_view(module_name)

    def update_detail_view(self, module_name: str) -> None:
        detail_static = self.query_one("#module-details", Static)
        try:
            manifest = load_module_manifest(JOBS_DIR, module_name)
            m = manifest.get("module", {})
            s = manifest.get("schedule", {})

            content = [
                f"[bold]Module:[/bold] {module_name}",
                f"[bold]Description:[/bold] {m.get('description', 'N/A')}",
                f"[bold]Type:[/bold] {m.get('type', 'N/A')}",
                f"[bold]Schedule:[/bold] {s.get('calendar', 'Manual only')}",
            ]
            detail_static.update("\n".join(content))
        except ManifestError as e:
            detail_static.update(f"[red]Error:[/red] {str(e)}")

    def update_status_view(self, module_name: str) -> None:
        """UK English: Fetches health pulse and applies semantic status classes."""
        status_static = self.query_one("#module-status", Static)

        # Clear all potential dynamic classes to prevent stale states
        status_static.remove_class(
            "status-success",
            "status-failure",
            "status-empty",
            "live-running",
            "live-idle",
        )

        # 1. Determine running state (Semantic CSS only)
        is_running = is_module_running(STATE_DIR, module_name)
        live_text = "Running now" if is_running else "Idle"
        live_class = "live-running" if is_running else "live-idle"

        state = read_state(STATE_DIR, module_name)

        if not state:
            status_static.update(
                f"Live Status: {live_text}\n\nNo run information available yet"
            )
            status_static.add_class("status-empty")
            status_static.add_class(live_class)
            return

        last_run = state.get("last_run", {})
        outcome = last_run.get("outcome", "unknown")
        if outcome not in ("success", "failure"):
            outcome = "empty"

        # Build plain text content (Styling moved to TCSS)
        content = [
            f"Live Status: {live_text}",
            "",
            f"Last Outcome: {outcome.upper()}",
            f"Exit Code: {last_run.get('exit_code', 'N/A')}",
            f"Start (UTC): {last_run.get('start', 'N/A')}",
            f"End (UTC): {last_run.get('end', 'N/A')}",
            f"Summary: {last_run.get('summary', 'N/A')}",
        ]

        status_static.update("\n".join(content))
        status_static.add_class(f"status-{outcome}")
        status_static.add_class(live_class)  # Apply the corrected live class

    def update_logs_view(self, module_name: str) -> None:
        logs_static = self.query_one("#module-logs", Static)
        unit_name = f"auto-{module_name}.service"

        res = stream_user_journal(unit_name, lines=30, capture=True)
        if res.returncode != 0:
            logs_static.update("[red]Error:[/red] Failed to retrieve systemd journal.")
            return

        if res.stdout and res.stdout.strip():
            logs_static.update(f"[code]{res.stdout}[/code]")
        else:
            logs_static.update("No recent journal entries found.")

    def action_sync_env(self) -> None:
        self.run_maintenance("sync")

    def action_upgrade_deps(self) -> None:
        self.run_maintenance("upgrade")

    def run_maintenance(self, action_type: str) -> None:
        """UK English: Hardened trigger with manifest validation."""
        list_view = self.query_one("#module-list", ListView)
        status_label = self.query_one("#action-status", Label)

        if not list_view.highlighted_child or self.is_busy:
            return

        module_name = list_view.highlighted_child.module_name

        # Item 3: Manifest-error action hardening
        try:
            load_module_manifest(JOBS_DIR, module_name)
        except ManifestError:
            status_label.update("[red]Error: Invalid manifest. Action blocked.[/red]")
            return

        self.execute_worker(module_name, action_type)

    @work(thread=True)
    def execute_worker(self, module_name: str, action_type: str) -> None:
        """UK English: Refined worker logic with precise outcome reporting."""
        self.is_busy = True
        status_label = self.query_one("#action-status", Label)
        module_cwd = JOBS_DIR / module_name / "current"

        # Fix 3: Added visual "busy" class and clear running state
        self.call_from_thread(status_label.add_class, "busy")
        self.call_from_thread(status_label.update, f"Running {action_type}...")

        start_time = datetime.now(timezone.utc).isoformat()
        final_msg = ""

        try:
            if action_type == "sync":
                res = sync_module_venv(module_cwd, capture=True)
                success = res.returncode == 0
                exit_code = res.returncode
                summary = (
                    "Manual TUI Sync completed."
                    if success
                    else "Manual TUI Sync failed."
                )
            else:
                manifest = load_module_manifest(JOBS_DIR, module_name)
                packages = manifest.get("updates", {}).get("auto_upgrade_packages", [])
                if not packages:
                    success, exit_code, summary = (
                        True,
                        0,
                        "No packages defined to upgrade.",
                    )
                else:
                    success = upgrade_module_packages(
                        module_cwd, packages, capture=True
                    )
                    exit_code = 0 if success else 1
                    summary = (
                        "Manual TUI Upgrade finished."
                        if success
                        else "One or more packages failed."
                    )

            # Persist the result
            outcome = "success" if success else "failure"
            state_payload = {
                "module": module_name,
                "last_run": {
                    "start": start_time,
                    "end": datetime.now(timezone.utc).isoformat(),
                    "exit_code": exit_code,
                    "outcome": outcome,
                    "summary": summary,
                },
            }
            write_state(STATE_DIR, module_name, state_payload)

            # Prepare final message for the UI
            color = "green" if success else "red"
            final_msg = f"[{color}]{summary}[/{color}]"

        # Fix 2: Narrower exception handling
        except (ManifestError, subprocess.SubprocessError, OSError) as e:
            final_msg = f"[red]System Error: {type(e).__name__}[/red]"

        finally:
            self.is_busy = False
            self.call_from_thread(status_label.remove_class, "busy")
            if final_msg:
                self.call_from_thread(status_label.update, final_msg)
            # Item 2: Unified refresh logic on completion
            self.call_from_thread(self.action_refresh_all)


if __name__ == "__main__":
    DagheTUI().run()
