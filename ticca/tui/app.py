"""
Main TUI application class.
"""

from datetime import datetime, timezone

from textual import on
from textual.app import App, ComposeResult
from textual.binding import Binding
from textual.containers import Container
from textual.events import Resize
from textual.reactive import reactive
from textual.widgets import Footer, ListView

# message_history_accumulator and prune_interrupted_tool_calls have been moved to BaseAgent class
from ticca.agents.agent_manager import get_current_agent
from ticca.command_line.command_handler import handle_command
from ticca.command_line.model_picker_completion import set_active_model
from ticca.config import (
    get_global_model_name,
    initialize_command_history_file,
    save_command_to_history,
)
# Import our message queue system
from ticca.messaging import TUIRenderer, get_global_queue
from ticca.tui.components import (
    ChatView,
    CustomTextArea,
    FileTreePanel,
    InputArea,
    RightSidebar,
    Sidebar,
    StatusBar,
)

# Import shared message classes
from .messages import CommandSelected, HistoryEntrySelected
from .models import ChatMessage, MessageType
from .screens import (
    HelpScreen,
    MCPInstallWizardScreen,
    ModelPicker,
    QuitConfirmationScreen,
    SettingsScreen,
    UISettingsScreen,
    ModelSettingsScreen,
)


class CodePuppyTUI(App):
    """Main Ticca TUI application."""

    TITLE = "Ticca - Terminal Injected Coding CLI Assistant"
    SUB_TITLE = "TUI Mode"

    # Base CSS structure - no theme CSS needed, Textual handles it!
    CSS = """
    Screen {
        layout: horizontal;
        background: $background;
    }

    /* Make modal screens have semi-transparent scrim to dim background */
    ModalScreen {
        background: rgba(0, 0, 0, 0.6);
    }

    /* Global scrollbar styling - slim and subtle */
    * {
        scrollbar-background: transparent;
        scrollbar-color: $primary;
        scrollbar-color-hover: $primary-lighten-1;
        scrollbar-color-active: $accent;
        scrollbar-size: 1 1;
    }

    #main-area {
        layout: vertical;
        width: 1fr;
        min-width: 40;
        background: $background;
    }

    #chat-container {
        height: 1fr;
        min-height: 10;
        background: $background;
    }

    /* Clean TICCA design - full height sidebars */
    FileTreePanel {
        height: 100%;
    }

    Sidebar {
        background: $background;
        border-right: solid $panel;
        width: 30;
        padding: 1;
        height: 100%;
    }

    RightSidebar {
        height: 100%;
    }

    /* Status bar at top - dark background for better readability */
    StatusBar {
        height: 1;
        background: $background;
        color: $text;
        padding: 0 1;
        dock: top;
        text-style: bold;
    }

    /* Compact input area */
    InputArea {
        height: auto;
        background: $background;
        border-top: solid $panel;
        padding: 1 1 1 0;
    }

    /* Transparent input field - only for the main input area */
    #input-field {
        background: transparent !important;
        border: none !important;
    }

    #input-field:focus {
        background: transparent !important;
        border: none !important;
    }

    /* Compact message styling */
    .message-user {
        color: $success;
        text-style: bold;
        margin: 0 0 1 0;
    }

    .message-agent {
        color: $text;
        margin: 0 0 1 0;
    }

    .message-error {
        color: $error;
        text-style: bold;
        margin: 0 0 1 0;
    }

    .message-system {
        color: $warning;
        text-style: italic;
        margin: 0 0 1 0;
    }

    /* Compact chat view */
    ChatView {
        padding: 1 1 1 0;
        background: $background;
    }

    /* Footer (bottom keybinding bar) - dark background for better readability */
    Footer {
        height: 1;
        background: $background;
        color: $text;
        dock: bottom;
    }
    """

    BINDINGS = [
        Binding("ctrl+q", "quit", "Quit"),
        Binding("ctrl+c", "copy_selection", "Copy", show=False),
        Binding("ctrl+l", "clear_chat", "Clear Chat"),
        Binding("ctrl+1", "clear_chat", "Clear Chat", show=False),  # Hidden from footer
        Binding("ctrl+2", "toggle_sidebar", "History"),
        Binding("ctrl+3", "open_ui_settings", "UI Settings"),
        Binding("ctrl+4", "toggle_file_tree", "Files"),
        Binding("ctrl+5", "focus_input", "Focus Prompt"),
        Binding("ctrl+6", "focus_chat", "Focus Response"),
        Binding("ctrl+7", "toggle_right_sidebar", "Status"),
        Binding("ctrl+m", "open_model_settings", "Model Settings"),
        Binding("ctrl+t", "open_mcp_wizard", "MCP Install Wizard"),
        Binding("ctrl+r", "open_resume_dialog", "Resume"),
        Binding("ctrl+backslash", "command_palette", "Command Palette"),
    ]

    # Reactive variables for app state
    current_model = reactive("")
    current_agent = reactive("")
    agent_busy = reactive(False)

    def watch_agent_busy(self) -> None:
        """Watch for changes to agent_busy state."""
        # Update the submit/cancel button state when agent_busy changes
        self._update_submit_cancel_button(self.agent_busy)

    def watch_current_agent(self) -> None:
        """Watch for changes to current_agent and update title."""
        self._update_title()

    def _update_title(self) -> None:
        """Update the application title to include current agent."""
        if self.current_agent:
            self.title = f"Ticca - {self.current_agent}"
            self.sub_title = "Terminal Injected Coding CLI Assistant"
        else:
            self.title = "Ticca - Terminal Injected Coding CLI Assistant"
            self.sub_title = "TUI Mode"

    def _on_agent_reload(self, agent_id: str, agent_name: str) -> None:
        """Callback for when agent is reloaded/changed."""
        # Get the updated agent configuration
        from ticca.agents.agent_manager import get_current_agent

        current_agent_config = get_current_agent()
        new_agent_display = (
            current_agent_config.display_name if current_agent_config else "code-agent"
        )

        # Update the reactive variable (this will trigger watch_current_agent)
        self.current_agent = new_agent_display

        # Update to show the effective model (respects pinned model)
        self.current_model = current_agent_config.get_model_name()

        # Update status bar
        status_bar = self.query_one(StatusBar)
        status_bar.current_model = self.current_model

        # Don't show duplicate message - the UI handler already shows success message

    def __init__(self, initial_command: str = None, **kwargs):
        super().__init__(**kwargs)
        self._current_worker = None
        self.initial_command = initial_command

        # Initialize message queue renderer
        self.message_queue = get_global_queue()
        self.message_renderer = TUIRenderer(self.message_queue, self)
        self._renderer_started = False

        # Track session start time
        from datetime import datetime

        self._session_start_time = datetime.now()

        # Background worker for periodic context updates during agent execution
        self._context_update_worker = None

        # Track double-click timing for history list
        self._last_history_click_time = None
        self._last_history_click_index = None

    def _register_themes(self) -> None:
        """Register only the active theme to avoid expensive startup style recalculations.

        Other themes are registered lazily when the user switches to them.
        """
        from ticca.themes import ThemeManager
        from ticca.themes.css_generator import create_textual_theme
        from ticca.config import get_value

        # Initialize theme manager
        ThemeManager.initialize()

        # Get the current theme from config
        try:
            current_theme_name = get_value("tui_theme") or "nord"
        except Exception:
            current_theme_name = "nord"

        # OPTIMIZATION: Only register the active theme at startup
        # This avoids triggering style recalculations for all themes
        # Other themes will be registered on-demand when user switches
        theme_obj = ThemeManager.get_theme(current_theme_name)
        if theme_obj:
            textual_theme = create_textual_theme(theme_obj)
            self.register_theme(textual_theme)
            self.theme = current_theme_name

    def compose(self) -> ComposeResult:
        """Create the UI layout."""
        yield StatusBar()
        yield FileTreePanel(".")  # File tree on the left
        yield Sidebar()  # History sidebar (hidden by default)
        with Container(id="main-area"):
            with Container(id="chat-container"):
                yield ChatView(id="chat-view")
            yield InputArea()
        yield RightSidebar()
        yield Footer()

    def on_mount(self) -> None:
        """Initialize the application when mounted."""
        # Register this app instance for global access
        from ticca.tui_state import set_tui_app_instance

        set_tui_app_instance(self)

        # Register all custom themes
        self._register_themes()

        # Register callback for agent reload events
        from ticca.callbacks import register_callback

        register_callback("agent_reload", self._on_agent_reload)

        # Load configuration
        # Get current agent information
        from ticca.agents.agent_manager import get_current_agent, set_current_agent
        from ticca.config import get_easy_mode, clear_agent_pinned_model

        # If Easy Mode is enabled, force code-agent and ensure it uses default model
        if get_easy_mode():
            # Clear any pinned model for code-agent to ensure it uses default model
            clear_agent_pinned_model("code-agent")
            # Force code-agent as the current agent
            set_current_agent("code-agent")

        current_agent_config = get_current_agent()
        self.current_agent = (
            current_agent_config.display_name if current_agent_config else "code-agent"
        )

        # Get effective model (respects agent pinned model)
        self.current_model = current_agent_config.get_model_name()

        # Initial title update
        self._update_title()

        # Use runtime manager to ensure we always have the current agent
        # Update status bar
        status_bar = self.query_one(StatusBar)
        status_bar.current_model = self.current_model
        status_bar.agent_status = "Ready"

        # Add welcome message with YOLO mode status
        from ticca.config import get_yolo_mode
        yolo_enabled = get_yolo_mode()

        if yolo_enabled:
            welcome_text = (
                "Welcome to Ticca ⚡\n\n"
                "💨 YOLO mode: ON\n"
                "Commands execute without confirmation"
            )
        else:
            welcome_text = (
                "Welcome to Ticca ⚡\n\n"
                "⚠️  YOLO mode: OFF\n"
                "Commands will prompt for confirmation"
            )
        self.add_system_message(welcome_text)

        # Start the message renderer EARLY to catch startup messages
        # Using call_after_refresh to start it as soon as possible after mount
        self.call_after_refresh(self.start_message_renderer_sync)

        # DEFER agent preload until TUI is fully visible to avoid blocking initial render
        # Use a short timer (0.3s) so user sees the UI immediately, THEN we load the model
        def deferred_preload():
            self.run_worker(self.preload_agent_on_startup(), exclusive=False)
        self.set_timer(0.3, deferred_preload)

        # DO NOT auto-prompt for autosave on startup - user can use /resume or Ctrl+R
        # self.call_after_refresh(self.maybe_prompt_restore_autosave)

        # Apply responsive design adjustments
        self.apply_responsive_layout()

        # Auto-focus the input field so user can start typing immediately
        self.call_after_refresh(self.focus_input_field)

        # Process initial command if provided
        if self.initial_command:
            self.call_after_refresh(self.process_initial_command)

        # Initialize right sidebar (hidden by default)
        try:
            right_sidebar = self.query_one(RightSidebar)
            right_sidebar.display = True  # Show by default for sexy UI
            self._update_right_sidebar()
        except Exception:
            pass

        # Apply file tree visibility setting from config
        try:
            from ticca.config import get_show_file_tree
            file_tree = self.query_one(FileTreePanel)
            file_tree.display = get_show_file_tree()
        except Exception:
            pass

    def _tighten_text(self, text: str) -> str:
        """Aggressively tighten whitespace: trim lines, collapse multiples, drop extra blanks."""
        try:
            import re

            # Split into lines, strip each, drop empty runs
            lines = [re.sub(r"\s+", " ", ln.strip()) for ln in text.splitlines()]
            # Remove consecutive blank lines
            tight_lines = []
            last_blank = False
            for ln in lines:
                is_blank = ln == ""
                if is_blank and last_blank:
                    continue
                tight_lines.append(ln)
                last_blank = is_blank
            return "\n".join(tight_lines).strip()
        except Exception:
            return text.strip()

    def add_system_message(
        self, content: str, message_group: str = None, group_id: str = None
    ) -> None:
        """Add a system message to the chat."""
        # Support both parameter names for backward compatibility
        final_group_id = message_group or group_id
        # Tighten only plain strings
        content_to_use = (
            self._tighten_text(content) if isinstance(content, str) else content
        )
        message = ChatMessage(
            id=f"sys_{datetime.now(timezone.utc).timestamp()}",
            type=MessageType.SYSTEM,
            content=content_to_use,
            timestamp=datetime.now(timezone.utc),
            group_id=final_group_id,
        )
        chat_view = self.query_one("#chat-view", ChatView)
        chat_view.add_message(message)

    def add_system_message_rich(
        self, rich_content, message_group: str = None, group_id: str = None
    ) -> None:
        """Add a system message with Rich content (like Markdown) to the chat."""
        # Support both parameter names for backward compatibility
        final_group_id = message_group or group_id
        message = ChatMessage(
            id=f"sys_rich_{datetime.now(timezone.utc).timestamp()}",
            type=MessageType.SYSTEM,
            content=rich_content,  # Store the Rich object directly
            timestamp=datetime.now(timezone.utc),
            group_id=final_group_id,
        )
        chat_view = self.query_one("#chat-view", ChatView)
        chat_view.add_message(message)

    def add_user_message(self, content: str, message_group: str = None) -> None:
        """Add a user message to the chat."""
        message = ChatMessage(
            id=f"user_{datetime.now(timezone.utc).timestamp()}",
            type=MessageType.USER,
            content=content,
            timestamp=datetime.now(timezone.utc),
            group_id=message_group,
        )
        chat_view = self.query_one("#chat-view", ChatView)
        chat_view.add_message(message)

    def add_agent_message(self, content: str, message_group: str = None) -> None:
        """Add an agent message to the chat."""
        message = ChatMessage(
            id=f"agent_{datetime.now(timezone.utc).timestamp()}",
            type=MessageType.AGENT_RESPONSE,
            content=content,
            timestamp=datetime.now(timezone.utc),
            group_id=message_group,
        )
        chat_view = self.query_one("#chat-view", ChatView)
        chat_view.add_message(message)

    def add_error_message(self, content: str, message_group: str = None) -> None:
        """Add an error message to the chat."""
        content_to_use = (
            self._tighten_text(content) if isinstance(content, str) else content
        )
        message = ChatMessage(
            id=f"error_{datetime.now(timezone.utc).timestamp()}",
            type=MessageType.ERROR,
            content=content_to_use,
            timestamp=datetime.now(timezone.utc),
            group_id=message_group,
        )
        chat_view = self.query_one("#chat-view", ChatView)
        chat_view.add_message(message)

    def add_agent_reasoning_message(
        self, content, message_group: str = None
    ) -> None:
        """Add an agent reasoning message to the chat.

        Args:
            content: Message content - can be a string or Rich object (like Markdown)
            message_group: Optional group ID for grouping related messages
        """
        message = ChatMessage(
            id=f"agent_reasoning_{datetime.now(timezone.utc).timestamp()}",
            type=MessageType.AGENT_REASONING,
            content=content,
            timestamp=datetime.now(timezone.utc),
            group_id=message_group,
        )
        chat_view = self.query_one("#chat-view", ChatView)
        chat_view.add_message(message)

    def add_planned_next_steps_message(
        self, content, message_group: str = None
    ) -> None:
        """Add a planned next steps message to the chat.

        Args:
            content: Message content - can be a string or Rich object (like Markdown)
            message_group: Optional group ID for grouping related messages
        """
        message = ChatMessage(
            id=f"planned_next_steps_{datetime.now(timezone.utc).timestamp()}",
            type=MessageType.PLANNED_NEXT_STEPS,
            content=content,
            timestamp=datetime.now(timezone.utc),
            group_id=message_group,
        )
        chat_view = self.query_one("#chat-view", ChatView)
        chat_view.add_message(message)

    def on_custom_text_area_message_sent(
        self, event: CustomTextArea.MessageSent
    ) -> None:
        """Handle message sent from custom text area."""
        self.action_send_message()

    def on_input_area_submit_requested(self, event) -> None:
        """Handle submit button clicked."""
        self.action_send_message()

    def on_input_area_cancel_requested(self, event) -> None:
        """Handle cancel button clicked."""
        self.action_cancel_processing()

    def on_file_tree_panel_file_double_clicked(self, event) -> None:
        """Handle file double-click in the file tree - open editor modal."""
        try:
            from pathlib import Path

            file_path = Path(event.path)

            # Check if file exists and is a file
            if not file_path.is_file():
                self.add_error_message(f"Not a file: {file_path}")
                return

            # Check file size (500KB limit for editor)
            file_size = file_path.stat().st_size
            max_size = 500 * 1024  # 500KB in bytes

            if file_size > max_size:
                size_mb = file_size / (1024 * 1024)
                self.add_error_message(
                    f"File too large to open in editor: {size_mb:.2f} MB\n"
                    f"Maximum size: 500 KB"
                )
                return

            # Check if it's an image file
            image_extensions = {'.png', '.jpg', '.jpeg', '.gif', '.bmp', '.webp', '.svg', '.ico'}
            if file_path.suffix.lower() in image_extensions:
                # Open image viewer instead
                from .components.image_viewer_modal import ImageViewerModal
                self.push_screen(ImageViewerModal(file_path))
            else:
                # Open text editor
                from .components.file_editor_modal import FileEditorModal
                self.push_screen(FileEditorModal(file_path))

        except Exception as e:
            self.add_error_message(f"Failed to open file: {e}")

    async def on_key(self, event) -> None:
        """Handle app-level key events."""
        input_field = self.query_one("#input-field", CustomTextArea)

        # Only handle keys when input field is focused
        if input_field.has_focus:
            # Handle Ctrl+Enter or Shift+Enter for a new line
            if event.key in ("ctrl+enter", "shift+enter"):
                input_field.insert("\n")
                event.prevent_default()
                return

        # Check if a modal is currently active - if so, let the modal handle keys
        if hasattr(self, "_active_screen") and self._active_screen:
            # Don't handle keys at the app level when a modal is active
            return

        # Handle arrow keys for sidebar navigation when sidebar is visible
        if not input_field.has_focus:
            try:
                sidebar = self.query_one(Sidebar)
                if sidebar.display:
                    # Handle navigation for the currently active tab
                    tabs = self.query_one("#sidebar-tabs")
                    active_tab = tabs.active

                    if active_tab == "history-tab":
                        history_list = self.query_one("#history-list", ListView)
                        if event.key == "enter":
                            if history_list.highlighted_child and hasattr(
                                history_list.highlighted_child, "command_entry"
                            ):
                                # Show command history modal
                                from .components.command_history_modal import (
                                    CommandHistoryModal,
                                )

                                # Make sure sidebar's current_history_index is synced with the ListView
                                sidebar.current_history_index = history_list.index

                                # Push the modal screen
                                # The modal will get the command entries from the sidebar
                                self.push_screen(CommandHistoryModal())
                            event.prevent_default()
                            return
            except Exception:
                pass

    def refresh_history_display(self) -> None:
        """Refresh the history display with the command history file."""
        try:
            sidebar = self.query_one(Sidebar)
            sidebar.load_command_history()
        except Exception:
            pass  # Silently fail if history list not available

    def action_send_message(self) -> None:
        """Send the current message."""
        input_field = self.query_one("#input-field", CustomTextArea)
        message = input_field.text.strip()

        if message:
            # Clear input
            input_field.text = ""

            # Add user message to chat
            self.add_user_message(message)

            # Save command to history file with timestamp
            try:
                save_command_to_history(message)
            except Exception as e:
                self.add_error_message(f"Failed to save command history: {str(e)}")

            # Update button state
            self._update_submit_cancel_button(True)

            # Process the message asynchronously using Textual's worker system
            # Using exclusive=False to avoid TaskGroup conflicts with MCP servers
            self._current_worker = self.run_worker(
                self.process_message(message), exclusive=False
            )

    def _update_submit_cancel_button(self, is_cancel_mode: bool) -> None:
        """Update the submit/cancel button state."""
        try:
            from .components.input_area import SubmitCancelButton

            button = self.query_one(SubmitCancelButton)
            button.is_cancel_mode = is_cancel_mode
        except Exception:
            pass  # Silently fail if button not found

    def action_cancel_processing(self) -> None:
        """Cancel the current message processing."""
        if hasattr(self, "_current_worker") and self._current_worker is not None:
            try:
                # First, kill any running shell processes (same as interactive mode Ctrl+C)
                from ticca.tools.command_runner import (
                    kill_all_running_shell_processes,
                )

                killed = kill_all_running_shell_processes()
                if killed:
                    self.add_system_message(
                        f"🔥 Cancelled {killed} running shell process(es)"
                    )
                    # Don't stop spinner/agent - let the agent continue processing
                    # Shell processes killed, but agent worker continues running

                else:
                    # Only cancel the agent task if NO processes were killed
                    self._current_worker.cancel()
                    self.add_system_message("⚠️  Processing cancelled by user")
                    # Stop spinner and clear state only when agent is actually cancelled
                    self._current_worker = None
                    self.agent_busy = False
                    self.stop_agent_progress()
                    # Stop periodic context updates
                    self._stop_context_updates()
            except Exception as e:
                self.add_error_message(f"Failed to cancel processing: {str(e)}")
                # Only clear state on exception if we haven't already done so
                if (
                    hasattr(self, "_current_worker")
                    and self._current_worker is not None
                ):
                    self._current_worker = None
                    self.agent_busy = False
                    self.stop_agent_progress()
                    # Stop periodic context updates
                    self._stop_context_updates()

    async def process_message(self, message: str) -> None:
        """Process a user message asynchronously."""
        try:
            self.agent_busy = True
            self._update_submit_cancel_button(True)
            self.start_agent_progress("Thinking")

            # Start periodic context updates
            self._start_context_updates()

            # Handle commands
            if message.strip().startswith("/"):
                # Handle special commands directly
                if message.strip().lower() in ("clear", "/clear"):
                    self.action_clear_chat()
                    return

                # Let the command handler process all /agent commands
                # result will be handled by the command handler directly through messaging system
                if message.strip().startswith("/agent"):
                    # The command handler will emit messages directly to our messaging system
                    handle_command(message.strip())
                    # Agent manager will automatically use the latest agent
                    return

                # Handle exit commands
                if message.strip().lower() in ("/exit", "/quit"):
                    self.add_system_message("Goodbye!")
                    # Exit the application
                    self.app.exit()
                    return

                if message.strip().lower() in ("/model", "/m"):
                    self.action_open_model_picker()
                    return

                # Use the existing command handler
                # The command handler directly uses the messaging system, so we don't need to capture stdout
                try:
                    result = handle_command(message.strip())

                    # Handle special command return values
                    if result == "__AUTOSAVE_LOAD__":
                        # Open the autosave picker dialog
                        await self.maybe_prompt_restore_autosave()
                        return
                    elif not result:
                        self.add_system_message(f"Unknown command: {message}")
                except Exception as e:
                    self.add_error_message(f"Error executing command: {str(e)}")
                return

            # Process with agent
            try:
                self.update_agent_progress("Processing", 25)

                # Use agent_manager's run_with_mcp to handle MCP servers properly
                try:
                    agent = get_current_agent()
                    self.update_agent_progress("Processing", 50)
                    result = await agent.run_with_mcp(
                        message,
                    )

                    if not result or not hasattr(result, "output"):
                        self.add_error_message("Invalid response format from agent")
                        return

                    self.update_agent_progress("Processing", 75)
                    agent_response = result.output
                    self.add_agent_message(agent_response)

                    # Auto-save session if enabled (mirror --interactive)
                    from ticca.config import auto_save_session_if_enabled

                    auto_save_session_if_enabled()

                    # Refresh history display to show new interaction
                    self.refresh_history_display()

                    # Update right sidebar with new token counts
                    self._update_right_sidebar()

                except Exception as eg:
                    # Handle TaskGroup and other exceptions
                    # BaseExceptionGroup is only available in Python 3.11+
                    if hasattr(eg, "exceptions"):
                        # Handle TaskGroup exceptions specifically (Python 3.11+)
                        for e in eg.exceptions:
                            self.add_error_message(f"MCP/Agent error: {str(e)}")
                    else:
                        # Handle regular exceptions
                        self.add_error_message(f"MCP/Agent error: {str(eg)}")
                finally:
                    pass
            except Exception as agent_error:
                # Handle any other errors in agent processing
                self.add_error_message(f"Agent processing failed: {str(agent_error)}")

        except Exception as e:
            self.add_error_message(f"Error processing message: {str(e)}")
        finally:
            self.agent_busy = False
            self._update_submit_cancel_button(False)
            self.stop_agent_progress()

            # Stop periodic context updates and do a final update
            self._stop_context_updates()

            # Refocus the input field so the user can immediately continue typing
            self.call_after_refresh(self.focus_input_field)

    # Action methods
    def action_clear_chat(self) -> None:
        """Clear the chat history."""
        chat_view = self.query_one("#chat-view", ChatView)
        chat_view.clear_messages()
        agent = get_current_agent()
        agent.clear_message_history()
        self.add_system_message("Chat history cleared")

    def action_copy_selection(self) -> None:
        """Copy selected text to clipboard."""
        import subprocess
        import sys

        try:
            # Get the currently focused widget
            focused = self.focused
            selected_text = None

            # Try to get selected text from focused widget
            if hasattr(focused, 'selected_text') and focused.selected_text:
                selected_text = focused.selected_text
            elif hasattr(focused, 'selection') and focused.selection:
                # For TextArea widgets with selection
                try:
                    start, end = focused.selection
                    selected_text = focused.text[start.offset:end.offset]
                except Exception:
                    pass

            # If no selection, try to get all text from input field if it's focused
            if not selected_text and isinstance(focused, CustomTextArea):
                selected_text = focused.text

            if not selected_text:
                self.add_system_message("💡 No text selected to copy")
                return

            # Copy to clipboard using platform-appropriate method
            success = False
            error_msg = None

            try:
                if sys.platform == "darwin":  # macOS
                    subprocess.run(
                        ["pbcopy"], input=selected_text, text=True, check=True, capture_output=True
                    )
                    success = True
                elif sys.platform == "win32":  # Windows
                    subprocess.run(
                        ["clip"], input=selected_text, text=True, check=True, capture_output=True
                    )
                    success = True
                else:  # Linux and other Unix-like systems
                    # Try xclip first, then xsel as fallback
                    try:
                        subprocess.run(
                            ["xclip", "-selection", "clipboard"],
                            input=selected_text,
                            text=True,
                            check=True,
                            capture_output=True,
                        )
                        success = True
                    except (subprocess.CalledProcessError, FileNotFoundError):
                        # Fallback to xsel
                        subprocess.run(
                            ["xsel", "--clipboard", "--input"],
                            input=selected_text,
                            text=True,
                            check=True,
                            capture_output=True,
                        )
                        success = True
            except subprocess.CalledProcessError as e:
                error_msg = f"Clipboard command failed: {e}"
            except FileNotFoundError:
                if sys.platform not in ["darwin", "win32"]:
                    error_msg = "Clipboard utilities not found. Please install xclip or xsel."
                else:
                    error_msg = "System clipboard command not found."
            except Exception as e:
                error_msg = f"Unexpected error: {e}"

            if success:
                # Show success message with preview of copied text
                preview = selected_text[:50] + "..." if len(selected_text) > 50 else selected_text
                self.add_system_message(f"📋 Copied to clipboard: {preview}")
            else:
                self.add_error_message(f"Failed to copy to clipboard: {error_msg}")

        except Exception as e:
            self.add_error_message(f"Failed to copy selection: {e}")

    def action_quit(self) -> None:
        """Show quit confirmation dialog before exiting."""

        def handle_quit_confirmation(should_quit: bool) -> None:
            if should_quit:
                self.exit()

        self.push_screen(QuitConfirmationScreen(), handle_quit_confirmation)

    def action_show_help(self) -> None:
        """Show help information in a modal."""
        self.push_screen(HelpScreen())

    def action_toggle_sidebar(self) -> None:
        """Toggle sidebar visibility."""
        sidebar = self.query_one(Sidebar)
        sidebar.display = not sidebar.display

        # If sidebar is now visible, focus the history list to enable keyboard navigation
        if sidebar.display:
            try:
                # Ensure history tab is active
                tabs = self.query_one("#sidebar-tabs")
                tabs.active = "history-tab"

                # Refresh the command history
                sidebar.load_command_history()

                # Focus the history list
                history_list = self.query_one("#history-list", ListView)
                history_list.focus()

                # If the list has items, set the index to the first item
                if len(history_list.children) > 0:
                    # Reset sidebar's internal index tracker to 0
                    sidebar.current_history_index = 0
                    # Set ListView index to match
                    history_list.index = 0

            except Exception as e:
                # Log the exception in debug mode but silently fail for end users
                import logging

                logging.debug(f"Error focusing history item: {str(e)}")
                pass
        else:
            # If sidebar is now hidden, focus the input field for a smooth workflow
            try:
                self.action_focus_input()
            except Exception:
                # Silently fail if there's an issue with focusing
                pass

    def action_focus_input(self) -> None:
        """Focus the input field."""
        input_field = self.query_one("#input-field", CustomTextArea)
        input_field.focus()

    def focus_input_field(self) -> None:
        """Focus the input field (used for auto-focus on startup)."""
        try:
            input_field = self.query_one("#input-field", CustomTextArea)
            input_field.focus()
        except Exception:
            pass  # Silently handle if widget not ready yet

    def action_focus_chat(self) -> None:
        """Focus the chat area."""
        chat_view = self.query_one("#chat-view", ChatView)
        chat_view.focus()

    def action_toggle_right_sidebar(self) -> None:
        """Toggle right sidebar visibility."""
        try:
            right_sidebar = self.query_one(RightSidebar)
            right_sidebar.display = not right_sidebar.display

            # Update context info when showing
            if right_sidebar.display:
                self._update_right_sidebar()
        except Exception:
            pass

    def action_toggle_file_tree(self) -> None:
        """Toggle file tree visibility."""
        try:
            file_tree = self.query_one(FileTreePanel)
            file_tree.display = not file_tree.display
        except Exception:
            pass

    def action_open_ui_settings(self) -> None:
        """Open the UI settings configuration screen."""

        def handle_settings_result(result):
            if result and result.get("success"):
                # Handle theme change if needed
                if result.get("theme_changed"):
                    self.add_system_message("Theme updated successfully")

                # Handle Easy Mode change - reload right sidebar
                if result.get("easy_mode_changed"):
                    try:
                        from ticca.config import get_easy_mode, clear_agent_pinned_model
                        from ticca.agents.agent_manager import set_current_agent

                        easy_mode = get_easy_mode()

                        # Force code-agent when enabling Easy Mode
                        if easy_mode:
                            clear_agent_pinned_model("code-agent")
                            set_current_agent("code-agent")

                            # Reload current agent info
                            from ticca.agents.agent_manager import get_current_agent
                            current_agent_config = get_current_agent()
                            self.current_agent = current_agent_config.display_name
                            self.current_model = current_agent_config.get_model_name()

                            # Update status bar
                            status_bar = self.query_one(StatusBar)
                            status_bar.current_model = self.current_model

                        # Reload right sidebar to show/hide agent selector
                        right_sidebar = self.query_one(RightSidebar)
                        agent_selector = right_sidebar.query_one("#agent-selector")
                        agent_selector.display = not easy_mode

                    except Exception as e:
                        self.add_error_message(f"Failed to update Easy Mode: {e}")

                # Show success message
                self.add_system_message(result.get("message", "UI settings updated"))
            elif (
                result
                and not result.get("success")
                and "cancelled" not in result.get("message", "").lower()
            ):
                # Show error message (but not for cancellation)
                self.add_error_message(result.get("message", "UI settings update failed"))

        self.push_screen(UISettingsScreen(), handle_settings_result)

    def action_open_model_settings(self) -> None:
        """Open the model settings configuration screen."""

        def handle_settings_result(result):
            if result and result.get("success"):
                # Handle model change if needed
                if result.get("model_changed"):
                    try:
                        current_agent = get_current_agent()
                        current_agent.reload_code_generation_agent()
                        # Get the effective model after reload (respects pinned model)
                        self.current_model = current_agent.get_model_name()
                    except Exception as reload_error:
                        self.add_error_message(
                            f"Failed to reload agent after model change: {reload_error}"
                        )

                # Update status bar
                status_bar = self.query_one(StatusBar)
                status_bar.current_model = self.current_model

                # Show success message
                self.add_system_message(result.get("message", "Model settings updated"))
            elif (
                result
                and not result.get("success")
                and "cancelled" not in result.get("message", "").lower()
            ):
                # Show error message (but not for cancellation)
                self.add_error_message(result.get("message", "Model settings update failed"))

        self.push_screen(ModelSettingsScreen(), handle_settings_result)

    def action_open_settings(self) -> None:
        """Open the settings configuration screen (legacy - redirects to model settings)."""
        # Keep for backward compatibility - redirect to model settings
        self.action_open_model_settings()

    def action_open_mcp_wizard(self) -> None:
        """Open the MCP Install Wizard."""

        def handle_wizard_result(result):
            if result and result.get("success"):
                # Show success message
                self.add_system_message(
                    result.get("message", "MCP server installed successfully")
                )

                # If a server was installed, suggest starting it
                if result.get("server_name"):
                    server_name = result["server_name"]
                    self.add_system_message(
                        f"💡 Use '/mcp start {server_name}' to start the server"
                    )
            elif (
                result
                and not result.get("success")
                and "cancelled" not in result.get("message", "").lower()
            ):
                # Show error message (but not for cancellation)
                self.add_error_message(result.get("message", "MCP installation failed"))

        self.push_screen(MCPInstallWizardScreen(), handle_wizard_result)

    def action_open_model_picker(self) -> None:
        """Open the model picker modal."""

        def handle_model_select(model_name: str | None):
            if model_name:
                try:
                    set_active_model(model_name)
                    # Reload agent with new model
                    agent = get_current_agent()
                    agent.reload_code_generation_agent()
                    # Get the effective model (respects pinned model)
                    self.current_model = agent.get_model_name()
                    status_bar = self.query_one(StatusBar)
                    status_bar.current_model = self.current_model
                    self.add_system_message(f"✅ Model switched to: {model_name}")
                except Exception as e:
                    self.add_error_message(f"Failed to switch model: {e}")

        self.push_screen(ModelPicker(), handle_model_select)

    def action_open_resume_dialog(self) -> None:
        """Open the resume/autosave picker dialog."""
        # Call the same method used at startup, but now manually triggered
        self.run_worker(self.maybe_prompt_restore_autosave(), exclusive=False)

    def process_initial_command(self) -> None:
        """Process the initial command provided when starting the TUI."""
        if self.initial_command:
            # Add the initial command to the input field
            input_field = self.query_one("#input-field", CustomTextArea)
            input_field.text = self.initial_command

            # Show that we're auto-executing the initial command
            self.add_system_message(
                f"🚀 Auto-executing initial command: {self.initial_command}"
            )

            # Automatically submit the message
            self.action_send_message()

    def show_history_details(self, history_entry: dict) -> None:
        """Show detailed information about a selected history entry."""
        try:
            timestamp = history_entry.get("timestamp", "Unknown time")
            description = history_entry.get("description", "No description")
            output = history_entry.get("output", "")
            awaiting_input = history_entry.get("awaiting_user_input", False)

            # Parse timestamp for better display with safe parsing
            def parse_timestamp_safely_for_details(timestamp_str: str) -> str:
                """Parse timestamp string safely for detailed display."""
                try:
                    # Handle 'Z' suffix (common UTC format)
                    cleaned_timestamp = timestamp_str.replace("Z", "+00:00")
                    parsed_dt = datetime.fromisoformat(cleaned_timestamp)

                    # If the datetime is naive (no timezone), assume UTC
                    if parsed_dt.tzinfo is None:
                        parsed_dt = parsed_dt.replace(tzinfo=timezone.utc)

                    return parsed_dt.strftime("%Y-%m-%d %H:%M:%S")
                except (ValueError, AttributeError, TypeError):
                    # Handle invalid timestamp formats gracefully
                    return timestamp_str

            formatted_time = parse_timestamp_safely_for_details(timestamp)

            # Create detailed view content
            details = [
                f"Timestamp: {formatted_time}",
                f"Description: {description}",
                "",
            ]

            if output:
                details.extend(
                    [
                        "Output:",
                        "─" * 40,
                        output,
                        "",
                    ]
                )

            if awaiting_input:
                details.append("⚠️  Was awaiting user input")

            # Display details as a system message in the chat
            detail_text = "\\n".join(details)
            self.add_system_message(f"History Details:\\n{detail_text}")

        except Exception as e:
            self.add_error_message(f"Failed to show history details: {e}")

    # Progress and status methods
    def set_agent_status(self, status: str, show_progress: bool = False) -> None:
        """Update agent status and optionally show/hide progress bar."""
        try:
            # Update status bar
            status_bar = self.query_one(StatusBar)
            status_bar.agent_status = status

            # Update spinner visibility
            from .components.input_area import SimpleSpinnerWidget

            spinner = self.query_one("#spinner", SimpleSpinnerWidget)
            if show_progress:
                spinner.add_class("visible")
                spinner.start_spinning()
            else:
                spinner.remove_class("visible")
                spinner.stop_spinning()

        except Exception:
            pass  # Silently fail if widgets not available

    def start_agent_progress(self, initial_status: str = "Thinking") -> None:
        """Start showing agent progress indicators."""
        self.set_agent_status(initial_status, show_progress=True)

    def update_agent_progress(self, status: str, progress: int = None) -> None:
        """Update agent progress during processing."""
        try:
            status_bar = self.query_one(StatusBar)
            status_bar.agent_status = status
            # Note: LoadingIndicator doesn't use progress values, it just spins
        except Exception:
            pass

    def stop_agent_progress(self) -> None:
        """Stop showing agent progress indicators."""
        self.set_agent_status("Ready", show_progress=False)

    def _update_right_sidebar(self) -> None:
        """Update the right sidebar with current session information."""
        try:
            right_sidebar = self.query_one(RightSidebar)

            # Get current agent and calculate tokens
            agent = get_current_agent()
            message_history = agent.get_message_history()

            total_tokens = sum(
                agent.estimate_tokens_for_message(msg) for msg in message_history
            )
            max_tokens = agent.get_model_context_length()

            # Calculate session duration
            from datetime import datetime

            duration = datetime.now() - self._session_start_time
            hours = int(duration.total_seconds() // 3600)
            minutes = int((duration.total_seconds() % 3600) // 60)

            if hours > 0:
                duration_str = f"{hours}h {minutes}m"
            else:
                duration_str = f"{minutes}m"

            # Update sidebar
            right_sidebar.update_context(total_tokens, max_tokens)
            right_sidebar.update_session_info(
                message_count=len(message_history),
                duration=duration_str,
                model=self.current_model,
            )

        except Exception:
            pass  # Silently fail if right sidebar not available

    async def _periodic_context_update(self) -> None:
        """Periodically update context information while agent is busy."""
        import asyncio

        while self.agent_busy:
            try:
                # Update the right sidebar with current context
                self._update_right_sidebar()

                # Wait before next update (0.5 seconds for responsive updates)
                await asyncio.sleep(0.5)
            except asyncio.CancelledError:
                # Task was cancelled, exit gracefully
                break
            except Exception:
                # Silently handle any errors to avoid crashing the update loop
                pass

    def _start_context_updates(self) -> None:
        """Start periodic context updates during agent execution."""
        # Cancel any existing update worker
        if self._context_update_worker is not None:
            try:
                self._context_update_worker.cancel()
            except Exception:
                pass

        # Start a new background worker for context updates
        self._context_update_worker = self.run_worker(
            self._periodic_context_update(), exclusive=False
        )

    def _stop_context_updates(self) -> None:
        """Stop periodic context updates."""
        if self._context_update_worker is not None:
            try:
                self._context_update_worker.cancel()
            except Exception:
                pass
            self._context_update_worker = None

        # Do a final update when stopping
        self._update_right_sidebar()

    def on_resize(self, event: Resize) -> None:
        """Handle terminal resize events to update responsive elements."""
        try:
            # Apply responsive layout adjustments
            self.apply_responsive_layout()

            # Update status bar to reflect new width
            status_bar = self.query_one(StatusBar)
            status_bar.update_status()

            # Refresh history display with new responsive truncation
            self.refresh_history_display()

        except Exception:
            pass  # Silently handle resize errors

    def apply_responsive_layout(self) -> None:
        """Apply responsive layout adjustments based on terminal size."""
        try:
            terminal_width = self.size.width if hasattr(self, "size") else 80
            terminal_height = self.size.height if hasattr(self, "size") else 24
            sidebar = self.query_one(Sidebar)

            # Calculate responsive width based on terminal width
            if terminal_width >= 120:
                responsive_width = 40
            elif terminal_width >= 100:
                responsive_width = 35
            elif terminal_width >= 80:
                responsive_width = 30
            elif terminal_width >= 60:
                responsive_width = 25
            else:
                responsive_width = 20

            # Apply same width to left sidebar (history)
            sidebar.styles.width = responsive_width

            # Apply same width to right sidebar to prevent layout shift
            try:
                right_sidebar = self.query_one(RightSidebar)
                right_sidebar.styles.width = responsive_width
            except Exception:
                pass

            # Apply same width to file tree panel to prevent layout shift
            try:
                file_tree = self.query_one(FileTreePanel)
                file_tree.styles.width = responsive_width
            except Exception:
                pass

            # Auto-hide sidebar on very narrow terminals
            if terminal_width < 50:
                if sidebar.display:
                    sidebar.display = False
                    self.add_system_message(
                        "💡 Sidebar auto-hidden for narrow terminal. Press Ctrl+2 to toggle."
                    )

            # Adjust input area height for very short terminals
            if terminal_height < 20:
                input_area = self.query_one(InputArea)
                input_area.styles.height = 10
            else:
                input_area = self.query_one(InputArea)
                input_area.styles.height = 10

        except Exception:
            pass

    def start_message_renderer_sync(self):
        """Synchronous wrapper to start message renderer via run_worker."""
        self.run_worker(self.start_message_renderer(), exclusive=False)

    async def preload_agent_on_startup(self) -> None:
        """Preload the agent/model at startup so loading status is visible."""
        try:
            # Show loading in status bar and spinner
            self.start_agent_progress("Loading")

            # Warm up agent/model without blocking UI
            import asyncio

            from ticca.agents.agent_manager import get_current_agent

            agent = get_current_agent()

            # Run the synchronous reload in a worker thread
            await asyncio.to_thread(agent.reload_code_generation_agent)

            # After load, refresh current model (in case of fallback or changes)
            # Use the effective model from the agent (respects pinned model)
            agent = get_current_agent()
            self.current_model = agent.get_model_name()

            # Update status bar with effective model
            status_bar = self.query_one(StatusBar)
            status_bar.current_model = self.current_model

            # Update right sidebar with correct context after agent loads
            self._update_right_sidebar()

            # Let the user know model/agent are ready
            self.add_system_message("✓ Model and agent ready")
        except Exception as e:
            # Surface any preload issues but keep app usable
            self.add_error_message(f"Startup preload failed: {e}")
        finally:
            # Always stop spinner and set ready state
            self.stop_agent_progress()

    async def start_message_renderer(self):
        """Start the message renderer to consume messages from the queue."""
        if not self._renderer_started:
            self._renderer_started = True

            # Process any buffered startup messages first
            from io import StringIO

            from rich.console import Console

            from ticca.messaging import get_buffered_startup_messages

            buffered_messages = get_buffered_startup_messages()

            if buffered_messages:
                # Group startup messages into a single display
                startup_content_lines = []

                for message in buffered_messages:
                    try:
                        # Convert message content to string for grouping
                        if hasattr(message.content, "__rich_console__"):
                            # For Rich objects, render to plain text
                            string_io = StringIO()
                            # Use markup=False to prevent interpretation of square brackets as markup
                            temp_console = Console(
                                file=string_io,
                                width=80,
                                legacy_windows=False,
                                markup=False,
                            )
                            temp_console.print(message.content)
                            content_str = string_io.getvalue().rstrip("\n")
                        else:
                            content_str = str(message.content)

                        startup_content_lines.append(content_str)
                    except Exception as e:
                        startup_content_lines.append(
                            f"Error processing startup message: {e}"
                        )

                # Create a single grouped startup message (tightened)
                grouped_content = "\n".join(startup_content_lines)
                self.add_system_message(self._tighten_text(grouped_content))

                # Clear the startup buffer after processing
                self.message_queue.clear_startup_buffer()

            # Now start the regular message renderer
            await self.message_renderer.start()

    async def maybe_prompt_restore_autosave(self) -> None:
        """Offer to restore an autosave session at startup (TUI version)."""
        try:
            from pathlib import Path

            from ticca.config import (
                AUTOSAVE_DIR,
                set_current_autosave_from_session_name,
            )
            from ticca.session_storage import list_sessions, load_session

            base_dir = Path(AUTOSAVE_DIR)
            sessions = list_sessions(base_dir)
            if not sessions:
                self.add_system_message("📭 No saved sessions available to resume")
                return

            # Show modal picker for selection
            from .screens.autosave_picker import AutosavePicker

            async def handle_result(result_name: str | None):
                if not result_name:
                    return
                try:
                    # Load history and set into agent
                    from ticca.agents.agent_manager import get_current_agent

                    history = load_session(result_name, base_dir)
                    agent = get_current_agent()
                    agent.set_message_history(history)

                    # Set current autosave session id so subsequent autosaves overwrite this session
                    try:
                        set_current_autosave_from_session_name(result_name)
                    except Exception:
                        pass

                    # Update token info/status bar
                    total_tokens = sum(
                        agent.estimate_tokens_for_message(msg) for msg in history
                    )
                    try:
                        status_bar = self.query_one(StatusBar)
                        status_bar.update_token_info(
                            total_tokens,
                            agent.get_model_context_length(),
                            total_tokens / max(1, agent.get_model_context_length()),
                        )
                    except Exception:
                        pass

                    # Notify
                    session_path = base_dir / f"{result_name}.pkl"
                    self.add_system_message(
                        f"✅ Autosave loaded: {len(history)} messages ({total_tokens} tokens)\n"
                        f"📁 From: {session_path}"
                    )

                    # Refresh history sidebar
                    self.refresh_history_display()
                except Exception as e:
                    self.add_error_message(f"Failed to load autosave: {e}")

            # Push modal and await result
            picker = AutosavePicker(base_dir)

            # Use Textual's push_screen with a result callback
            def on_picker_result(result_name=None):
                # Schedule async handler to avoid blocking UI

                self.run_worker(handle_result(result_name), exclusive=False)

            self.push_screen(picker, on_picker_result)
        except Exception as e:
            # Fail silently but show debug in chat
            self.add_system_message(f"[dim]Autosave prompt error: {e}[/dim]")

    async def stop_message_renderer(self):
        """Stop the message renderer."""
        if self._renderer_started:
            self._renderer_started = False
            try:
                await self.message_renderer.stop()
            except Exception as e:
                # Log renderer stop errors but don't crash
                self.add_system_message(f"Renderer stop error: {e}")

    @on(ListView.Selected, "#history-list")
    def on_history_list_selected(self, event: ListView.Selected) -> None:
        """Handle clicks on history list items - show modal on double-click."""
        import time

        current_time = time.time()
        current_index = event.list_view.index

        # Check if this is a double-click (within 0.5 seconds and same item)
        if (
            self._last_history_click_time is not None
            and self._last_history_click_index == current_index
            and (current_time - self._last_history_click_time) < 0.5
        ):
            # This is a double-click - show the modal
            try:
                sidebar = self.query_one(Sidebar)
                sidebar.current_history_index = current_index

                from .components.command_history_modal import CommandHistoryModal

                self.push_screen(CommandHistoryModal())
            except Exception:
                pass

            # Reset tracking
            self._last_history_click_time = None
            self._last_history_click_index = None
        else:
            # This is a single click - just track it
            self._last_history_click_time = current_time
            self._last_history_click_index = current_index

    @on(HistoryEntrySelected)
    def on_history_entry_selected(self, event: HistoryEntrySelected) -> None:
        """Handle selection of a history entry from the sidebar."""
        # Display the history entry details
        self.show_history_details(event.history_entry)

    @on(CommandSelected)
    def on_command_selected(self, event: CommandSelected) -> None:
        """Handle selection of a command from the history modal."""
        # Set the command in the input field
        input_field = self.query_one("#input-field", CustomTextArea)
        input_field.text = event.command

        # Focus the input field for immediate editing
        input_field.focus()

        # Close the sidebar automatically for a smoother workflow
        sidebar = self.query_one(Sidebar)
        sidebar.display = False

    @on(RightSidebar.AgentChanged)
    def on_right_sidebar_agent_changed(self, event: RightSidebar.AgentChanged) -> None:
        """Handle agent change from right sidebar dropdown."""
        try:
            # Prevent agent switching when Easy Mode is enabled
            from ticca.config import get_easy_mode
            if get_easy_mode():
                self.add_system_message("⚠️  Agent switching is disabled in Easy Mode")
                return

            agent_name = event.agent_name

            # Use the agent manager to switch agents
            from ticca.agents.agent_manager import set_current_agent

            success = set_current_agent(agent_name)
            if not success:
                self.add_error_message(f"Failed to switch to agent: {agent_name}")
                return

            # Get the new agent
            agent = get_current_agent()
            self.current_agent = agent.display_name

            # Update to show the effective model (respects pinned model)
            self.current_model = agent.get_model_name()

            # Update status bar
            status_bar = self.query_one(StatusBar)
            status_bar.current_model = self.current_model

            # Update right sidebar display
            self._update_right_sidebar()

            # Show success message
            self.add_system_message(f"✅ Agent switched to: {agent.display_name}")

        except Exception as e:
            self.add_error_message(f"Failed to switch agent: {e}")

    @on(RightSidebar.ModelChanged)
    def on_right_sidebar_model_changed(self, event: RightSidebar.ModelChanged) -> None:
        """Handle model change from right sidebar dropdown."""
        try:
            model_name = event.model_name
            set_active_model(model_name)

            # Reload agent with new model
            try:
                agent = get_current_agent()
                agent.reload_code_generation_agent()
                # Get the effective model after reload (respects pinned model)
                self.current_model = agent.get_model_name()
            except Exception as reload_error:
                self.add_error_message(
                    f"Failed to reload agent after model change: {reload_error}"
                )
                return

            # Update status bar
            status_bar = self.query_one(StatusBar)
            status_bar.current_model = self.current_model

            # Update right sidebar display
            self._update_right_sidebar()

            # Show success message
            self.add_system_message(f"✅ Model switched to: {model_name}")

        except Exception as e:
            self.add_error_message(f"Failed to switch model: {e}")

    @on(RightSidebar.CommitRequested)
    def on_right_sidebar_commit_requested(self, event: RightSidebar.CommitRequested) -> None:
        """Handle commit button click from right sidebar."""
        try:
            from ticca.plugins.gac.gac_wrapper import generate_commit_message, unstage_files
            from .components.commit_message_modal import CommitMessageModal
            from .components.security_warning_modal import SecurityWarningModal

            # Show loading message
            self.add_system_message("Generating commit message...")

            # Generate the commit message (automatically stage all changes)
            result = generate_commit_message(stage_all=True)

            if not result:
                self.add_error_message("Failed to generate commit message")
                return

            # Check for security warnings
            if result.secrets:
                # Show security warning modal
                def handle_security_decision(decision):
                    if decision == "continue":
                        # User wants to proceed despite warnings
                        self.add_system_message("⚠️  Continuing with potential secrets in commit")
                        if result.message:
                            self.push_screen(CommitMessageModal(result.message, create_commit=True))
                    elif decision == "unstage":
                        # Unstage affected files and regenerate commit with remaining files
                        if unstage_files(result.affected_files):
                            self.add_system_message(f"✓ Unstaged {len(result.affected_files)} file(s) with secrets")
                            # Regenerate commit message for remaining staged files
                            self.add_system_message("Regenerating commit message for remaining files...")
                            new_result = generate_commit_message(stage_all=False)
                            if new_result and new_result.message:
                                self.push_screen(CommitMessageModal(new_result.message, create_commit=True))
                            else:
                                self.add_error_message("No staged changes remaining after unstaging files")
                        else:
                            self.add_error_message("Failed to unstage some files")
                    # else: cancel - do nothing

                self.push_screen(
                    SecurityWarningModal(result.secrets, result.affected_files),
                    handle_security_decision
                )
            elif result.message:
                # No secrets - proceed with commit
                self.push_screen(CommitMessageModal(result.message, create_commit=True))
            else:
                self.add_error_message("No commit message generated")

        except Exception as e:
            self.add_error_message(f"Error generating commit message: {e}")

    @on(RightSidebar.GitPullRequested)
    def on_right_sidebar_git_pull_requested(self, event: RightSidebar.GitPullRequested) -> None:
        """Handle git pull button click from right sidebar."""
        try:
            import subprocess

            self.add_system_message("Pulling from remote...")

            result = subprocess.run(
                ["git", "pull"],
                capture_output=True,
                text=True,
                check=False
            )

            if result.returncode == 0:
                output = result.stdout.strip()
                if output:
                    self.add_system_message(f"✓ Git pull successful:\n{output}")
                else:
                    self.add_system_message("✓ Git pull successful")
            else:
                error = result.stderr.strip() or result.stdout.strip()
                self.add_error_message(f"Git pull failed:\n{error}")

        except FileNotFoundError:
            self.add_error_message("git command not found. Please ensure git is installed.")
        except Exception as e:
            self.add_error_message(f"Error during git pull: {e}")

    @on(RightSidebar.GitPushRequested)
    def on_right_sidebar_git_push_requested(self, event: RightSidebar.GitPushRequested) -> None:
        """Handle git push button click from right sidebar."""
        try:
            import subprocess

            self.add_system_message("Pushing to remote...")

            result = subprocess.run(
                ["git", "push"],
                capture_output=True,
                text=True,
                check=False
            )

            if result.returncode == 0:
                output = result.stdout.strip() or result.stderr.strip()  # git push outputs to stderr
                if output:
                    self.add_system_message(f"✓ Git push successful:\n{output}")
                else:
                    self.add_system_message("✓ Git push successful")
            else:
                error = result.stderr.strip() or result.stdout.strip()
                self.add_error_message(f"Git push failed:\n{error}")

        except FileNotFoundError:
            self.add_error_message("git command not found. Please ensure git is installed.")
        except Exception as e:
            self.add_error_message(f"Error during git push: {e}")

    async def on_unmount(self):
        """Clean up when the app is unmounted."""
        try:
            # Unregister the agent reload callback
            from ticca.callbacks import unregister_callback

            unregister_callback("agent_reload", self._on_agent_reload)

            await self.stop_message_renderer()
        except Exception as e:
            # Log unmount errors but don't crash during cleanup
            try:
                self.add_system_message(f"Unmount cleanup error: {e}")
            except Exception:
                # If we can't even add a message, just ignore
                pass


async def run_textual_ui(initial_command: str = None):
    """Run the Textual UI interface."""
    from ticca.config import load_api_keys_to_environment

    # Initialize the command history file
    initialize_command_history_file()

    # Load API keys from puppy.cfg into environment variables
    load_api_keys_to_environment()

    # YOLO mode is now user-configurable via Settings (Ctrl+3)
    # No longer forced to "true" in TUI mode

    app = CodePuppyTUI(initial_command=initial_command)
    await app.run_async()
