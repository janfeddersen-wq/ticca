"""
Easy Mode selection modal screen.
"""

from textual import on
from textual.app import ComposeResult
from textual.containers import Container, Horizontal, Vertical
from textual.screen import ModalScreen
from textual.widgets import Button, Label


class EasyModeSelectionScreen(ModalScreen[bool]):
    """Modal for selecting Easy Mode preference on first run."""

    DEFAULT_CSS = """
    EasyModeSelectionScreen {
        align: center middle;
    }

    #easy-mode-dialog {
        width: 70;
        height: auto;
        border: round $primary;
        background: $surface;
        padding: 2 3;
    }

    #easy-mode-title {
        text-align: center;
        text-style: bold;
        color: $primary;
        margin: 0 0 1 0;
    }

    #easy-mode-description {
        width: 100%;
        padding: 1 0;
        margin: 0 0 1 0;
        color: $text;
    }

    #mode-options {
        layout: vertical;
        height: auto;
        width: 100%;
        margin: 1 0;
    }

    .mode-option {
        layout: vertical;
        height: auto;
        width: 100%;
        margin: 0 0 1 0;
        padding: 1;
        border: round $border;
        background: $panel;
    }

    .mode-title {
        text-style: bold;
        color: $success;
        margin: 0 0 1 0;
    }

    .mode-desc {
        color: $text-muted;
    }

    #easy-mode-buttons {
        layout: horizontal;
        height: 3;
        align: center middle;
        width: 100%;
        margin: 1 0 0 0;
    }

    .mode-button {
        margin: 0 1;
        min-width: 15;
        height: 3;
    }

    #easy-mode-button {
        border: wide $success;
        background: $success;
        color: $background;
    }

    #easy-mode-button:hover {
        background: $success-lighten-1;
    }

    #normal-mode-button {
        border: wide $primary;
        background: $secondary;
        color: $text;
    }

    #normal-mode-button:hover {
        background: $border;
    }
    """

    def compose(self) -> ComposeResult:
        with Container(id="easy-mode-dialog"):
            yield Label("⚙️  Choose Your Experience", id="easy-mode-title")
            yield Label(
                "Welcome to Ticca! Please select your preferred mode:",
                id="easy-mode-description",
            )

            with Vertical(id="mode-options"):
                with Container(classes="mode-option"):
                    yield Label("🎯 Easy Mode (Recommended for Beginners)", classes="mode-title")
                    yield Label(
                        "• Simplified interface with one agent\n"
                        "• Focus on coding tasks\n"
                        "• Uses default model settings",
                        classes="mode-desc",
                    )

                with Container(classes="mode-option"):
                    yield Label("🔧 Normal Mode (Advanced Users)", classes="mode-title")
                    yield Label(
                        "• Full access to all agents\n"
                        "• Customize models per agent\n"
                        "• Advanced configuration options",
                        classes="mode-desc",
                    )

            with Horizontal(id="easy-mode-buttons"):
                yield Button("Easy Mode", id="easy-mode-button", classes="mode-button")
                yield Button("Normal Mode", id="normal-mode-button", classes="mode-button")

    def on_mount(self) -> None:
        """Set initial focus to the Easy Mode button."""
        easy_button = self.query_one("#easy-mode-button", Button)
        easy_button.focus()

    @on(Button.Pressed, "#easy-mode-button")
    def select_easy_mode(self) -> None:
        """User selected Easy Mode."""
        self.dismiss(True)

    @on(Button.Pressed, "#normal-mode-button")
    def select_normal_mode(self) -> None:
        """User selected Normal Mode."""
        self.dismiss(False)
