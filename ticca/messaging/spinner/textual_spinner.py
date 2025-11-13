"""
Textual spinner implementation for TUI mode.
"""

from textual.app import ComposeResult
from textual.containers import Container

from .spinner_base import SpinnerBase
from .kitt_scanner import KittScanner


class TextualSpinner(Container):
    """A textual spinner widget with KITT-style scanner animation."""

    DEFAULT_CSS = """
    TextualSpinner {
        height: auto;
        width: 1fr;
        display: none;
    }

    TextualSpinner.active {
        display: block;
    }
    """

    def __init__(self, **kwargs):
        """Initialize the textual spinner."""
        super().__init__(**kwargs)
        self._is_spinning = False
        self._paused = False
        self.scanner = None

        # Register this spinner for global management
        from . import register_spinner

        register_spinner(self)

    def compose(self) -> ComposeResult:
        """Compose the spinner with the KITT scanner."""
        self.scanner = KittScanner(message=SpinnerBase.THINKING_MESSAGE)
        yield self.scanner

    def start_spinning(self):
        """Start the spinner animation."""
        if not self._is_spinning:
            self._is_spinning = True
            self._paused = False

            # Show the spinner
            self.add_class("active")

            # Ensure scanner is available
            if self.scanner is None:
                self.scanner = self.query_one(KittScanner)

            # Update message based on current state
            self._update_message()

            # Start the KITT scanner animation
            self.scanner.start_scanning()

    def stop_spinning(self):
        """Stop the spinner animation."""
        self._is_spinning = False

        # Hide the spinner
        self.remove_class("active")

        if self.scanner:
            self.scanner.stop_scanning()

        # Unregister this spinner from global management
        from . import unregister_spinner

        unregister_spinner(self)

    def _update_message(self):
        """Update the message displayed based on current state."""
        if not self.scanner:
            return

        # Check if we're awaiting user input to determine which message to show
        from ticca.tools.command_runner import is_awaiting_user_input

        if is_awaiting_user_input():
            # Show waiting message when waiting for user input
            message = SpinnerBase.WAITING_MESSAGE
        else:
            # Show thinking message during normal processing
            message = SpinnerBase.THINKING_MESSAGE

        # Add context info if available
        context_info = SpinnerBase.get_context_info()
        if context_info:
            message = f"{message} {context_info}"

        self.scanner.update_message(message)

    def pause(self):
        """Pause the spinner animation temporarily."""
        if self._is_spinning and not self._paused:
            self._paused = True
            # Hide the spinner when paused
            self.remove_class("active")
            if self.scanner:
                self.scanner.stop_scanning()

    def resume(self):
        """Resume a paused spinner animation."""
        # Check if we should show a spinner - don't resume if waiting for user input
        from ticca.tools.command_runner import is_awaiting_user_input

        if is_awaiting_user_input():
            return  # Don't resume if waiting for user input

        if self._is_spinning and self._paused:
            self._paused = False
            # Show the spinner again
            self.add_class("active")
            self._update_message()
            if self.scanner:
                self.scanner.start_scanning()
