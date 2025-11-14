"""
Modal component for viewing and editing commit messages.
"""

import subprocess
from textual import on
from textual.app import ComposeResult
from textual.containers import Container, Horizontal
from textual.events import Key
from textual.screen import ModalScreen
from textual.widgets import Button, Static, TextArea


class CommitMessageModal(ModalScreen):
    """Modal for viewing and editing commit messages before committing."""

    def __init__(self, message: str, create_commit: bool = True, **kwargs):
        """Initialize the modal with commit message.

        Args:
            message: Generated commit message
            create_commit: Whether to create a commit (True) or just show message (False)
            **kwargs: Additional arguments to pass to the parent class
        """
        super().__init__(**kwargs)
        self.message = message
        self.create_commit = create_commit
        self.result = {"committed": False, "message": None}

    DEFAULT_CSS = """
    CommitMessageModal {
        align: center middle;
        background: transparent;
    }

    #commit-container {
        width: 90%;
        max-width: 100;
        height: 70%;
        min-height: 25;
        background: $surface;
        border: solid $primary;
        padding: 1 2;
        layout: vertical;
    }

    #commit-title {
        width: 100%;
        margin-bottom: 0;
        color: $accent;
        text-align: center;
        text-style: bold;
        height: 1;
    }

    #commit-info {
        width: 100%;
        margin-bottom: 1;
        color: $primary-lighten-1;
        text-align: center;
        height: 1;
        text-style: dim italic;
    }

    #commit-text-area {
        width: 100%;
        height: 1fr;
        border: none;
        margin-bottom: 1;
    }

    #button-container {
        width: 100%;
        height: 3;
        align: center bottom;
        layout: horizontal;
    }

    #commit-button, #cancel-button {
        width: auto;
        height: 3;
        margin: 0 1;
        min-width: 15;
        content-align: center middle;
        border: wide $accent;
        border-bottom: wide $accent-darken-1;
        border-right: wide $accent-darken-1;
        background: $primary;
        color: $background;
        text-style: bold;
    }

    #commit-button {
        background: $success;
        border: wide $success;
    }

    #commit-button:hover {
        border: wide $success-lighten-1;
        border-bottom: wide $success-darken-1;
        border-right: wide $success-darken-1;
        background: $success-lighten-1;
        color: $background;
    }

    #commit-button:focus {
        border: wide $success-darken-1;
        border-top: wide $success;
        border-left: wide $success;
        background: $success-darken-1;
        color: $accent;
    }

    #cancel-button:hover {
        border: wide $accent-lighten-1;
        border-bottom: wide $accent-darken-1;
        border-right: wide $accent-darken-1;
        background: $primary-lighten-1;
        color: $background;
    }

    #cancel-button:focus {
        border: wide $accent-darken-1;
        border-top: wide $accent;
        border-left: wide $accent;
        background: $primary-darken-1;
        color: $accent;
    }

    #hint-text {
        width: 100%;
        color: $text;
        text-align: center;
        height: 1;
        margin-top: 1;
        text-style: italic dim;
    }
    """

    def compose(self) -> ComposeResult:
        """Create the modal layout."""
        with Container(id="commit-container"):
            if self.create_commit:
                yield Static("🚀 Commit Message", id="commit-title")
                yield Static(
                    "Review and edit the generated commit message",
                    id="commit-info"
                )
            else:
                yield Static("💭 Generated Commit Message", id="commit-title")
                yield Static(
                    "Preview of generated commit message (no commit will be created)",
                    id="commit-info"
                )

            # TextArea for editing the message
            text_area = TextArea(
                self.message,
                id="commit-text-area",
                show_line_numbers=False
            )
            yield text_area

            with Horizontal(id="button-container"):
                if self.create_commit:
                    yield Button("Commit", id="commit-button")
                    yield Button("Cancel", id="cancel-button")
                else:
                    yield Button("Close", id="cancel-button")

            if self.create_commit:
                yield Static("Ctrl+Enter to commit • Escape to cancel", id="hint-text")
            else:
                yield Static("Escape to close", id="hint-text")

    def on_mount(self) -> None:
        """Focus the editor when modal opens."""
        try:
            editor = self.query_one("#commit-text-area", TextArea)
            editor.focus()
        except Exception as e:
            print(f"CommitMessageModal on_mount exception: {e}")

    @on(Button.Pressed, "#commit-button")
    def on_commit_clicked(self) -> None:
        """Handle commit button click."""
        self._create_commit()

    @on(Button.Pressed, "#cancel-button")
    def on_cancel_clicked(self) -> None:
        """Handle cancel button click."""
        self._close_modal()

    def on_key(self, event: Key) -> None:
        """Handle key events."""
        if event.key == "escape":
            self._close_modal()
            event.prevent_default()
        elif event.key == "ctrl+enter" and self.create_commit:
            self._create_commit()
            event.prevent_default()

    def _create_commit(self) -> None:
        """Create the git commit with the current message."""
        try:
            editor = self.query_one("#commit-text-area", TextArea)
            message = editor.text.strip()

            if not message:
                from ticca.messaging import emit_error
                emit_error("Commit message cannot be empty")
                return

            # Create the commit
            result = subprocess.run(
                ["git", "commit", "-m", message],
                capture_output=True,
                text=True,
                check=False
            )

            if result.returncode == 0:
                from ticca.messaging import emit_info
                emit_info(f"✓ Commit created successfully")
                if result.stdout:
                    emit_info(result.stdout.strip())

                self.result = {"committed": True, "message": message}
                self.dismiss(self.result)
            else:
                from ticca.messaging import emit_error
                emit_error(f"Failed to create commit: {result.stderr.strip()}")

        except Exception as e:
            from ticca.messaging import emit_error
            emit_error(f"Error creating commit: {e}")

    def _close_modal(self) -> None:
        """Close the modal without committing."""
        self.result = {"committed": False, "message": None}
        self.dismiss(self.result)
