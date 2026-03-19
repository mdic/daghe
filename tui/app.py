import os
import sys
from pathlib import Path

# --- Import Bridge (Identical logic to bin/daghe) ---
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

# Standard DaGhE Paths
JOBS_DIR = BASE_DIR / "jobs"
PRODUCTION_PATH = Path("/opt/daghe")


class ModuleItem(ListItem):
    """UK English: Custom list item to hold module name reference."""

    def __init__(self, module_name: str) -> None:
        super().__init__(Label(module_name))
        self.module_name = module_name


class DagheTUI(App):
    """
    DaGhE TUI Dashboard - Batch 3.1
    UK English spelling. Minimal read-only shell.
    """

    TITLE = "DaGhE Automation"
    CSS = """
        Screen { background: #1a1b26; }
        #sidebar { width: 35; border-right: solid $primary; background: #16161e; }
        #detail-area { padding: 1 2; }
        .section-title { text-style: bold; color: $accent; margin-top: 1; }
        .placeholder { color: #565f89; text-style: italic; margin: 1 0; }
        .mode-testing { color: #e0af68; }
        .mode-production { color: #9ece6a; }
        """

    BINDINGS = [
        Binding("q", "quit", "Quit"),
        Binding("r", "refresh_list", "Refresh Modules"),
    ]

    def compose(self) -> ComposeResult:
        # 1. Header with Mode Detection
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

                # Placeholders for future batches
                yield Label("STATUS", classes="section-title")
                yield Label(
                    "[Future Batch] State pulse will appear here...",
                    classes="placeholder",
                )

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
        """UK English: Initialise the module list on startup."""
        self.action_refresh_list()

    def action_refresh_list(self) -> None:
        """Scans the jobs directory and populates the sidebar."""
        list_view = self.query_one("#module-list", ListView)
        list_view.clear()

        modules = list_valid_modules(JOBS_DIR)
        for name in modules:
            list_view.append(ModuleItem(name))

        if not modules:
            self.query_one("#module-details").update(
                "No valid modules found in /jobs directory."
            )

    def on_list_view_highlighted(self, event: ListView.Highlighted) -> None:
        """UK English: Updates the detail panel when a module is selected."""
        if event.item:
            self.update_detail_view(event.item.module_name)

    def update_detail_view(self, module_name: str) -> None:
        """Loads manifest data and renders the detail view."""
        detail_static = self.query_one("#module-details")

        try:
            # Using confirmed signature: (jobs_dir: Path, module_name: str)
            manifest = load_module_manifest(JOBS_DIR, module_name)
            m = manifest.get("module", {})
            s = manifest.get("schedule", {})
            g = manifest.get("git", {})

            content = [
                f"[bold]Module:[/bold] {module_name}",
                f"[bold]Description:[/bold] {m.get('description', 'N/A')}",
                f"[bold]Type:[/bold] {m.get('type', 'N/A')}",
                f"[bold]Entrypoint:[/bold] {m.get('entrypoint', 'N/A')}",
                "",
                f"[bold]Schedule:[/bold] {s.get('calendar', 'Manual only')}",
                f"[bold]Random Delay:[/bold] {s.get('random_delay', '0s')}",
                "",
                f"[bold]Code Repository:[/bold] {g.get('code_repo', 'N/A')}",
                f"[bold]Data Repository:[/bold] {g.get('data_repo', 'N/A')}",
            ]
            detail_static.update("\n".join(content))
        except ManifestError as e:
            # Only catch known manifest-related failures
            detail_static.update(
                f"[red]Error:[/red] Could not load manifest for {module_name}.\n{str(e)}"
            )


if __name__ == "__main__":
    app = DagheTUI()
    app.run()
