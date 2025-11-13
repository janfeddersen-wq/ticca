"""
Approval modal for tool execution in TUI mode.
"""

from textual import on
from textual.app import ComposeResult
from textual.containers import Container, Vertical
from textual.screen import ModalScreen
from textual.widgets import Button, Input, Label, Static
from rich.text import Text


class ApprovalModal(ModalScreen):
    """Modal screen for approving tool executions."""

    DEFAULT_CSS = """
    ApprovalModal {
        align: center middle;
    }

    #approval-dialog {
        width: 90;
        height: auto;
        max-height: 35;
        border: thick $accent;
        background: $surface;
        padding: 1 2;
    }

    #approval-title {
        text-align: center;
        text-style: bold;
        color: $accent;
        margin: 0 0 1 0;
    }

    #approval-content {
        height: auto;
        max-height: 20;
        overflow-y: auto;
        margin: 0 0 1 0;
        padding: 1;
        background: $panel;
        border: round $border;
    }

    #approval-buttons {
        layout: horizontal;
        height: 3;
        align: center middle;
        margin: 1 0 0 0;
    }

    #approve-button, #reject-button, #feedback-button {
        margin: 0 1;
        min-width: 15;
        height: 3;
    }

    #approve-button {
        border: wide $success;
        background: $success;
        color: $background;
    }

    #approve-button:hover {
        border: wide $success;
        background: $success-darken-1;
    }

    #reject-button {
        border: wide $error;
        background: $error;
        color: $background;
    }

    #reject-button:hover {
        border: wide $error;
        background: $error-darken-1;
    }

    #feedback-button {
        border: wide $warning;
        background: $warning;
        color: $background;
    }

    #feedback-button:hover {
        border: wide $warning;
        background: $warning-darken-1;
    }

    #feedback-input-container {
        display: none;
        margin: 1 0;
    }

    #feedback-input-container.visible {
        display: block;
    }

    #feedback-input {
        width: 100%;
        margin: 1 0;
    }

    #submit-feedback-button {
        width: 100%;
        height: 3;
        border: wide $accent;
        background: $primary;
        color: $background;
    }
    """

    def __init__(self, title: str, content: str, preview: str | None = None, **kwargs):
        super().__init__(**kwargs)
        self.title_text = title
        self.content_text = content
        self.preview_text = preview
        self.result = {"approved": False, "feedback": None}
        self.feedback_mode = False

    def compose(self) -> ComposeResult:
        with Container(id="approval-dialog"):
            yield Label(f"⚠️  {self.title_text}", id="approval-title")

            # Content
            content_widget = Static(id="approval-content")
            yield content_widget

            # Buttons
            with Container(id="approval-buttons"):
                yield Button("✓ Approve", id="approve-button", variant="success")
                yield Button("✗ Reject", id="reject-button", variant="error")
                yield Button("💬 Reject with Feedback", id="feedback-button", variant="warning")

            # Feedback input (hidden by default)
            with Vertical(id="feedback-input-container"):
                yield Label("Provide feedback to the agent:")
                yield Input(placeholder="Tell the agent what to change...", id="feedback-input")
                yield Button("Submit Feedback", id="submit-feedback-button")

    def on_mount(self) -> None:
        """Populate content when mounted."""
        content = self.query_one("#approval-content", Static)

        # Build content text
        full_text = self.content_text
        if self.preview_text:
            full_text += "\n\n" + "─" * 40 + "\nPreview:\n" + self.preview_text

        content.update(full_text)

    @on(Button.Pressed, "#approve-button")
    def approve(self) -> None:
        """Approve the operation."""
        self.result = {"approved": True, "feedback": None}
        self.dismiss(self.result)

    @on(Button.Pressed, "#reject-button")
    def reject(self) -> None:
        """Reject the operation."""
        self.result = {"approved": False, "feedback": None}
        self.dismiss(self.result)

    @on(Button.Pressed, "#feedback-button")
    def show_feedback_input(self) -> None:
        """Show feedback input."""
        feedback_container = self.query_one("#feedback-input-container")
        feedback_container.add_class("visible")

        # Hide buttons
        self.query_one("#approval-buttons").display = False

        # Focus input
        self.query_one("#feedback-input", Input).focus()

    @on(Button.Pressed, "#submit-feedback-button")
    def submit_feedback(self) -> None:
        """Submit feedback and reject."""
        feedback = self.query_one("#feedback-input", Input).value.strip()
        self.result = {
            "approved": False,
            "feedback": feedback if feedback else None
        }
        self.dismiss(self.result)

    def on_key(self, event) -> None:
        """Handle key events."""
        if event.key == "escape" and not self.feedback_mode:
            self.reject()
