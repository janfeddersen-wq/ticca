# Ticca - Terminal Injected Coding CLI Assistant

**Ticca** is a sophisticated AI-powered coding assistant that runs directly in your terminal. It combines the power of multiple AI models with advanced browser automation, file operations, and a rich terminal user interface to provide an unparalleled development experience.

## Features

### AI-Powered Development
- **Multiple Model Support**: OpenAI GPT models, custom endpoints, and synthetic models
- **Specialized Agents**: Code reviewer, security auditor, planner, and more
- **Context Management**: Intelligent message history with summarization
- **Vision Capabilities**: Image analysis and screenshot interpretation

### Dual Interface Modes
- **CLI Mode**: Fast, efficient command-line interaction
- **TUI Mode**: Rich terminal interface with split views, modals, and interactive components

### Advanced Tooling
- **Browser Automation**: Built-in Playwright/Camoufox support for web interactions
- **File Operations**: Smart reading, writing, and search with diff generation
- **Command Execution**: Safe shell command execution with monitoring
- **Session Management**: Autosave/resume with SQLite/DBOS persistence

### Extensible Architecture
- **Plugin System**: OAuth integration, custom commands, and file permission handling
- **MCP Server Support**: Model Context Protocol server management
- **Customizable Themes**: rich terminal UI themes and styling
- **Agent Framework**: Easy-to-extend base agent system

## Quick Start

### Installation

```bash
# Clone the repository
git clone https://github.com/janfeddersen-wq/ticca.git
cd ticca

# Install with UV (recommended)
uv sync

# Or with pip
pip install -e .
```

### Basic Usage

```bash
# Start with the launcher script (recommended)
./start.sh

# Or start directly
uv run ticca

# Short alias also works
uv run tic
```

First run will initialize configuration in `~/.ticca/` and prompt for AI model selection.

## Usage Guide

### CLI Mode

```bash
# Basic interaction
ticca "Write a Python function to sort a list"

# File operations
ticca "Review the code in src/main.py and suggest improvements"

# Browser automation
ticca "Take a screenshot of https://example.com and analyze it"

# Use specific agent
ticca --agent security-reviewer "Audit the authentication code"
```

### TUI Mode

The TUI provides a rich interface with:
- **Split View**: Chat interface and file browser side-by-side
- **Command History**: Easy access to previous commands
- **Session Management**: Save and restore conversations
- **Interactive Modals**: File editor, image viewer, approval dialogs

Key TUI shortcuts:
- `Ctrl+C`: Exit current operation
- `Ctrl+S`: Save session
- `Ctrl+H`: Show command history
- `Tab`: Auto-completion for files and commands
- `@`: Trigger file path completion
- `/`: Access model picker

## Configuration

Configuration is stored in `~/.ticca/puppy.cfg`:

```ini
[puppy]
# AI Model (gpt-4, gpt-4-turbo, claude-3-sonnet, etc.)
model = gpt-4

# Enable DBOS for advanced session management
enable_dbos = true

# Message history settings
message_limit = 100
compaction_threshold = 50

# Browser automation
browser_timeout = 30
screenshot_quality = high
```

### Environment Variables

```bash
# OpenAI API key
export OPENAI_API_KEY="your-api-key-here"

# Custom model endpoints
export SYN_API_KEY="your-synthetic-api-key"

# Browser automation
export PLAYWRIGHT_BROWSERS_PATH="/path/to/browsers"
```

## Available Agents

| Agent | Purpose |
|-------|---------|
| `code-agent` | General code generation and assistance |
| `code-reviewer` | Code quality and best practices review |
| `security-auditor` | Security vulnerability assessment |
| `planning` | Project architecture and planning |
| `python-programmer` | Python-specific development |

## Plugin System

### Built-in Plugins

1. **OAuth Integration**
   - ChatGPT OAuth flow
   - Claude Code OAuth support

2. **File Permission Handler**
   - Automatic permission fixes for file operations
   - Permission validation and recovery

3. **Custom Commands**
   - Extensible command registry
   - User-defined command shortcuts

### Creating Custom Plugins

```python
# ~/.ticca/plugins/my_plugin.py
from ticca.plugins import register_callback

@register_callback("before_file_edit")
def my_edit_handler(file_path, content):
    # Custom logic before file editing
    return modified_content
```

## Browser Automation

Ticca includes powerful browser automation capabilities:

```bash
# Navigate and interact
ticca "Go to https://github.com and search for 'ticca'"

# Take screenshots and analyze
ticca "Screenshot the dashboard and identify any errors"

# Form interactions
ticca "Fill out the login form with test credentials"

# Element interactions
ticca "Click the submit button and wait for the response"
```

## Architecture Overview

```
ticca/
├── agents/           # AI agent implementations
├── command_line/     # CLI interface and commands
├── mcp_/            # Model Context Protocol server management
├── plugins/         # Plugin system and built-in plugins
├── tools/           # Core tools (file, browser, command runners)
├── tui/             # Terminal User Interface components
└── messaging/       # Message handling and rendering
```

### Core Components

- **BaseAgent**: Foundation for all AI agents with tool registration
- **ConfigManager**: Centralized configuration with validation
- **SessionStorage**: Persistent conversation management
- **MCPManager**: External service integration via MCP protocol
- **TUIApp**: Rich terminal interface built with Textual

## Development

### Running Tests

```bash
# Run all tests
uv run pytest

# Run with coverage
uv run pytest --cov=ticca --cov-report=term-missing

# Run specific test file
uv run pytest tests/test_config.py
```

### Code Quality

```bash
# Format code
uv run ruff format .

# Check linting
uv run ruff check

# Fix linting issues
uv run ruff check --fix
```

### Performance Profiling

```bash
# Enable profiling
export TICCA_PROFILE=1
./start.sh

# View performance report
cat ~/.ticca/perf_report.txt
```

## Advanced Features

### Session Management

- **Autosave**: Automatic session saving every N messages
- **Resume**: Restore previous conversations with `ticca --resume`
- **Backup**: Export/import sessions for sharing

### Multi-Model Support

Configure multiple models in `~/.ticca/models.json`:

```json
{
  "custom-model": {
    "type": "custom_openai",
    "name": "my-custom-model",
    "custom_endpoint": {
      "url": "https://api.example.com/v1/",
      "api_key": "$MY_API_KEY"
    },
    "context_length": 100000
  }
}
```

### File Operations with Diffs

All file modifications generate diffs automatically:

```bash
ticca "Add error handling to process_data.py"
# Shows diff before applying changes
```

## Contributing

We welcome contributions! Please see our development guidelines:

1. Fork the repository
2. Create a feature branch
3. Make your changes with tests
4. Run `uv run ruff check && uv run pytest`
5. Submit a pull request

### Git Workflow

```bash
# Always run before committing
pnpm check  # or equivalent local checks

# Fix issues
ruff check --fix
ruff format .

# Never force push to main
git push --force-with-lease  # Use this instead if needed
```

## License

MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

Built with:
- [pydantic-ai](https://github.com/pydantic-ai/pydantic-ai) - AI agent framework
- [Rich](https://github.com/Textualize/rich) - Terminal formatting
- [Textual](https://github.com/Textualize/textual) - TUI framework
- [Playwright](https://playwright.dev/) - Browser automation

## Additional Documentation

- [Agent Configuration](ticca/AGENTS.md) - Custom agent setup
- [Performance Guide](ticca/PERFORMANCE.md) - Optimization tips
- [Environment Variables](ticca/ENVIRONMENT_VARIABLES.md) - All configuration options
- [MCP Integration](ticca/HYBRID_STORAGE.md) - External service integration

---

**Ticca** - Making terminal development intelligent, interactive, and inspiring.