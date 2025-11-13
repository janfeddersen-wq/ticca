"""
Human feedback modal for agents to ask questions with options.
"""

from textual import on
from textual.app import ComposeResult
from textual.containers import Container, Vertical
from textual.screen import ModalScreen
from textual.widgets import Button, Input, Label, RadioButton, RadioSet, Static


class HumanFeedbackModal(ModalScreen):
    """Modal screen for agents to get human feedback with options."""

    DEFAULT_CSS = """
    HumanFeedbackModal {
        align: center middle;
    }

    #feedback-dialog {
        width: 80;
        height: auto;
        max-height: 40;
        border: thick $primary;
        background: $surface;
        padding: 1 2;
    }

    #feedback-title {
        text-align: center;
        text-style: bold;
        color: $primary;
        margin: 0 0 1 0;
    }

    #feedback-question {
        height: auto;
        margin: 0 0 2 0;
        padding: 1;
        background: $panel;
        border: round $border;
        color: $text;
    }

    #feedback-options {
        height: auto;
        margin: 0 0 1 0;
        padding: 1;
    }

    RadioSet {
        height: auto;
        background: transparent;
    }

    RadioButton {
        height: auto;
        margin: 0 0 1 0;
        background: transparent;
    }

    #custom-input-container {
        display: none;
        margin: 1 0;
        padding: 1;
        background: $panel;
        border: round $border;
    }

    #custom-input-container.visible {
        display: block;
    }

    #custom-input {
        width: 100%;
        margin: 0 0 1 0;
    }

    #feedback-buttons {
        layout: horizontal;
        height: 3;
        align: center middle;
        margin: 1 0 0 0;
    }

    #submit-button, #cancel-button {
        margin: 0 1;
        min-width: 12;
        height: 3;
    }

    #submit-button {
        border: wide $accent;
        background: $primary;
        color: $background;
    }

    #submit-button:hover {
        border: wide $accent-lighten-1;
        background: $primary-lighten-1;
    }

    #cancel-button {
        border: wide $error;
        background: $error;
        color: $background;
    }

    #cancel-button:hover {
        border: wide $error;
        background: $error-darken-1;
    }
    """

    def __init__(self, question: str, options: list[str], **kwargs):
        super().__init__(**kwargs)
        self.question_text = question
        self.options_list = options[:3]  # Max 3 options
        self.result = None

    def compose(self) -> ComposeResult:
        with Container(id="feedback-dialog"):
            yield Label("🤔 Agent Needs Your Input", id="feedback-title")

            # Question
            yield Static(self.question_text, id="feedback-question")

            # Options
            with Vertical(id="feedback-options"):
                with RadioSet(id="option-radioset"):
                    for i, option in enumerate(self.options_list):
                        yield RadioButton(option, id=f"option-{i}")
                    yield RadioButton("Other (custom answer)", id="option-custom")

            # Custom input (hidden by default)
            with Vertical(id="custom-input-container"):
                yield Label("Enter your custom answer:")
                yield Input(placeholder="Type your answer here...", id="custom-input")

            # Buttons
            with Container(id="feedback-buttons"):
                yield Button("Submit", id="submit-button", variant="primary")
                yield Button("Cancel", id="cancel-button")

    def on_mount(self) -> None:
        """Select first option by default."""
        radioset = self.query_one("#option-radioset", RadioSet)
        if self.options_list:
            radioset.pressed_button = self.query_one(f"#option-0", RadioButton)

    @on(RadioSet.Changed)
    def radio_changed(self, event: RadioSet.Changed) -> None:
        """Handle radio button changes."""
        custom_container = self.query_one("#custom-input-container")

        if event.radio_set.pressed_button and event.radio_set.pressed_button.id == "option-custom":
            custom_container.add_class("visible")
            self.query_one("#custom-input", Input).focus()
        else:
            custom_container.remove_class("visible")

    @on(Button.Pressed, "#submit-button")
    def submit(self) -> None:
        """Submit the selected option."""
        radioset = self.query_one("#option-radioset", RadioSet)
        pressed = radioset.pressed_button

        if not pressed:
            return

        if pressed.id == "option-custom":
            # Get custom input
            custom_input = self.query_one("#custom-input", Input).value.strip()
            self.result = custom_input if custom_input else None
        else:
            # Get selected option
            option_index = int(pressed.id.split("-")[1])
            self.result = self.options_list[option_index]

        if self.result:
            self.dismiss(self.result)

    @on(Button.Pressed, "#cancel-button")
    def cancel(self) -> None:
        """Cancel the feedback request."""
        self.dismiss(None)

    def on_key(self, event) -> None:
        """Handle key events."""
        if event.key == "escape":
            self.cancel()
