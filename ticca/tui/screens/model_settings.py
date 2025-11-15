"""
Model Settings screen for AI model configuration and agent pinning.
"""

import os
from textual.app import ComposeResult
from textual.containers import Container, Horizontal, VerticalScroll
from textual.screen import ModalScreen
from textual.widgets import Button, Input, Label, Select, Static, Switch, TabbedContent, TabPane
from textual import on


class ModelSettingsScreen(ModalScreen):
    """Model settings configuration screen with tabbed interface."""

    DEFAULT_CSS = """
    ModelSettingsScreen {
        align: center middle;
    }

    #model-settings-dialog {
        width: 110;
        height: 40;
        border: round $primary;
        background: $surface;
        padding: 1 2;
    }

    #model-settings-title {
        text-align: center;
        text-style: bold;
        color: $accent;
        margin: 0 0 1 0;
    }

    #model-settings-tabs {
        height: 1fr;
        margin: 0 0 1 0;
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

    .setting-input Input {
        height: 3;
    }

    .setting-input Select {
        height: auto;
        min-height: 1;
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

    .tab-scroll {
        height: 1fr;
        overflow: auto;
    }

    TabPane {
        padding: 1 2;
    }

    #agent-pinning-container {
        margin: 1 0;
    }

    .agent-pin-row {
        layout: horizontal;
        height: auto;
        margin: 0 0 1 0;
        align: left middle;
    }

    .agent-pin-row .setting-label {
        width: 35;
        margin: 0 1 0 0;
        padding: 0;
        height: auto;
    }

    .agent-pin-row Select {
        width: 1fr;
        margin: 0;
        padding: 0 !important;
        border: none !important;
        height: 1;
        min-height: 1;
    }

    .agent-pin-row Select:focus {
        border: none !important;
    }

    .agent-pin-row Select:hover {
        border: none !important;
    }

    .agent-pin-row Select > * {
        border: none !important;
        padding: 0 !important;
    }

    #model-settings-buttons {
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

    #gac-auth-button, #chatgpt-auth-button {
        width: 20;
        min-width: 20;
        height: 3;
        border: wide $accent;
        border-bottom: wide $accent-darken-1;
        border-right: wide $accent-darken-1;
        background: $primary;
        color: $background;
    }

    #gac-auth-button:hover, #chatgpt-auth-button:hover {
        border: wide $accent-lighten-1;
        border-bottom: wide $secondary;
        border-right: wide $secondary;
        background: $primary-lighten-1;
    }

    #gac-auth-button:focus, #chatgpt-auth-button:focus {
        border: wide $panel;
        border-top: wide $accent;
        border-left: wide $accent;
        background: $primary-darken-1;
        color: $accent;
    }
    """

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def compose(self) -> ComposeResult:
        with Container(id="model-settings-dialog"):
            yield Label("🤖 Model Settings", id="model-settings-title")

            with TabbedContent(id="model-settings-tabs"):
                # Tab 1: Models & AI
                with TabPane("Models & AI", id="models"):
                    with VerticalScroll(classes="tab-scroll"):
                        with Container(classes="setting-row"):
                            yield Label("Default Model:", classes="setting-label")
                            yield Select([], id="model-select", classes="setting-input")
                        yield Static(
                            "The primary model used for code generation.",
                            classes="input-description",
                        )

                        with Container(classes="setting-row"):
                            yield Label("Vision Model (VQA):", classes="setting-label")
                            yield Select([], id="vqa-model-select", classes="setting-input")
                        yield Static(
                            "Model used for vision and image-related tasks.",
                            classes="input-description",
                        )

                        with Container(classes="setting-row"):
                            yield Label("GPT-5 Reasoning Effort:", classes="setting-label")
                            yield Select(
                                [
                                    ("Low", "low"),
                                    ("Medium", "medium"),
                                    ("High", "high"),
                                ],
                                id="reasoning-effort-select",
                                classes="setting-input",
                            )
                        yield Static(
                            "Reasoning effort for GPT-5 models (only applies to GPT-5).",
                            classes="input-description",
                        )

                # Tab 2: Agents & Integrations
                with TabPane("Agents & Integrations", id="integrations"):
                    with VerticalScroll(classes="tab-scroll"):
                        yield Label("Agent Model Pinning", classes="section-header", id="agent-pinning-header")
                        yield Static(
                            "Pin specific models to individual agents. Select '(default)' to use the global model.",
                            classes="setting-description",
                            id="agent-pinning-description",
                        )
                        yield Container(id="agent-pinning-container")

                        yield Label("GAC Plugin", classes="section-header", id="gac-header")
                        yield Static(
                            "Configure AI-powered git commit message generation.",
                            classes="setting-description",
                            id="gac-description",
                        )

                        with Container(classes="switch-row", id="gac-enabled-row"):
                            yield Label("Enable GAC Plugin:", classes="setting-label")
                            yield Switch(id="gac-enabled-switch", classes="setting-input")
                            yield Static(
                                "Enable AI-powered commit message generation with /commit commands.",
                                classes="setting-description",
                            )

                        with Container(classes="setting-row", id="gac-model-row"):
                            yield Label("GAC Model:", classes="setting-label")
                            yield Select([], id="gac-model-select", classes="setting-input")
                        yield Static(
                            "Model to use for commit message generation. Select '(default)' to use global model.",
                            classes="input-description",
                            id="gac-model-description",
                        )

                        yield Label("MCP & DBOS", classes="section-header")

                        with Container(classes="switch-row"):
                            yield Label("Disable All MCP Servers:", classes="setting-label")
                            yield Switch(id="disable-mcp-switch", classes="setting-input")
                            yield Static(
                                "Globally enable or disable the Model Context Protocol.",
                                classes="setting-description",
                            )

                        with Container(classes="switch-row"):
                            yield Label("Enable DBOS:", classes="setting-label")
                            yield Switch(id="enable-dbos-switch", classes="setting-input")
                            yield Static(
                                "Use DBOS for durable, resumable agent workflows.",
                                classes="setting-description",
                            )

                # Tab 3: API Keys & Status
                with TabPane("API Keys & Status", id="status"):
                    with VerticalScroll(classes="tab-scroll"):
                        yield Static("API Keys Configuration", classes="section-header")

                        with Container(classes="setting-row"):
                            yield Label("OpenAI API Key:", classes="setting-label")
                            yield Input(id="openai-api-key-input", classes="setting-input", password=True)
                        yield Static("Required for OpenAI GPT models", classes="input-description")

                        with Container(classes="setting-row"):
                            yield Label("Gemini API Key:", classes="setting-label")
                            yield Input(id="gemini-api-key-input", classes="setting-input", password=True)
                        yield Static("Required for Google Gemini models", classes="input-description")

                        with Container(classes="setting-row"):
                            yield Label("Anthropic API Key:", classes="setting-label")
                            yield Input(id="anthropic-api-key-input", classes="setting-input", password=True)
                        yield Static("Required for Anthropic Claude models", classes="input-description")

                        with Container(classes="setting-row"):
                            yield Label("Cerebras API Key:", classes="setting-label")
                            yield Input(id="cerebras-api-key-input", classes="setting-input", password=True)
                        yield Static("Required for Cerebras models", classes="input-description")

                        with Container(classes="setting-row"):
                            yield Label("Synthetic API Key:", classes="setting-label")
                            yield Input(id="syn-api-key-input", classes="setting-input", password=True)
                        yield Static("Required for Synthetic provider models", classes="input-description")

                        with Container(classes="setting-row"):
                            yield Label("Azure OpenAI API Key:", classes="setting-label")
                            yield Input(id="azure-api-key-input", classes="setting-input", password=True)
                        yield Static("Required for Azure OpenAI", classes="input-description")

                        with Container(classes="setting-row"):
                            yield Label("Azure OpenAI Endpoint:", classes="setting-label")
                            yield Input(id="azure-endpoint-input", classes="setting-input")
                        yield Static("Azure OpenAI endpoint URL", classes="input-description")

                        yield Static("", classes="section-header")

                        with Container(classes="setting-row"):
                            yield Label("Claude Code OAuth:", classes="setting-label")
                            yield Button("Authenticate", id="gac-auth-button")
                        yield Static(
                            "Authenticate with Claude Code OAuth for enhanced features",
                            classes="input-description",
                        )

                        with Container(classes="setting-row"):
                            yield Label("ChatGPT OAuth:", classes="setting-label")
                            yield Button("Authenticate", id="chatgpt-auth-button")
                        yield Static(
                            "Authenticate with ChatGPT OAuth to access ChatGPT models",
                            classes="input-description",
                        )

            with Horizontal(id="model-settings-buttons"):
                yield Button("Save & Close", id="save-button", variant="primary")
                yield Button("Cancel", id="cancel-button")

    def on_mount(self) -> None:
        """Load current settings when the screen mounts."""
        from ticca.config import (
            get_easy_mode,
            get_global_model_name,
            get_vqa_model_name,
            get_openai_reasoning_effort,
            get_gac_enabled,
            get_gac_model,
            get_mcp_disabled,
            get_use_dbos,
        )

        # Check if Easy Mode is enabled
        easy_mode = get_easy_mode()

        # Tab 1: Models & AI
        self.load_model_options()
        self.query_one("#model-select", Select).value = get_global_model_name()
        self.query_one("#vqa-model-select", Select).value = get_vqa_model_name()
        self.query_one("#reasoning-effort-select", Select).value = get_openai_reasoning_effort()

        # Tab 2: Agents & Integrations
        if easy_mode:
            # Hide agent pinning section in Easy Mode
            self.query_one("#agent-pinning-header", Label).display = False
            self.query_one("#agent-pinning-description", Static).display = False
            self.query_one("#agent-pinning-container", Container).display = False

            # Hide GAC Plugin section in Easy Mode
            self.query_one("#gac-header", Label).display = False
            self.query_one("#gac-description", Static).display = False
            self.query_one("#gac-enabled-row", Container).display = False
            self.query_one("#gac-model-row", Container).display = False
            self.query_one("#gac-model-description", Static).display = False
        else:
            # Show and populate agent pinning in normal mode
            self.load_agent_pinning_table()

            # Show and populate GAC settings in normal mode
            self.load_gac_model_options()
            self.query_one("#gac-enabled-switch", Switch).value = get_gac_enabled()
            gac_model = get_gac_model()
            self.query_one("#gac-model-select", Select).value = gac_model if gac_model else ""

        self.query_one("#disable-mcp-switch", Switch).value = get_mcp_disabled()
        self.query_one("#enable-dbos-switch", Switch).value = get_use_dbos()

        # Tab 3: API Keys & Status
        self.load_api_keys()

    def load_model_options(self):
        """Load available models into the model select widgets."""
        try:
            from ticca.model_factory import ModelFactory

            models_data = ModelFactory.load_config()
            model_options = []
            vqa_options = []

            for model_name, model_config in models_data.items():
                model_type = model_config.get("type", "unknown")
                display_name = f"{model_name} ({model_type})"
                model_options.append((display_name, model_name))

                if model_config.get("supports_vision") or model_config.get("supports_vqa"):
                    vqa_options.append((display_name, model_name))

            self.query_one("#model-select", Select).set_options(model_options)

            if not vqa_options:
                vqa_options = model_options

            self.query_one("#vqa-model-select", Select).set_options(vqa_options)

        except Exception:
            fallback = [("gpt-5 (openai)", "gpt-5")]
            self.query_one("#model-select", Select).set_options(fallback)
            self.query_one("#vqa-model-select", Select).set_options(fallback)

    def load_gac_model_options(self):
        """Load available models into the GAC model select widget."""
        try:
            from ticca.model_factory import ModelFactory

            models_data = ModelFactory.load_config()
            model_options = [("(use global model)", "")]
            for model_name, model_config in models_data.items():
                model_type = model_config.get("type", "unknown")
                display_name = f"{model_name} ({model_type})"
                model_options.append((display_name, model_name))

            self.query_one("#gac-model-select", Select).set_options(model_options)

        except Exception:
            fallback = [("(use global model)", "")]
            self.query_one("#gac-model-select", Select).set_options(fallback)

    def load_agent_pinning_table(self):
        """Load agent model pinning dropdowns."""
        from ticca.agents import get_available_agents
        from ticca.config import get_agent_pinned_model
        from ticca.model_factory import ModelFactory

        container = self.query_one("#agent-pinning-container")
        agents = get_available_agents()
        models_data = ModelFactory.load_config()

        model_options = [("(default)", "")]
        for model_name, model_config in models_data.items():
            model_type = model_config.get("type", "unknown")
            display_name = f"{model_name} ({model_type})"
            model_options.append((display_name, model_name))

        for agent_name, display_name in agents.items():
            pinned_model = get_agent_pinned_model(agent_name) or ""
            agent_row = Container(classes="agent-pin-row")
            container.mount(agent_row)

            label = Label(f"{display_name}:", classes="setting-label")
            agent_row.mount(label)

            select_id = f"agent-pin-{agent_name}"
            agent_select = Select(model_options, id=select_id, value=pinned_model)
            agent_row.mount(agent_select)

    def load_api_keys(self):
        """Load API keys from environment variables or ~/.ticca/puppy.cfg into input fields."""
        api_key_names = {
            "OPENAI_API_KEY": "#openai-api-key-input",
            "GEMINI_API_KEY": "#gemini-api-key-input",
            "ANTHROPIC_API_KEY": "#anthropic-api-key-input",
            "CEREBRAS_API_KEY": "#cerebras-api-key-input",
            "SYN_API_KEY": "#syn-api-key-input",
            "AZURE_OPENAI_API_KEY": "#azure-api-key-input",
            "AZURE_OPENAI_ENDPOINT": "#azure-endpoint-input",
        }

        from ticca.config import get_api_key

        for key_name, input_id in api_key_names.items():
            if key_name in os.environ and os.environ[key_name]:
                value = os.environ[key_name]
            else:
                value = get_api_key(key_name)

            self.query_one(input_id, Input).value = value or ""

    def save_api_keys(self):
        """Save API keys to ~/.ticca/puppy.cfg and update environment variables."""
        from ticca.config import set_api_key

        api_keys = {
            "OPENAI_API_KEY": self.query_one("#openai-api-key-input", Input).value.strip(),
            "GEMINI_API_KEY": self.query_one("#gemini-api-key-input", Input).value.strip(),
            "ANTHROPIC_API_KEY": self.query_one("#anthropic-api-key-input", Input).value.strip(),
            "CEREBRAS_API_KEY": self.query_one("#cerebras-api-key-input", Input).value.strip(),
            "SYN_API_KEY": self.query_one("#syn-api-key-input", Input).value.strip(),
            "AZURE_OPENAI_API_KEY": self.query_one("#azure-api-key-input", Input).value.strip(),
            "AZURE_OPENAI_ENDPOINT": self.query_one("#azure-endpoint-input", Input).value.strip(),
        }

        for key, value in api_keys.items():
            if value:
                os.environ[key] = value
            elif key in os.environ:
                del os.environ[key]

        for key, value in api_keys.items():
            set_api_key(key, value)

    @on(Button.Pressed, "#save-button")
    def save_settings(self) -> None:
        """Save the modified settings."""
        from ticca.config import (
            get_easy_mode,
            set_model_name,
            set_vqa_model_name,
            set_openai_reasoning_effort,
            set_agent_pinned_model,
            set_gac_enabled,
            set_gac_model,
            set_config_value,
            set_enable_dbos,
        )

        try:
            # Tab 1: Models & AI
            selected_model = self.query_one("#model-select", Select).value
            selected_vqa_model = self.query_one("#vqa-model-select", Select).value
            reasoning_effort = self.query_one("#reasoning-effort-select", Select).value

            model_changed = False
            if selected_model:
                set_model_name(selected_model)
                model_changed = True
            if selected_vqa_model:
                set_vqa_model_name(selected_vqa_model)
            set_openai_reasoning_effort(reasoning_effort)

            # Tab 2: Agents & Integrations
            easy_mode = get_easy_mode()
            if not easy_mode:
                from ticca.agents import get_available_agents
                agents = get_available_agents()
                for agent_name in agents.keys():
                    select_id = f"agent-pin-{agent_name}"
                    try:
                        agent_select = self.query_one(f"#{select_id}", Select)
                        pinned_model = agent_select.value
                        set_agent_pinned_model(agent_name, pinned_model)
                    except Exception:
                        pass

                # Save GAC settings only if not in Easy Mode
                gac_enabled = self.query_one("#gac-enabled-switch", Switch).value
                gac_model = self.query_one("#gac-model-select", Select).value
                set_gac_enabled(gac_enabled)
                set_gac_model(gac_model if gac_model else "")
            else:
                # In Easy Mode, force GAC to use default model
                set_gac_model("")  # Empty string means "use global model"

            disable_mcp = self.query_one("#disable-mcp-switch", Switch).value
            enable_dbos = self.query_one("#enable-dbos-switch", Switch).value
            set_config_value("disable_mcp", "true" if disable_mcp else "false")
            set_enable_dbos(enable_dbos)

            # Tab 3: API Keys & Status
            self.save_api_keys()

            # Reload agent if model changed
            if model_changed:
                try:
                    from ticca.agents import get_current_agent
                    current_agent = get_current_agent()
                    current_agent.reload_code_generation_agent()
                except Exception:
                    pass

            # Return success message
            from ticca.config import CONFIG_FILE

            message = "✅ Model Settings saved successfully!\n"
            message += f"📁 Config & API Keys: {CONFIG_FILE}"

            if model_changed:
                message += f"\n🔄 Model switched to: {selected_model}"

            self.dismiss({
                "success": True,
                "message": message,
                "model_changed": model_changed,
            })

        except Exception as e:
            self.dismiss({"success": False, "message": f"❌ Error saving settings: {str(e)}"})

    @on(Button.Pressed, "#cancel-button")
    def cancel_settings(self) -> None:
        """Cancel settings changes."""
        self.dismiss({"success": False, "message": "Settings cancelled"})

    @on(Button.Pressed, "#gac-auth-button")
    def handle_gac_auth(self) -> None:
        """Handle Claude Code OAuth authentication."""
        try:
            from ticca.plugins.claude_code_oauth.register_callbacks import _perform_authentication
            import threading

            def run_oauth():
                try:
                    _perform_authentication()
                except Exception as e:
                    from ticca.messaging import emit_error
                    emit_error(f"OAuth authentication failed: {str(e)}")

            oauth_thread = threading.Thread(target=run_oauth, daemon=True)
            oauth_thread.start()

        except ImportError:
            from ticca.messaging import emit_error
            emit_error("Claude Code OAuth plugin not available.")
        except Exception as e:
            from ticca.messaging import emit_error
            emit_error(f"Failed to start OAuth: {str(e)}")

    @on(Button.Pressed, "#chatgpt-auth-button")
    def handle_chatgpt_auth(self) -> None:
        """Handle ChatGPT OAuth authentication."""
        try:
            from ticca.plugins.chatgpt_oauth.oauth_flow import run_oauth_flow
            import threading

            def run_oauth():
                try:
                    run_oauth_flow()
                except Exception as e:
                    from ticca.messaging import emit_error
                    emit_error(f"ChatGPT OAuth authentication failed: {str(e)}")

            oauth_thread = threading.Thread(target=run_oauth, daemon=True)
            oauth_thread.start()

        except ImportError:
            from ticca.messaging import emit_error
            emit_error("ChatGPT OAuth plugin not available.")
        except Exception as e:
            from ticca.messaging import emit_error
            emit_error(f"Failed to start ChatGPT OAuth: {str(e)}")

    def on_key(self, event) -> None:
        """Handle key events."""
        if event.key == "escape":
            self.cancel_settings()
