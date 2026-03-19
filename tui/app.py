import os
import sys
from pathlib import Path

# --- Import Bridge ---
SCRIPT_PATH = Path(__file__).resolve()
BASE_DIR = SCRIPT_PATH.parent.parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

from textual.app import App, ComposeResult
from textual.binding import Binding
from textual.containers import Horizontal, ScrollableContainer, Vertical
from textual.widgets import Footer, Header, Label, ListItem, ListView, Static

from core.manifest import ManifestError, load_module_manifest
from core.modules import list_valid_modules
from core.state import read_state

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
    DaGhE TUI Dashboard - Batch 3.2
    UK English spelling. Integrated with core.state for health monitoring.
    """

    TITLE = "DaGhE Automation"

    # Visual styling is now externalised
    CSS_PATH = "styles.tcss"

    BINDINGS = [
        Binding("q", "quit", "Quit"),
        Binding("r", "refresh_all", "Refresh"),
    ]

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

                # Module Metadata
                yield Static(id="module-details")

                # Real Status Panel (Batch 3.2)
                yield Label("STATUS", classes="section-title")
                yield Static(id="module-status")

                # Placeholders for future batches
                yield Label("MAINTENANCE ACTIONS", classes="section-title")
                yield Label(
                    "[Future Batch] Sync/Upgrade buttons will appear here...",
                    classes="placeholder",
                )

                yield Label("LATEST LOGS", classes="section-title")
                yield Label(
                    "[Future Batch] Journalctl snapshot will appear here...",
                    classes="placeholder",
                )
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
        """
        UK English: Fetches the latest pulse from the state directory.
        Applies semantic CSS classes based on archival outcome.
        """
        status_static = self.query_one("#module-status", Static)
        status_static.set_classes("")  # Reset classes

        state = read_state(STATE_DIR, module_name)

        if not state:
            status_static.update("No run information available yet")
            status_static.add_class("status-empty")
            return

        last_run = state.get("last_run", {})
        outcome = last_run.get("outcome", "unknown")

        content = [
            f"[bold]Outcome:[/bold] {outcome.upper()}",
            f"[bold]Exit Code:[/bold] {last_run.get('exit_code', 'N/A')}",
            f"[bold]Start:[/bold] {last_run.get('start', 'N/A')}",
            f"[bold]End:[/bold] {last_run.get('end', 'N/A')}",
            f"[bold]Summary:[/bold] {last_run.get('summary', 'N/A')}",
        ]

        status_static.update("\n".join(content))
        status_static.add_class(f"status-{outcome}")


if __name__ == "__main__":
    app = DagheTUI()
    app.run()
