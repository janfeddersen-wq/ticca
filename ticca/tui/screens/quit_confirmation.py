"""
Quit confirmation modal screen.
"""

from textual import on
from textual.app import ComposeResult
from textual.containers import Container, Horizontal
from textual.screen import ModalScreen
from textual.widgets import Button, Label


class QuitConfirmationScreen(ModalScreen[bool]):
    """Confirmation modal for quitting the application."""

    DEFAULT_CSS = """
    QuitConfirmationScreen {
        align: center middle;
    }

    #quit-dialog {
        width: 50;
        height: auto;
        border: round $error;
        background: $surface;
        padding: 1 2;
    }

    #quit-title {
        text-align: center;
        text-style: bold;
        color: $error;
        margin: 0 0 1 0;
    }

    #quit-message {
        width: 100%;
        text-align: center;
        padding: 1 0;
        margin: 0 0 1 0;
        color: $text;
    }

    #quit-buttons {
        layout: horizontal;
        height: 3;
        align: center middle;
        width: 100%;
        margin: 1 0 0 0;
    }

    #cancel-button {
        margin: 0 1;
        min-width: 12;
        height: 3;
        border: wide $primary;
        background: $secondary;
        color: $text;
    }

    #cancel-button:hover {
        border: wide $primary-lighten-1;
        background: $border;
    }

    #quit-button {
        margin: 0 1;
        min-width: 12;
        height: 3;
        border: wide $error;
        border-bottom: wide $error-darken-1;
        border-right: wide $error-darken-1;
        background: $error;
        color: $background;
    }

    #quit-button:hover {
        border: wide $error-lighten-1;
        border-bottom: wide $error-darken-2;
        border-right: wide $error-darken-2;
        background: $error-lighten-1;
    }

    #quit-button:focus {
        border: wide $panel;
        border-top: wide $error;
        border-left: wide $error;
        background: $error-darken-1;
        color: $error-lighten-2;
    }
    """

    def compose(self) -> ComposeResult:
        with Container(id="quit-dialog"):
            yield Label("⚠️  Quit Ticca?", id="quit-title")
            yield Label(
                "Are you sure you want to quit?\nAny unsaved work will be lost.",
                id="quit-message",
            )
            with Horizontal(id="quit-buttons"):
                yield Button("Cancel", id="cancel-button")
                yield Button("Quit", id="quit-button")

    def on_mount(self) -> None:
        """Set initial focus to the Quit button."""
        quit_button = self.query_one("#quit-button", Button)
        quit_button.focus()

    @on(Button.Pressed, "#cancel-button")
    def cancel_quit(self) -> None:
        """Cancel quitting."""
        self.dismiss(False)

    @on(Button.Pressed, "#quit-button")
    def confirm_quit(self) -> None:
        """Confirm quitting."""
        self.dismiss(True)

    def on_key(self, event) -> None:
        """Handle key events."""
        if event.key == "escape":
            self.dismiss(False)
        # Note: Enter key will automatically activate the focused button
        # No need to handle it here - Textual handles button activation
