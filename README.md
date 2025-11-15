# Ticca ⚡

[![Python](https://img.shields.io/badge/Python-3.11+-blue.svg)](https://python.org)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Version](https://img.shields.io/badge/Version-0.1.4-orange.svg)](https://github.com/janfeddersen-wq/ticca)

**Terminal Injected Coding CLI Assistant** - A powerful, extensible coding assistant with terminal UI and web interface.

## ✨ Features

- 🖥️ **Rich Terminal UI** - Beautiful, responsive interface built with Textual
- 🌐 **Web Interface** - Browser-based access to the same functionality
- 🤖 **Multiple AI Agents** - Specialized agents for coding, planning, security, and code review
- 📁 **File Operations** - Read, edit, search, and manage files with intelligent diff generation
- 🔧 **Tool Integration** - Shell command execution, browser automation, and more
- 🔌 **Plugin System** - Extensible architecture with OAuth and custom command support
- 💾 **Session Management** - Auto-save, session restoration, and conversation history
- 🎨 **Theming** - Customizable themes and visual settings
- 📊 **Performance Profiling** - Built-in performance monitoring and optimization tools
- 🔄 **MCP Support** - Model Control Protocol server management and integration

## 🚀 Quick Start

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

### Configuration

1. **Set up API keys** - Copy `.env.example` to `.env` and configure your preferred AI provider:

```bash
cp .env.example .env
# Edit .env with your API keys
```

Supported providers:
- OpenAI (GPT models)
- Anthropic (Claude)
- Google Gemini
- Azure OpenAI
- Custom OpenAI-compatible APIs

2. **Optional: Configure global settings** in `~/.ticca/puppy.cfg`

### Run Ticca

```bash
# Start with TUI (recommended)
./start.sh

# Or directly
ticca

# Web interface
ticca --web

# With specific model or agent
ticca --model gpt-4 --agent code-agent
```

## 🎯 Usage Examples

### Basic File Operations

```
# List project files
> List all Python files in the src directory

# Read and analyze code
> Read the main.py file and explain what it does

# Edit files with approval workflow
> Add error handling to the data processing function in utils.py
```

### Code Generation

```
# Create new components
> Generate a React component for a user profile page with TypeScript

# Add features
> Implement pagination for the API endpoint in routes.py

# Refactor code
> Refactor the database query to use an ORM pattern
```

### Shell Command Execution

```
# Run tests
> Run pytest and show me any failing tests

# Build project
> Build the Docker image and push to registry

# Install dependencies
> Install the missing packages from requirements.txt
```

### Browser Automation

```
# Web testing
> Open the login page and test the authentication flow

# Screenshots
> Take a screenshot of the dashboard and save as dashboard.png

# Form interactions
> Fill out the contact form and verify submission
```

## 🏗️ Architecture

### Agent System

Ticca includes specialized agents for different tasks:

- **`code-agent`** - General coding and development tasks
- **`planning-agent`** - Project planning and architecture design
- **`security-auditor`** - Security analysis and vulnerability detection
- **`code-reviewer`** - Code review and quality assessment
- **`json-agent`** - JSON processing and validation

### Tool System

Powerful built-in tools for common development tasks:

- **File Operations** - List, read, edit, search files with intelligent filtering
- **Command Runner** - Execute shell commands with real-time output and cancellation
- **Browser Automation** - Control browsers with Playwright and Camoufox
- **Human Feedback** - Interactive prompts for user decisions
- **Agent Tools** - Delegate tasks to specialized agents

### Plugin System

Extend Ticca with custom plugins:

- **OAuth Providers** - ChatGPT, Claude Code authentication
- **Custom Commands** - Add domain-specific commands
- **Theme Extensions** - Create custom visual themes
- **File Handlers** - Specialized file type processors

## ⚙️ Configuration

### Model Configuration

Edit `ticca/models.json` to add or configure AI models:

```json
{
  "custom-model": {
    "type": "custom_openai",
    "name": "gpt-4o",
    "custom_endpoint": {
      "url": "https://api.your-provider.com/v1/",
      "api_key": "$YOUR_API_KEY"
    },
    "context_length": 128000
  }
}
```

### Environment Variables

Create `.env` file for API keys and settings:

```bash
# Primary AI provider
OPENAI_API_KEY=sk-your-openai-key
ANTHROPIC_API_KEY=sk-your-anthropic-key

# Optional providers
GEMINI_API_KEY=your-gemini-key
CEREBRAS_API_KEY=your-cerebras-key

# Feature flags
TICCA_PROFILE=1          # Enable performance profiling
TICCA_WEB_HOST=0.0.0.0   # Web interface host
```

### Session Settings

Configure in `~/.ticca/puppy.cfg`:

```ini
[general]
default_model = gpt-4o
default_agent = code-agent
tui_theme = dark
auto_save = true

[limits]
message_limit = 50
context_length = 128000
```

## 🎨 Themes

Customize the appearance with built-in or custom themes:

```
# Switch themes
/theme dark
/theme light
/theme custom

# Configure colors
/theme --accent cyan
/theme --background rgb(20,20,30)
```

## 📊 Performance Profiling

Enable profiling to identify optimization opportunities:

```bash
# With profiling enabled
./start.sh
# Performance report saved to ~/.ticca/perf_report.txt

# Or via environment variable
TICCA_PROFILE=1 ticca
```

## 🔧 Development

### Setup Development Environment

```bash
# Clone repository
git clone https://github.com/janfeddersen-wq/ticca.git
cd ticca

# Install development dependencies
uv sync --dev

# Set up pre-commit hooks
pre-commit install
```

### Code Quality

```bash
# Run linting and formatting
ruff check --fix
ruff format .

# Run tests
uv run pytest --cov=ticca

# Check with pnpm (if applicable)
pnpm check
```

### Project Structure

```
ticca/
├── agents/           # AI agent implementations
├── command_line/     # CLI command handling
├── messaging/        # Message rendering and queues
├── tools/           # File, shell, browser tools
├── tui/             # Terminal user interface
├── plugins/         # Plugin system
├── mcp_/            # MCP server management
├── themes/          # Theme system
└── config.py        # Configuration management
```

### Adding Plugins

1. Create a new directory in `plugins/`
2. Implement the plugin interface
3. Register callbacks

```python
# plugins/my_plugin/register_callbacks.py
from ticca import callbacks

@callbacks.on_startup
async def my_startup_callback():
    # Plugin initialization
    pass
```

## 🤝 Contributing

We welcome contributions! Please follow these guidelines:

1. **Fork** the repository
2. **Create** a feature branch (`git checkout -b feature/amazing-feature`)
3. **Commit** your changes (`git commit -m 'Add amazing feature'`)
4. **Push** to the branch (`git push origin feature/amazing-feature`)
5. **Open** a Pull Request

### Code Standards

- Follow PEP 8 style guidelines
- Use type hints on all functions
- Keep files under 600 lines
- Apply DRY, YAGNI, SOLID principles
- Add tests for new features
- Update documentation

### Testing

```bash
# Run all tests
uv run pytest

# Run with coverage
uv run pytest --cov=ticca --cov-report=html

# Run specific test file
uv run pytest tests/test_file_operations.py
```

## 📚 Documentation

- **[DEV_CONSOLE.md](DEV_CONSOLE.md)** - Console development details
- **[AGENTS.md](AGENTS.md)** - Agent system documentation
- **[ENVIRONMENT_VARIABLES.md](ENVIRONMENT_VARIABLES.md)** - Configuration reference
- **[PERFORMANCE.md](PERFORMANCE.md)** - Performance profiling guide
- **[HYBRID_STORAGE.md](HYBRID_STORAGE.md)** - Storage system architecture

## 🆘 Troubleshooting

### Common Issues

**Models not available:**
- Check API keys in `.env`
- Verify model configuration in `models.json`
- Run `/models` command to list available models

**UI not loading:**
- Install textual: `pip install textual[syntax]`
- Check Python version (3.11+ required)
- Verify terminal supports TUI features

**Plugin errors:**
- Check plugin configuration in `puppy.cfg`
- Review plugin logs in `~/.ticca/logs/`
- Disable problematic plugins temporarily

### Getting Help

- Use `/help` command in Ticca
- Check issue tracker for known problems
- Create bug report with system information

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- [Pydantic AI](https://github.com/pydantic/pydantic-ai) - AI agent framework
- [Textual](https://github.com/Textualize/textual) - TUI framework
- [Rich](https://github.com/Textualize/rich) - Rich terminal output
- All contributors and users who make Ticca better!