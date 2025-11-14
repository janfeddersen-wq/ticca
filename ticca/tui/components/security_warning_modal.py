"""
Security warning modal for displaying detected secrets.
"""

from textual import on
from textual.app import ComposeResult
from textual.containers import Container, Horizontal, Vertical
from textual.screen import ModalScreen
from textual.widgets import Button, Label, Static


class SecurityWarningModal(ModalScreen):
    """Modal screen for security warnings about detected secrets."""

    DEFAULT_CSS = """
    SecurityWarningModal {
        align: center middle;
    }

    #security-warning-dialog {
        width: 90;
        height: auto;
        max-height: 35;
        border: thick $error;
        background: $surface;
        padding: 1 2;
    }

    #security-warning-title {
        width: 100%;
        text-align: center;
        text-style: bold;
        color: $error;
        margin: 0 0 1 0;
    }

    #security-warning-content {
        width: 100%;
        height: auto;
        max-height: 20;
        overflow-y: auto;
        margin: 0 0 1 0;
        background: $panel;
        padding: 1;
        border: solid $error;
    }

    #security-warning-buttons {
        layout: horizontal;
        width: 100%;
        height: auto;
        align: center middle;
    }

    #security-warning-buttons Button {
        margin: 0 1;
        min-width: 18;
        height: 3;
    }

    #continue-button {
        border: wide $warning;
        border-bottom: wide $warning-darken-1;
        border-right: wide $warning-darken-1;
        background: $warning;
        color: $background;
        text-style: bold;
    }

    #continue-button:hover {
        border: wide $warning-lighten-1;
        border-bottom: wide $warning-darken-1;
        border-right: wide $warning-darken-1;
        background: $warning-lighten-1;
    }

    #unstage-button {
        border: wide $accent;
        border-bottom: wide $accent-darken-1;
        border-right: wide $accent-darken-1;
        background: $primary;
        color: $background;
        text-style: bold;
    }

    #unstage-button:hover {
        border: wide $accent-lighten-1;
        border-bottom: wide $accent-darken-1;
        border-right: wide $accent-darken-1;
        background: $primary-lighten-1;
    }

    #cancel-button {
        border: wide $primary;
        border-bottom: wide $primary-darken-1;
        border-right: wide $primary-darken-1;
        background: $secondary;
        color: $text;
        text-style: bold;
    }

    #cancel-button:hover {
        border: wide $primary-lighten-1;
        border-bottom: wide $primary-darken-1;
        border-right: wide $primary-darken-1;
        background: $border;
    }
    """

    def __init__(self, secrets: list, affected_files: list[str], **kwargs):
        super().__init__(**kwargs)
        self.secrets = secrets
        self.affected_files = affected_files

    def compose(self) -> ComposeResult:
        with Container(id="security-warning-dialog"):
            yield Label("⚠️  SECURITY WARNING", id="security-warning-title")

            with Vertical(id="security-warning-content"):
                yield Static(
                    f"Found {len(self.secrets)} potential secret(s) in staged changes!\n",
                    markup=True,
                )

                # Show detected secrets
                for secret in self.secrets:
                    location = (
                        f"{secret.file_path}:{secret.line_number}"
                        if secret.line_number
                        else secret.file_path
                    )
                    yield Static(
                        f"• [yellow]{secret.secret_type}[/yellow] in [cyan]{location}[/cyan]"
                    )
                    yield Static(f"  Match: [dim]{secret.matched_text}[/dim]\n")

                # Show affected files
                yield Static(f"\nAffected files ({len(self.affected_files)}):")
                for file in self.affected_files:
                    yield Static(f"  - {file}")

                yield Static(
                    "\n[dim]Committing secrets can expose sensitive data.[/dim]"
                )

            with Horizontal(id="security-warning-buttons"):
                yield Button("Unstage Files", id="unstage-button", variant="primary")
                yield Button("Cancel", id="cancel-button")
                yield Button("Continue Anyway", id="continue-button", variant="warning")

    @on(Button.Pressed, "#continue-button")
    def on_continue_pressed(self) -> None:
        """Continue with commit despite warnings."""
        self.dismiss("continue")

    @on(Button.Pressed, "#unstage-button")
    def on_unstage_pressed(self) -> None:
        """Unstage the files with secrets."""
        self.dismiss("unstage")

    @on(Button.Pressed, "#cancel-button")
    def on_cancel_pressed(self) -> None:
        """Cancel the commit."""
        self.dismiss("cancel")

    def on_key(self, event) -> None:
        """Handle key events."""
        if event.key == "escape":
            self.dismiss("cancel")
