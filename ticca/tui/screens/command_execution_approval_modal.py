"""
Command Execution Approval modal for TUI mode.
"""

from textual import on
from textual.app import ComposeResult
from textual.containers import Container, Horizontal, Vertical
from textual.screen import ModalScreen
from textual.widgets import Button, Input, Label, Static


class CommandExecutionApprovalModal(ModalScreen):
    """Modal screen for approving shell command execution."""

    DEFAULT_CSS = """
    CommandExecutionApprovalModal {
        align: center middle;
    }

    #command-exec-dialog {
        width: 90;
        height: auto;
        max-height: 35;
        border: round $primary;
        background: $surface;
        padding: 1 2;
    }

    #command-exec-title {
        text-align: center;
        text-style: bold;
        color: $accent;
        margin: 0 0 1 0;
    }

    #command-info-container {
        margin: 0 0 2 0;
        padding: 1;
        background: $panel;
        border: round $border;
    }

    #command-label {
        color: $warning;
        text-style: bold;
        margin: 0 0 1 0;
    }

    #command-text {
        color: $text;
        margin: 0 0 1 0;
        padding: 1;
        background: $background;
        border: round $border;
    }

    #cwd-label {
        color: $text-muted;
        text-style: italic;
        margin: 0 0 0 0;
    }

    #action-buttons {
        layout: horizontal;
        height: 3;
        align: center middle;
        margin: 1 0 0 0;
    }

    #approve-btn, #reject-btn, #feedback-btn {
        margin: 0 1;
        min-width: 15;
        height: 3;
    }

    #approve-btn {
        border: wide $success;
        border-bottom: wide $success-darken-1;
        border-right: wide $success-darken-1;
        background: $success;
        color: $background;
    }

    #approve-btn:hover {
        border: wide $success-lighten-1;
        border-bottom: wide $success-darken-2;
        border-right: wide $success-darken-2;
        background: $success-lighten-1;
    }

    #approve-btn:focus {
        border: wide $panel;
        border-top: wide $success;
        border-left: wide $success;
        background: $success-darken-1;
        color: $success-lighten-2;
    }

    #reject-btn {
        border: wide $error;
        border-bottom: wide $error-darken-1;
        border-right: wide $error-darken-1;
        background: $error;
        color: $background;
    }

    #reject-btn:hover {
        border: wide $error-lighten-1;
        border-bottom: wide $error-darken-2;
        border-right: wide $error-darken-2;
        background: $error-lighten-1;
    }

    #reject-btn:focus {
        border: wide $panel;
        border-top: wide $error;
        border-left: wide $error;
        background: $error-darken-1;
        color: $error-lighten-2;
    }

    #feedback-btn {
        border: wide $warning;
        border-bottom: wide $warning-darken-1;
        border-right: wide $warning-darken-1;
        background: $warning;
        color: $background;
    }

    #feedback-btn:hover {
        border: wide $warning-lighten-1;
        border-bottom: wide $warning-darken-2;
        border-right: wide $warning-darken-2;
        background: $warning-lighten-1;
    }

    #feedback-btn:focus {
        border: wide $panel;
        border-top: wide $warning;
        border-left: wide $warning;
        background: $warning-darken-1;
        color: $warning-lighten-2;
    }

    #feedback-container {
        display: none;
        margin: 1 0 0 0;
        padding: 1;
        background: $panel;
        border: round $border;
    }

    #feedback-container.visible {
        display: block;
    }

    #feedback-input {
        width: 100%;
        margin: 1 0;
        border: round $primary;
        background: $panel;
        color: $foreground;
        padding: 0 1;
    }

    #feedback-input:focus {
        border: round $accent;
        background: $secondary;
    }

    #submit-feedback-btn {
        width: 100%;
        height: 3;
        border: wide $accent;
        border-bottom: wide $accent-darken-1;
        border-right: wide $accent-darken-1;
        background: $primary;
        color: $background;
    }

    #submit-feedback-btn:hover {
        border: wide $accent-lighten-1;
        border-bottom: wide $secondary;
        border-right: wide $secondary;
        background: $primary-lighten-1;
    }

    #submit-feedback-btn:focus {
        border: wide $panel;
        border-top: wide $accent;
        border-left: wide $accent;
        background: $primary-darken-1;
        color: $accent;
    }
    """

    def __init__(
        self,
        command: str,
        cwd: str | None = None,
        **kwargs
    ):
        super().__init__(**kwargs)
        self.command = command
        self.cwd = cwd
        self.result = {"approved": False, "feedback": None}

    def compose(self) -> ComposeResult:
        with Container(id="command-exec-dialog"):
            yield Label("⚡ Shell Command Approval", id="command-exec-title")

            # Command info
            with Vertical(id="command-info-container"):
                yield Label("Command to execute:", id="command-label")
                yield Static(f"$ {self.command}", id="command-text")

                if self.cwd:
                    yield Label(f"📂 Working directory: {self.cwd}", id="cwd-label")

            # Action buttons
            with Container(id="action-buttons"):
                yield Button("✓ Approve", id="approve-btn")
                yield Button("✗ Reject", id="reject-btn")
                yield Button("💬 Reject with Feedback", id="feedback-btn")

            # Feedback input (hidden by default)
            with Vertical(id="feedback-container"):
                yield Label("Provide feedback to the agent:")
                yield Input(
                    placeholder="Tell the agent why you rejected this command...",
                    id="feedback-input"
                )
                yield Button("Submit Feedback", id="submit-feedback-btn")

    @on(Button.Pressed, "#approve-btn")
    def approve(self) -> None:
        """Approve the command execution."""
        self.result = {"approved": True, "feedback": None}
        self.dismiss(self.result)

    @on(Button.Pressed, "#reject-btn")
    def reject(self) -> None:
        """Reject the command execution."""
        self.result = {"approved": False, "feedback": None}
        self.dismiss(self.result)

    @on(Button.Pressed, "#feedback-btn")
    def show_feedback_input(self) -> None:
        """Show feedback input."""
        feedback_container = self.query_one("#feedback-container")
        feedback_container.add_class("visible")

        # Hide buttons
        self.query_one("#action-buttons").display = False

        # Focus input
        self.query_one("#feedback-input", Input).focus()

    @on(Button.Pressed, "#submit-feedback-btn")
    def submit_feedback(self) -> None:
        """Submit feedback and reject."""
        feedback = self.query_one("#feedback-input", Input).value.strip()
        self.result = {
            "approved": False,
            "feedback": feedback if feedback else None
        }
        self.dismiss(self.result)

    def on_mount(self) -> None:
        """Set initial focus to the approve button."""
        try:
            approve_btn = self.query_one("#approve-btn", Button)
            approve_btn.focus()
        except Exception:
            pass

    def on_key(self, event) -> None:
        """Handle key events."""
        if event.key == "escape":
            self.reject()
