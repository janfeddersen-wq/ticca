"""
Right sidebar component with status information.
"""

from datetime import datetime

from rich.text import Text
from textual import on
from textual.app import ComposeResult
from textual.containers import Container, Vertical
from textual.reactive import reactive
from textual.widgets import Static, Select
from textual.message import Message


class RightSidebar(Container):
    """Right sidebar with status information and metrics."""

    class ModelChanged(Message):
        """Model was changed in selector."""
        def __init__(self, model_name: str) -> None:
            self.model_name = model_name
            super().__init__()

    DEFAULT_CSS = """
    RightSidebar {
        dock: right;
        width: 30;
        min-width: 25;
        max-width: 45;
        background: $background;
        border-left: solid $panel;
        padding: 1;
        layout: vertical;
    }

    RightSidebar #model-selector {
        width: 100%;
        margin-bottom: 1;
        height: auto;
        min-height: 1;
        border: none !important;
        background: #3b4252;
        color: #eceff4;
        padding: 0 !important;
    }

    RightSidebar #model-selector:focus {
        border: none !important;
        background: #434c5e;
    }

    RightSidebar #model-selector:hover {
        border: none !important;
        background: #434c5e;
    }

    RightSidebar #model-selector > * {
        border: none !important;
        padding: 0 !important;
    }

    RightSidebar #status-display {
        width: 100%;
        height: 1fr;
    }
    """

    # Reactive variables
    context_used = reactive(0)
    context_total = reactive(100000)
    context_percentage = reactive(0.0)
    message_count = reactive(0)
    session_duration = reactive("0m")
    current_model = reactive("Unknown")
    agent_name = reactive("code-puppy")

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.id = "right-sidebar"
        self._model_options = []

    def compose(self) -> ComposeResult:
        """Compose the sidebar layout."""
        # Get available models
        try:
            from ticca.model_factory import get_available_models
            models = get_available_models()
            self._model_options = [(name, name) for name in models]
        except Exception:
            self._model_options = [("default", "default")]

        # Model selector dropdown
        yield Select(
            options=self._model_options,
            prompt="Select Model",
            id="model-selector",
            allow_blank=False
        )

        # Status display area
        yield Static("", id="status-display")

    def on_mount(self) -> None:
        """Initialize the sidebar and start auto-refresh."""
        # Set initial model value
        try:
            model_select = self.query_one("#model-selector", Select)
            if self.current_model and self.current_model != "Unknown":
                model_select.value = self.current_model
        except Exception:
            pass

        self._update_display()
        # Auto-refresh every second for live updates
        self.set_interval(1.0, self._update_display)

    def watch_context_used(self) -> None:
        """Update display when context usage changes."""
        self._update_display()

    def watch_context_total(self) -> None:
        """Update display when context total changes."""
        self._update_display()

    def watch_message_count(self) -> None:
        """Update display when message count changes."""
        self._update_display()

    def watch_current_model(self) -> None:
        """Update display when model changes."""
        # Update the Select widget value if model changed externally
        try:
            model_select = self.query_one("#model-selector", Select)
            if self.current_model and self.current_model != model_select.value:
                model_select.value = self.current_model
        except Exception:
            pass
        self._update_display()

    def watch_agent_name(self) -> None:
        """Update display when agent changes."""
        self._update_display()

    def watch_session_duration(self) -> None:
        """Update display when session duration changes."""
        self._update_display()

    @on(Select.Changed, "#model-selector")
    def on_model_selector_changed(self, event: Select.Changed) -> None:
        """Handle model selection change."""
        if event.value and event.value != Select.BLANK:
            # Update our current_model reactive variable
            self.current_model = event.value
            # Notify parent app of the change
            self.post_message(self.ModelChanged(event.value))

    def _update_display(self) -> None:
        """Update the entire sidebar display with Rich Text."""
        try:
            status_display = self.query_one("#status-display", Static)
        except Exception:
            # Widget not ready yet
            return

        status_text = Text()

        # Active Agent Section (like ticca_old)
        status_text.append("Active Agent:\n", style="bold")
        status_text.append(f"  {self.agent_name}\n\n", style="cyan")

        # LLM Model Section
        status_text.append("LLM Model:\n", style="bold")
        # Truncate model name if too long
        model_display = self.current_model
        if len(model_display) > 28:
            model_display = model_display[:25] + "..."
        status_text.append(f"  {model_display}\n\n", style="cyan")

        # Agent Status List (like ticca_old)
        status_text.append("Agents:\n", style="bold")

        # Try to get available agents and their status
        try:
            from ticca.agents import get_available_agents
            agents = get_available_agents()

            for agent_id, agent_display in agents.items():
                # Show agent with idle status and message count
                # Use a simple indicator: ○ for idle agents, ● for active
                indicator = "●" if agent_id.lower() in self.agent_name.lower() else "○"
                status_text.append(f"  {indicator} ", style="dim")
                status_text.append(f"{agent_display}: ", style="white")
                status_text.append("idle ", style="dim")
                # Show message count if available
                status_text.append(f"({self.message_count} msg)\n", style="dim")
        except Exception:
            # Fallback if agent discovery fails
            status_text.append(f"  ● {self.agent_name}: idle ({self.message_count} msg)\n", style="white")

        # Context Window Section (compact)
        status_text.append("\n")
        status_text.append("Context:\n", style="bold")

        # Calculate percentage
        if self.context_total > 0:
            percentage = (self.context_used / self.context_total) * 100
        else:
            percentage = 0

        # Show stats in k format (more compact)
        tokens_k = self.context_used / 1000
        max_k = self.context_total / 1000

        # Choose color based on usage
        if percentage < 50:
            stat_color = "green"
        elif percentage < 75:
            stat_color = "yellow"
        else:
            stat_color = "red"

        status_text.append(f"  {tokens_k:.1f}k/{max_k:.0f}k ", style=stat_color)
        status_text.append(f"({percentage:.0f}%)\n", style="dim")

        status_display.update(status_text)

    def update_context(self, used: int, total: int) -> None:
        """Update context usage values.

        Args:
            used: Number of tokens used
            total: Total token capacity
        """
        self.context_used = used
        self.context_total = total

    def update_session_info(
        self, message_count: int, duration: str, model: str, agent: str
    ) -> None:
        """Update session information.

        Args:
            message_count: Number of messages in session
            duration: Session duration as formatted string
            model: Current model name
            agent: Current agent name
        """
        self.message_count = message_count
        self.session_duration = duration
        self.current_model = model
        self.agent_name = agent
