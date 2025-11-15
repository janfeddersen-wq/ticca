"""
Right sidebar component with status information.
"""

from datetime import datetime

from rich.text import Text
from textual import on
from textual.app import ComposeResult
from textual.containers import Container, Vertical
from textual.reactive import reactive
from textual.widgets import RichLog, RadioSet, RadioButton, Button
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

    class CommitRequested(Message):
        """Commit button was clicked."""
        pass

    class GitPullRequested(Message):
        """Git pull button was clicked."""
        pass

    class GitPushRequested(Message):
        """Git push button was clicked."""
        pass

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

    RightSidebar #git-actions {
        width: 100%;
        height: auto;
        margin-bottom: 1;
        layout: vertical;
    }

    RightSidebar #commit-button,
    RightSidebar #git-pull-button, RightSidebar #git-push-button {
        width: 100%;
        height: 3;
        min-height: 3;
        margin: 0;
        padding: 0 1;
        content-align: center middle;
        border: wide $accent;
        border-bottom: wide $accent-darken-1;
        border-right: wide $accent-darken-1;
        background: $primary;
        color: $background;
        text-style: bold;
    }

    RightSidebar #commit-button:hover,
    RightSidebar #git-pull-button:hover, RightSidebar #git-push-button:hover {
        border: wide $accent-lighten-1;
        border-bottom: wide $accent-darken-1;
        border-right: wide $accent-darken-1;
        background: $primary-lighten-1;
        color: $background;
        text-style: bold;
    }

    RightSidebar #commit-button:focus,
    RightSidebar #git-pull-button:focus, RightSidebar #git-push-button:focus {
        border: wide $accent-darken-1;
        border-top: wide $accent;
        border-left: wide $accent;
        background: $primary-darken-1;
        color: $accent;
        text-style: bold;
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

        # Git action buttons
        with Vertical(id="git-actions"):
            yield Button("Commit", id="commit-button")
            yield Button("Git Pull", id="git-pull-button")
            yield Button("Git Push", id="git-push-button")

        # Status display area
        yield RichLog(id="status-display", wrap=True, highlight=True)

    def on_mount(self) -> None:
        """Initialize the sidebar and start auto-refresh."""
        # Hide agent selector if Easy Mode is enabled
        try:
            from ticca.config import get_easy_mode
            easy_mode = get_easy_mode()
            if easy_mode:
                agent_selector = self.query_one("#agent-selector")
                agent_selector.display = False
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

        # Check if user is at the bottom before updating
        # Only auto-scroll if they're already at the bottom (or within 2 lines of it)
        is_at_bottom = False
        try:
            # Check if scroll position is at or very close to the bottom
            scroll_offset = status_display.scroll_offset
            max_scroll = status_display.max_scroll_y
            # Consider "at bottom" if within 2 lines of the bottom
            is_at_bottom = (max_scroll - scroll_offset.y) <= 2
        except Exception:
            # If we can't determine scroll position, assume we should scroll
            is_at_bottom = True

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

        # Agent Status List (hide in Easy Mode)
        from ticca.config import get_easy_mode
        if not get_easy_mode():
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

        # Clear and write to RichLog
        status_display.clear()
        status_display.write(status_text)

        # Only scroll to bottom if user was already at the bottom
        if is_at_bottom:
            status_display.scroll_end(animate=False)

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

    @on(Button.Pressed, "#commit-button")
    def on_commit_button_pressed(self) -> None:
        """Handle commit button press."""
        self.post_message(self.CommitRequested())

    @on(Button.Pressed, "#git-pull-button")
    def on_git_pull_button_pressed(self) -> None:
        """Handle git pull button press."""
        self.post_message(self.GitPullRequested())

    @on(Button.Pressed, "#git-push-button")
    def on_git_push_button_pressed(self) -> None:
        """Handle git push button press."""
        self.post_message(self.GitPushRequested())
