# Ticca - Terminal Injected Coding CLI Assistant ⚡

A powerful AI-powered coding assistant that runs directly in your terminal. Ticca combines the convenience of a CLI tool with the intelligence of multiple LLM models, featuring a rich text-based user interface, extensive file management capabilities, browser automation, and extensible plugin architecture.

![Ticca](https://img.shields.io/badge/Ticca-0.1.4-blue)
![Python](https://img.shields.io/badge/Python-3.11+-green)
![License](https://img.shields.io/badge/License-MIT-yellow)

## ✨ Key Features

- 🤖 **Multi-Agent System**: Specialized agents for code review, security auditing, planning, and more
- 🖥️ **Rich TUI Interface**: Modern terminal UI built with Textual framework
- 📁 **Full File Management**: Read, edit, search, and manage files with intelligent approval system
- 🌐 **Browser Automation**: Built-in Playwright/Camoufox integration for web interaction testing
- 🔌 **Plugin Architecture**: Extensible system for OAuth providers, custom commands, and more
- 💾 **Session Management**: Autosave and resume your work sessions
- 🔄 **MCP Integration**: Model Context Protocol support for extending functionality
- 📊 **Performance Monitoring**: Built-in profiling and performance tracking
- 🛠️ **Dev Tools Integration**: Git hooks, linting, formatting with ruff
- 🔐 **Secure Operations**: Approval system for file modifications and command execution

## 🚀 Quick Start

### Prerequisites

- Python 3.11, 3.12, or 3.13
- UV (recommended) or pip

### Installation

#### Option 1: Using UV (Recommended)
```bash
# Clone the repository
git clone https://github.com/janfeddersen-wq/ticca.git
cd ticca

# Install dependencies
uv sync

# Run Ticca
uv run ticca
```

#### Option 2: Alternative Methods
```bash
# Using the provided launcher script (with profiling)
./start.sh

# Or directly with Python
python -m ticca

# If installed as a package
ticca
```

### First Run

1. Launch Ticca using one of the methods above
2. Follow the setup wizard to configure your preferred AI model
3. Start chatting with the AI assistant!

## 🛠️ Core Capabilities

### File Operations
```bash
# List files with intelligent filtering
@ls

# Read file contents
@read path/to/file.py

# Search across files
@grep "function_name" --type python

# Edit files with approval workflow
@edit path/to/file.py --start-line 10 --num-lines 5
```

### Shell Commands
```bash
# Run commands with approval
!ls -la
!git status
!python -m pytest
```

### Browser Automation
```bash
# Initialize browser
/browser_initialize

# Navigate to a URL
/browser_navigate https://example.com

# Find and interact with elements
/browser_find_by_text "Submit"
/browser_click element_id

# Take screenshots
/browser_screenshot_analyze
```

### Agent System
```bash
# List available agents
/list_agents

# Switch to specialized agent
/invoke_agent code_reviewer

# Get security audit
/invoke_agent security_auditor
```

## ⚙️ Configuration

### Model Configuration
Ticca supports multiple AI models through the `models.json` configuration:

- OpenAI models (GPT-4, GPT-4o, o1, etc.)
- Custom OpenAI-compatible endpoints
- Local models via Ollama
- Specialized reasoning models

### Environment Variables
Key environment variables for configuration:

```bash
# API Keys
export OPENAI_API_KEY="your-key-here"
export ANTHROPIC_API_KEY="your-key-here"

# Performance
export TICCA_PROFILE=1  # Enable profiling

# Database (optional)
export DBOS_DATABASE_URL="sqlite:///ticca.db"
```

### Session Settings
Configure session behavior, auto-save intervals, model preferences, and UI themes through the settings interface.

## 🔌 Plugin Development

Ticca's plugin system allows you to extend functionality:

### OAuth Plugins
Add support for new AI providers:
```python
# plugins/my_provider/oauth_flow.py
def register_oauth_provider():
    # Implementation
    pass
```

### Custom Commands
Create custom commands:
```python
# plugins/custom_commands/register_callbacks.py
from ticca.command_line import register_command

@register_command("my_command")
def handle_my_command(args):
    # Implementation
    pass
```

### File Handlers
Add custom file permission handlers:
```python
# plugins/file_handler/register_callbacks.py
def custom_permission_handler(file_path, operation):
    # Implementation
    return True  # or False
```

## 🏗️ Architecture

### Core Components

- **`ticca/agents/`**: Agent system with base classes and specialized implementations
- **`ticca/tools/`**: Extensive tool library for file operations, shell commands, browser automation
- **`ticca/tui/`**: Textual-based terminal user interface
- **`ticca/mcp_/`**: Model Context Protocol server management
- **`ticca/plugins/`**: Plugin architecture and built-in plugins
- **`ticca/config.py`**: Configuration management system

### Agent System
Ticca uses a sophisticated multi-agent architecture:
- **BaseAgent**: Core functionality with tool registration, message management
- **Specialized Agents**: CodeReviewer, SecurityAuditor, PlanningAgent, etc.
- **Agent Manager**: Coordinates agent switching and lifecycle

### Tool System
Modular tool registration system supporting:
- File operations (read, write, search, modify)
- Shell command execution with approval
- Browser automation via Playwright/Camoufox
- Agent invocation and management
- Human feedback collection

## 🧪 Testing

### Run Tests
```bash
# Run all tests
uv run pytest

# Run with coverage
uv run pytest --cov=ticca

# Run specific test file
uv run pytest tests/test_file_operations.py
```

### Integration Tests
```bash
# Run CLI integration tests
uv run pytest tests/integration/

# Run smoke tests
uv run pytest tests/integration/test_smoke.py
```

## 🎯 Development Workflow

### Code Quality
```bash
# Check code formatting and linting
pnpm check

# Auto-fix issues
ruff check --fix

# Format code
ruff format .
```

### Git Hooks
Ticca uses lefthook for pre-commit hooks:
- Code formatting with ruff
- Linting checks
- Test execution on commits

### Performance Profiling
```bash
# Enable profiling
export TICCA_PROFILE=1

# Run with profiling
./start.sh

# View performance report
cat ~/.ticca/perf_report.txt
```

## 📚 Advanced Usage

### MCP Servers
Extend Ticca with custom MCP servers:
```bash
# Install an MCP server
/mcp install my-mcp-server

# List installed servers
/mcp list

# Start/stop servers
/mcp start my-mcp-server
/mcp stop my-mcp-server
```

### Session Management
```bash
# Save current session
/session save my-session

# List saved sessions
/session list

# Resume session
/session resume my-session
```

### Custom Workflows
Create browser automation workflows:
```python
# Save browser interaction sequence
/browser_save_workflow my_workflow

# List workflows
/browser_list_workflows

# Execute workflow
/browser_read_workflow my_workflow
```

## 🐛 Troubleshooting

### Common Issues

1. **Import Errors**: Ensure all dependencies are installed with `uv sync`
2. **Permission Errors**: Check file permissions in your working directory
3. **Model Connection**: Verify API keys and network connectivity
4. **Browser Issues**: Ensure Playwright browsers are installed (`playwright install`)

### Debug Mode
```bash
# Enable debug logging
export TICCA_DEBUG=1

# Run with debug output
ticca --debug
```

### Performance Issues
1. Enable profiling with `TICCA_PROFILE=1`
2. Check the performance report at `~/.ticca/perf_report.txt`
3. Consider increasing model context limits for large files

## 🤝 Contributing

We welcome contributions! Please follow these steps:

1. Fork the repository
2. Create a feature branch: `git checkout -b feature-name`
3. Make your changes and ensure tests pass
4. Run code quality checks: `pnpm check`
5. Submit a pull request

### Development Setup
```bash
# Clone your fork
git clone https://github.com/yourusername/ticca.git
cd ticca

# Install in development mode
uv sync --dev

# Run tests
uv run pytest
```

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- Built with [pydantic-ai](https://github.com/pydantic-ai/pydantic-ai) for AI agent management
- UI powered by [Textual](https://github.com/Textualize/textual)
- Browser automation via [Playwright](https://playwright.dev/)
- Performance tracking with [DBOS](https://www.dbos.dev/)
- Code quality with [Ruff](https://github.com/astral-sh/ruff)

## 📞 Support

- 📖 [Documentation](https://github.com/janfeddersen-wq/ticca)
- 🐛 [Issue Tracker](https://github.com/janfeddersen-wq/ticca/issues)
- 💬 [Discussions](https://github.com/janfeddersen-wq/ticca/discussions)

---

**Ticca** - Your terminal-embedded coding companion. 🐶✨