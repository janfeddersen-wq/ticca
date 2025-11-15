"""
UI Settings screen for appearance and display preferences.
"""

from textual.app import ComposeResult
from textual.containers import Container, Horizontal, VerticalScroll
from textual.screen import ModalScreen
from textual.widgets import Button, Input, Label, Select, Static, Switch, TabbedContent, TabPane
from textual import on


class UISettingsScreen(ModalScreen):
    """UI settings configuration screen with tabbed interface."""

    DEFAULT_CSS = """
    UISettingsScreen {
        align: center middle;
    }

    #ui-settings-dialog {
        width: 110;
        height: 40;
        border: round $primary;
        background: $surface;
        padding: 1 2;
    }

    #ui-settings-title {
        text-align: center;
        text-style: bold;
        color: $accent;
        margin: 0 0 1 0;
    }

    #ui-settings-tabs {
        height: 1fr;
        margin: 0 0 1 0;
    }

    .switch-row {
        layout: horizontal;
        height: auto;
        margin: 0 0 1 0;
        align: left middle;
    }

    .switch-row .setting-label {
        width: 35;
        margin: 0 1 0 0;
        padding: 0;
        height: auto;
        content-align: left middle;
    }

    .switch-row Switch {
        width: 4;
        margin: 0 2 0 0;
        height: 1;
        padding: 0;
    }

    .switch-row .setting-description {
        width: 1fr;
        margin: 0;
        padding: 0;
        height: auto;
        color: $text-muted;
        text-style: italic;
    }

    .setting-row {
        layout: horizontal;
        height: auto;
        margin: 0 0 0 0;
        align: left middle;
        padding: 0;
    }

    .setting-label {
        width: 30;
        text-align: left;
        padding: 0 1 0 0;
        content-align: left middle;
    }

    .setting-input {
        width: 1fr;
        margin: 0;
    }

    .setting-description {
        color: $text-muted;
        text-style: italic;
        width: 1fr;
        margin: 0 0 1 0;
        height: auto;
    }

    .input-description {
        margin: 0 0 1 31;
    }

    .section-header {
        text-style: bold;
        color: $primary-lighten-1;
        margin: 1 0 0 0;
    }

    Input {
        width: 100%;
        border: round $primary;
        background: $panel;
        color: $foreground;
        padding: 0;
    }

    Input:focus {
        border: round $accent;
        background: $secondary;
    }

    Select {
        width: 100%;
        height: 1;
        min-height: 1;
        border: none !important;
        background: $panel;
        color: $foreground;
        padding: 0 !important;
    }

    Select:focus {
        border: none !important;
        background: $secondary;
    }

    Select:hover {
        border: none !important;
        background: $secondary;
    }

    Select > * {
        border: none !important;
        padding: 0 !important;
    }

    Switch {
        width: 4;
        height: 1;
        min-width: 4;
        padding: 0;
        margin: 0;
        border: none !important;
        background: transparent;
    }

    Switch:focus {
        border: none !important;
    }

    Switch:hover {
        border: none !important;
    }

    Switch > * {
        border: none !important;
    }

    .tab-scroll {
        height: 1fr;
        overflow: auto;
    }

    TabPane {
        padding: 1 2;
    }

    #ui-settings-buttons {
        layout: horizontal;
        height: 3;
        align: center middle;
        margin: 1 0 0 0;
    }

    #save-button, #cancel-button {
        margin: 0 1;
        min-width: 12;
        height: 3;
    }

    #save-button {
        border: wide $accent;
        background: $primary;
        color: $background;
    }

    #save-button:hover {
        border: wide $accent-lighten-1;
        background: $primary-lighten-1;
    }

    #cancel-button {
        border: wide $primary;
        background: $secondary;
        color: $text;
    }

    #cancel-button:hover {
        border: wide $primary-lighten-1;
        background: $border;
    }
    """

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def compose(self) -> ComposeResult:
        with Container(id="ui-settings-dialog"):
            yield Label("🎨 UI Settings", id="ui-settings-title")

            with TabbedContent(id="ui-settings-tabs"):
                # Tab 1: General
                with TabPane("General", id="general"):
                    with VerticalScroll(classes="tab-scroll"):
                        with Container(classes="switch-row"):
                            yield Label("Easy Mode:", classes="setting-label")
                            yield Switch(id="easy-mode-switch", classes="setting-input")
                            yield Static(
                                "Simplified interface (hides agent selector, forces code-agent).",
                                classes="setting-description",
                            )

                        with Container(classes="switch-row"):
                            yield Label("YOLO Mode (auto-confirm):", classes="setting-label")
                            yield Switch(id="yolo-mode-switch", classes="setting-input")
                            yield Static(
                                "If enabled, agent commands execute without confirmation.",
                                classes="setting-description",
                            )

                        with Container(classes="switch-row"):
                            yield Label("Allow Agent Recursion:", classes="setting-label")
                            yield Switch(id="allow-recursion-switch", classes="setting-input")
                            yield Static(
                                "Permits agents to call other agents to complete tasks.",
                                classes="setting-description",
                            )

                        with Container(classes="setting-row"):
                            yield Label("UI Theme:", classes="setting-label")
                            yield Select([], id="theme-select", classes="setting-input")
                        yield Static(
                            "Color theme for the TUI (applies instantly).",
                            classes="input-description",
                        )

                # Tab 2: Appearance
                with TabPane("Appearance", id="appearance"):
                    with VerticalScroll(classes="tab-scroll"):
                        yield Label("UI Panels", classes="section-header")
                        yield Static(
                            "Control visibility of sidebar panels.",
                            classes="setting-description",
                        )

                        with Container(classes="switch-row"):
                            yield Label("Show File Tree:", classes="setting-label")
                            yield Switch(id="show-file-tree-switch", classes="setting-input")
                            yield Static(
                                "Show or hide the left file tree panel (toggle with Ctrl+4).",
                                classes="setting-description",
                            )

                        yield Label("Message Display", classes="section-header")
                        yield Static(
                            "Control which message types are displayed in the chat view.",
                            classes="setting-description",
                        )

                        with Container(classes="switch-row"):
                            yield Label("Suppress Thinking Messages:", classes="setting-label")
                            yield Switch(id="suppress-thinking-switch", classes="setting-input")
                            yield Static(
                                "Hide agent reasoning and planning messages (reduces clutter).",
                                classes="setting-description",
                            )

                        with Container(classes="switch-row"):
                            yield Label("Suppress Informational Messages:", classes="setting-label")
                            yield Switch(id="suppress-informational-switch", classes="setting-input")
                            yield Static(
                                "Hide info, success, and warning messages (quieter experience).",
                                classes="setting-description",
                            )

                # Tab 3: History & Context
                with TabPane("History & Context", id="history"):
                    with VerticalScroll(classes="tab-scroll"):
                        with Container(classes="setting-row"):
                            yield Label("Compaction Strategy:", classes="setting-label")
                            yield Select(
                                [
                                    ("Summarization", "summarization"),
                                    ("Truncation", "truncation"),
                                ],
                                id="compaction-strategy-select",
                                classes="setting-input",
                            )
                        yield Static(
                            "How to compress context when it gets too large.",
                            classes="input-description",
                        )

                        with Container(classes="setting-row"):
                            yield Label("Compaction Threshold:", classes="setting-label")
                            yield Input(
                                id="compaction-threshold-input",
                                classes="setting-input",
                                placeholder="0.85",
                            )
                        yield Static(
                            "Percentage of context usage that triggers compaction (0.80-0.95).",
                            classes="input-description",
                        )

                        with Container(classes="setting-row"):
                            yield Label("Protected Recent Tokens:", classes="setting-label")
                            yield Input(
                                id="protected-tokens-input",
                                classes="setting-input",
                                placeholder="50000",
                            )
                        yield Static(
                            "Number of recent tokens to preserve during compaction.",
                            classes="input-description",
                        )

                        with Container(classes="switch-row"):
                            yield Label("Auto-Save Session:", classes="setting-label")
                            yield Switch(id="auto-save-switch", classes="setting-input")
                            yield Static(
                                "Automatically save the session after each LLM response.",
                                classes="setting-description",
                            )

                        with Container(classes="setting-row"):
                            yield Label("Max Autosaved Sessions:", classes="setting-label")
                            yield Input(
                                id="max-autosaves-input",
                                classes="setting-input",
                                placeholder="20",
                            )
                        yield Static(
                            "Maximum number of autosaves to keep (0 for unlimited).",
                            classes="input-description",
                        )

            with Horizontal(id="ui-settings-buttons"):
                yield Button("Save & Close", id="save-button", variant="primary")
                yield Button("Cancel", id="cancel-button")

    def on_mount(self) -> None:
        """Load current settings when the screen mounts."""
        from ticca.config import (
            get_easy_mode,
            get_yolo_mode,
            get_allow_recursion,
            get_show_file_tree,
            get_suppress_informational_messages,
            get_suppress_thinking_messages,
            get_value,
            get_compaction_strategy,
            get_compaction_threshold,
            get_protected_token_count,
            get_auto_save_session,
            get_max_saved_sessions,
        )

        # Tab 1: General
        self.query_one("#easy-mode-switch", Switch).value = get_easy_mode()
        self.query_one("#yolo-mode-switch", Switch).value = get_yolo_mode()
        self.query_one("#allow-recursion-switch", Switch).value = get_allow_recursion()
        self.load_theme_options()

        # Tab 2: Appearance
        self.query_one("#show-file-tree-switch", Switch).value = get_show_file_tree()
        self.query_one("#suppress-thinking-switch", Switch).value = get_suppress_thinking_messages()
        self.query_one("#suppress-informational-switch", Switch).value = get_suppress_informational_messages()

        # Tab 3: History & Context
        self.query_one("#compaction-strategy-select", Select).value = get_compaction_strategy()
        self.query_one("#compaction-threshold-input", Input).value = str(get_compaction_threshold())
        self.query_one("#protected-tokens-input", Input).value = str(get_protected_token_count())
        self.query_one("#auto-save-switch", Switch).value = get_auto_save_session()
        self.query_one("#max-autosaves-input", Input).value = str(get_max_saved_sessions())

    def load_theme_options(self):
        """Load available themes into the theme select widget."""
        try:
            from ticca.themes import ThemeManager
            from ticca.config import get_value

            themes = ThemeManager.list_themes()
            theme_options = [(display_name, theme_name) for theme_name, display_name in themes.items()]
            theme_options.sort(key=lambda x: x[0])
            self.query_one("#theme-select", Select).set_options(theme_options)

            try:
                current_theme = get_value("tui_theme") or "nord"
            except Exception:
                current_theme = "nord"

            self.query_one("#theme-select", Select).value = current_theme

        except Exception:
            fallback = [("Nord", "nord")]
            self.query_one("#theme-select", Select).set_options(fallback)
            self.query_one("#theme-select", Select).value = "nord"

    @on(Button.Pressed, "#save-button")
    def save_settings(self) -> None:
        """Save the modified settings."""
        from ticca.config import (
            get_easy_mode,
            get_model_context_length,
            set_easy_mode,
            set_show_file_tree,
            set_suppress_informational_messages,
            set_suppress_thinking_messages,
            set_config_value,
            set_auto_save_session,
            set_max_saved_sessions,
        )

        try:
            # Tab 1: General
            easy_mode = self.query_one("#easy-mode-switch", Switch).value
            yolo_mode = self.query_one("#yolo-mode-switch", Switch).value
            allow_recursion = self.query_one("#allow-recursion-switch", Switch).value
            selected_theme = self.query_one("#theme-select", Select).value

            current_easy_mode = get_easy_mode()
            easy_mode_changed = (easy_mode != current_easy_mode)

            set_easy_mode(easy_mode)
            set_config_value("yolo_mode", "true" if yolo_mode else "false")
            set_config_value("allow_recursion", "true" if allow_recursion else "false")

            theme_changed = False
            if selected_theme:
                from ticca.config import get_value
                current_theme = get_value("tui_theme") or "nord"
                if selected_theme != current_theme:
                    set_config_value("tui_theme", selected_theme)
                    self.app.theme = selected_theme
                    theme_changed = True

            # Tab 2: Appearance
            show_file_tree = self.query_one("#show-file-tree-switch", Switch).value
            suppress_thinking = self.query_one("#suppress-thinking-switch", Switch).value
            suppress_informational = self.query_one("#suppress-informational-switch", Switch).value

            set_show_file_tree(show_file_tree)
            set_suppress_thinking_messages(suppress_thinking)
            set_suppress_informational_messages(suppress_informational)

            # Tab 3: History & Context
            compaction_strategy = self.query_one("#compaction-strategy-select", Select).value
            compaction_threshold = self.query_one("#compaction-threshold-input", Input).value.strip()
            protected_tokens = self.query_one("#protected-tokens-input", Input).value.strip()
            auto_save = self.query_one("#auto-save-switch", Switch).value
            max_autosaves = self.query_one("#max-autosaves-input", Input).value.strip()

            if compaction_strategy in ["summarization", "truncation"]:
                set_config_value("compaction_strategy", compaction_strategy)

            if compaction_threshold:
                threshold_value = float(compaction_threshold)
                if 0.8 <= threshold_value <= 0.95:
                    set_config_value("compaction_threshold", compaction_threshold)
                else:
                    raise ValueError("Compaction threshold must be between 0.8 and 0.95")

            if protected_tokens.isdigit():
                tokens_value = int(protected_tokens)
                model_context_length = get_model_context_length()
                max_protected_tokens = int(model_context_length * 0.75)
                if 1000 <= tokens_value <= max_protected_tokens:
                    set_config_value("protected_token_count", protected_tokens)
                else:
                    raise ValueError(f"Protected tokens must be between 1000 and {max_protected_tokens}")

            set_auto_save_session(auto_save)

            if max_autosaves.isdigit():
                set_max_saved_sessions(int(max_autosaves))

            # Return success message
            from ticca.config import CONFIG_FILE

            message = "✅ UI Settings saved successfully!\n"
            message += f"📁 Config: {CONFIG_FILE}"

            if theme_changed:
                message += f"\n🎨 Theme changed to: {selected_theme}"

            if easy_mode_changed:
                message += f"\n⚡ Easy Mode: {'ON' if easy_mode else 'OFF'}"

            self.dismiss({
                "success": True,
                "message": message,
                "theme_changed": theme_changed,
                "easy_mode_changed": easy_mode_changed,
            })

        except Exception as e:
            self.dismiss({"success": False, "message": f"❌ Error saving settings: {str(e)}"})

    @on(Button.Pressed, "#cancel-button")
    def cancel_settings(self) -> None:
        """Cancel settings changes."""
        self.dismiss({"success": False, "message": "Settings cancelled"})

    def on_key(self, event) -> None:
        """Handle key events."""
        if event.key == "escape":
            self.cancel_settings()
