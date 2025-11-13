"""
Right sidebar component with status information.
"""

from datetime import datetime

from rich.text import Text
from textual import on
from textual.app import ComposeResult
from textual.containers import Container, Vertical
from textual.reactive import reactive
from textual.widgets import RichLog, RadioSet, RadioButton
from textual.message import Message


class RightSidebar(Container):
    """Right sidebar with status information and metrics."""

    class ModelChanged(Message):
        """Model was changed in selector."""
        def __init__(self, model_name: str) -> None:
            self.model_name = model_name
            super().__init__()

    class AgentChanged(Message):
        """Agent was changed in selector."""
        def __init__(self, agent_name: str) -> None:
            self.agent_name = agent_name
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

    RightSidebar #agent-selector {
        width: 100%;
        margin-bottom: 1;
        height: auto;
        background: transparent;
        border: none;
        padding: 0 1;
    }

    RightSidebar RadioButton {
        width: 100%;
        height: auto;
        background: transparent;
        padding: 0;
        margin: 0;
    }

    RightSidebar #status-display {
        width: 100%;
        height: 1fr;
        background: $background;
        border: none;
        scrollbar-size: 1 1;
    }
    """

    # Reactive variables
    context_used = reactive(0)
    context_total = reactive(100000)
    context_percentage = reactive(0.0)
    message_count = reactive(0)
    session_duration = reactive("0m")
    current_model = reactive("Unknown")
    agent_name = reactive("code-agent")

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.id = "right-sidebar"
        self._agent_options = []

    def compose(self) -> ComposeResult:
        """Compose the sidebar layout."""
        # Get available agents
        try:
            from ticca.agents.agent_manager import get_available_agents, get_current_agent_name
            agents = get_available_agents()
            current_agent = get_current_agent_name()

            # Agent selector radio buttons
            with RadioSet(id="agent-selector"):
                for agent_id, agent_display in agents.items():
                    yield RadioButton(agent_display, value=agent_id == current_agent, id=f"agent-{agent_id}")
        except Exception:
            with RadioSet(id="agent-selector"):
                yield RadioButton("Code Agent", value=True, id="agent-code-agent")

        # Status display area
        yield RichLog(id="status-display", wrap=True, highlight=True)

    def on_mount(self) -> None:
        """Initialize the sidebar and start auto-refresh."""
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
        self._update_display()

    def watch_agent_name(self) -> None:
        """Update display when agent changes."""
        self._update_display()

    def watch_session_duration(self) -> None:
        """Update display when session duration changes."""
        self._update_display()

    @on(RadioSet.Changed, "#agent-selector")
    def on_agent_selector_changed(self, event: RadioSet.Changed) -> None:
        """Handle agent selection change."""
        if event.pressed and event.pressed.id:
            # Extract agent ID from button ID (format: "agent-{agent_id}")
            agent_id = event.pressed.id.replace("agent-", "")
            # Update our agent_name reactive variable
            self.agent_name = agent_id
            # Notify parent app of the change
            self.post_message(self.AgentChanged(agent_id))

    def _update_display(self) -> None:
        """Update the entire sidebar display with Rich Text."""
        try:
            status_display = self.query_one("#status-display", RichLog)
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
            from ticca.agents.agent_manager import get_current_agent, _AGENT_HISTORIES
            agents = get_available_agents()

            # Get the current agent to access its live message history
            try:
                current_agent = get_current_agent()
                current_agent_id = current_agent.name
            except Exception:
                current_agent = None
                current_agent_id = None

            for agent_id, agent_display in agents.items():
                # Show agent with idle status and message count
                # Use a simple indicator: ○ for idle agents, ● for active
                indicator = "●" if agent_id.lower() in self.agent_name.lower() else "○"
                status_text.append(f"  {indicator} ", style="dim")

                # Remove the word "Agent" from display name
                display_clean = agent_display.replace(" Agent", "").replace(" agent", "")
                status_text.append(f"{display_clean}: ", style="white")
                status_text.append("idle ", style="dim")

                # Get message count for this specific agent
                try:
                    # If this is the current agent, get its live history
                    if current_agent and agent_id == current_agent_id:
                        agent_msg_count = len(current_agent.get_message_history())
                    # Otherwise, get from stored history
                    elif agent_id in _AGENT_HISTORIES:
                        agent_msg_count = len(_AGENT_HISTORIES[agent_id])
                    else:
                        agent_msg_count = 0
                except Exception:
                    agent_msg_count = 0

                status_text.append(f"({agent_msg_count} msg)\n", style="dim")
        except Exception:
            # Fallback if agent discovery fails
            display_clean = self.agent_name.replace("-agent", "").title()
            status_text.append(f"  ● {display_clean}: idle ({self.message_count} msg)\n", style="white")

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

        # Clear and write to RichLog
        status_display.clear()
        status_display.write(status_text)

    def update_context(self, used: int, total: int) -> None:
        """Update context usage values.

        Args:
            used: Number of tokens used
            total: Total token capacity
        """
        self.context_used = used
        self.context_total = total

    def update_session_info(
        self, message_count: int, duration: str, model: str
    ) -> None:
        """Update session information.

        Args:
            message_count: Number of messages in session
            duration: Session duration as formatted string
            model: Current model name
        """
        self.message_count = message_count
        self.session_duration = duration
        self.current_model = model
