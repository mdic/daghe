import os
import sys
from datetime import datetime, timezone
from pathlib import Path

# --- Import Bridge ---
SCRIPT_PATH = Path(__file__).resolve()
BASE_DIR = SCRIPT_PATH.parent.parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

from textual import work  # For threaded workers
from textual.app import App, ComposeResult
from textual.binding import Binding
from textual.containers import Horizontal, ScrollableContainer, Vertical
from textual.widgets import Footer, Header, Label, ListItem, ListView, Static

from core.execution import (  # Maintenance helpers
    sync_module_venv,
    upgrade_module_packages,
)
from core.manifest import ManifestError, load_module_manifest
from core.modules import get_testing_status_names, list_valid_modules
from core.state import read_state, write_state
from core.system import get_user_timers_status, stream_user_journal

# Standard DaGhE Paths
JOBS_DIR = BASE_DIR / "jobs"
STATE_DIR = BASE_DIR / "state"
PRODUCTION_PATH = Path("/opt/daghe")


class ModuleItem(ListItem):
    """Custom list item to hold module name reference."""

    def __init__(self, module_name: str) -> None:
        super().__init__(Label(module_name))
        self.module_name = module_name


class DagheTUI(App):
    """
    DaGhE TUI Dashboard - Batch 3.4
    UK English spelling. Implements non-blocking maintenance workers.
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
        self.is_busy = False  # Prevent duplicate triggers

    def compose(self) -> ComposeResult:
        is_prod = BASE_DIR == PRODUCTION_PATH
        mode_str = "PRODUCTION" if is_prod else "TESTING"
        mode_class = "mode-production" if is_prod else "mode-testing"

        yield Header()
        with Horizontal():
            with Vertical(id="sidebar"):
                yield Label("  INSTALLED MODULES", classes="section-title")
                yield ListView(id="module-list")
            with ScrollableContainer(id="detail-area"):
                yield Label(f"Current Mode: {mode_str}", classes=mode_class)
                yield Static(id="module-details")

                yield Label("STATUS", classes="section-title")
                yield Static(id="module-status")

                yield Label("MAINTENANCE ACTIONS", classes="section-title")
                yield Label(
                    "Idle", id="action-status"
                )  # Real action status (Batch 3.4)

                yield Label("LATEST LOGS", classes="section-title")
                yield Static(id="module-logs")
        yield Footer()

    def on_mount(self) -> None:
        self.action_refresh_all()

    def action_refresh_all(self) -> None:
        """UK English: Refresh both the list and the details of the selection."""
        list_view = self.query_one("#module-list", ListView)
        current_selection = None
        if list_view.highlighted_child:
            current_selection = list_view.highlighted_child.module_name

        list_view.clear()
        modules = list_valid_modules(JOBS_DIR)
        for name in modules:
            list_view.append(ModuleItem(name))

        if current_selection:
            self.update_view(current_selection)

    def on_list_view_highlighted(self, event: ListView.Highlighted) -> None:
        if event.item:
            self.update_view(event.item.module_name)

    def update_view(self, module_name: str) -> None:
        """UK English: Orchestrates the update of the detail and status panels."""
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
        status_static = self.query_one("#module-status", Static)
        status_static.remove_class("status-success", "status-failure", "status-empty")

        state = read_state(STATE_DIR, module_name)
        if not state:
            status_static.update("No run information available yet")
            status_static.add_class("status-empty")
            return

        last_run = state.get("last_run", {})
        outcome = last_run.get("outcome", "unknown")
        if outcome not in ("success", "failure"):
            outcome = "empty"

        content = [
            f"[bold]Outcome:[/bold] {outcome.upper()}",
            f"[bold]Exit Code:[/bold] {last_run.get('exit_code', 'N/A')}",
            f"[bold]Start (UTC):[/bold] {last_run.get('start', 'N/A')}",
            f"[bold]End (UTC):[/bold] {last_run.get('end', 'N/A')}",
            f"[bold]Summary:[/bold] {last_run.get('summary', 'N/A')}",
        ]
        status_static.update("\n".join(content))
        status_static.add_class(f"status-{outcome}")

    def update_logs_view(self, module_name: str) -> None:
        """Correction: Removed broad exception, added returncode check and [code] tag."""
        logs_static = self.query_one("#module-logs", Static)
        unit_name = f"auto-{module_name}.service"

        res = stream_user_journal(unit_name, lines=30, capture=True)

        if res.returncode != 0:
            logs_static.update("[red]Error:[/red] Failed to retrieve systemd journal.")
            return

        if res.stdout and res.stdout.strip():
            logs_static.update(
                f"[code]{res.stdout}[/code]"
            )  # Correction: preserve formatting
        else:
            logs_static.update("No recent journal entries found.")

    # --- BATCH 3.4: WORKERS & ACTIONS ---

    def action_sync_env(self) -> None:
        self.run_maintenance("sync")

    def action_upgrade_deps(self) -> None:
        self.run_maintenance("upgrade")

    def run_maintenance(self, action_type: str) -> None:
        """UK English: Standardised trigger logic for maintenance tasks."""
        list_view = self.query_one("#module-list", ListView)
        if not list_view.highlighted_child or self.is_busy:
            return

        module_name = list_view.highlighted_child.module_name
        self.execute_worker(module_name, action_type)

    @work(thread=True)
    def execute_worker(self, module_name: str, action_type: str) -> None:
        """UK English: Thread-based worker to prevent UI blocking."""
        self.is_busy = True
        status_label = self.query_one("#action-status", Label)
        module_cwd = JOBS_DIR / module_name / "current"

        # Update UI to running state
        self.call_from_thread(
            status_label.update, f"[yellow]Running {action_type}...[/yellow]"
        )

        start_time = datetime.now(timezone.utc).isoformat()
        try:
            if action_type == "sync":
                res = sync_module_venv(module_cwd, capture=True)
                success = res.returncode == 0
                summary = (
                    "Manual TUI Sync completed."
                    if success
                    else "Manual TUI Sync failed."
                )
                exit_code = res.returncode
            else:
                # Upgrade logic
                manifest = load_module_manifest(JOBS_DIR, module_name)
                packages = manifest.get("updates", {}).get("auto_upgrade_packages", [])
                if not packages:
                    success, exit_code, summary = True, 0, "No packages to upgrade."
                else:
                    success = upgrade_module_packages(
                        module_cwd, packages, capture=True
                    )
                    exit_code = 0 if success else 1
                    summary = (
                        "Manual TUI Upgrade completed."
                        if success
                        else "One or more packages failed."
                    )

            # Update persistent state
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

        except Exception as e:
            self.call_from_thread(status_label.update, f"[red]Error: {str(e)}[/red]")
        finally:
            self.is_busy = False
            # Refresh UI components
            self.call_from_thread(status_label.update, f"Last {action_type} finished.")
            self.call_from_thread(self.update_view, module_name)


if __name__ == "__main__":
    app = DagheTUI()
    app.run()
