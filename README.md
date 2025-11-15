# Ticca - Terminal Injected Coding CLI Assistant ⚡

[![Python](https://img.shields.io/badge/Python-3.11+-blue.svg)](https://python.org)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Tests](https://img.shields.io/badge/Tests-Pass-brightgreen.svg)](tests/)

Ticca is a powerful, terminal-based AI coding assistant that brings intelligent development capabilities directly to your command line. With support for multiple AI agents, browser automation, file operations, and seamless integration with various LLM providers, Ticca transforms your terminal into an intelligent development environment.

## ✨ Features

### 🤖 Multi-Agent System
- **Code Puppy** - Specialized code generation and modification agent
- **Code Reviewers** - Language-specific reviewers (Python, JavaScript, TypeScript, C++, Go, C)
- **Security Auditor** - Automated security analysis and vulnerability detection
- **Planning Agent** - Strategic project planning and architecture design
- **Custom Agents** - Extensible JSON-based agent configuration system

### 🌐 Browser Automation
- **Web Interaction** - Click, type, navigate, and extract data from web pages
- **Visual QA** - Screenshot capture and AI-powered visual analysis
- **Workflow Recording** - Record and replay browser automation sequences
- **Multiple Locators** - Find elements by role, text, label, XPath, and more

### 💻 Development Tools
- **File Operations** - Read, write, edit, and search files with intelligent diff generation
- **Command Execution** - Safe shell command execution with confirmation prompts
- **Session Management** - Auto-save and restore conversation states
- **Command History** - Persistent command history with search capabilities

### 🎨 Terminal User Interface
- **Modern TUI** - Rich terminal interface built with Textual
- **Real-time Chat** - Interactive conversation with AI agents
- **File Browser** - Navigate and explore project structure
- **Configuration Panels** - Interactive settings and model selection

### 🔌 Model Support
- **Multiple Providers** - OpenAI, Anthropic, Cerebras, and custom endpoints
- **Advanced Models** - GPT-5, Claude 4.x, GLM-4.6, DeepSeek, and more
- **Flexible Configuration** - Easy model switching and per-agent model pinning
- **Context Management** - Intelligent message history compression

### 🔧 MCP Integration
- **Server Management** - Built-in MCP server lifecycle management
- **Status Monitoring** - Real-time server health tracking
- **Configuration Wizard** - Interactive server setup and discovery
- **Error Recovery** - Automatic retry and circuit breaker patterns

## 🚀 Installation

### Prerequisites
- Python 3.11 or higher
- UV (recommended) or pip package manager

### Quick Install
```bash
# Install with UV (recommended)
pip install uv
uv add ticca

# Or install with pip
pip install ticca
```

### Development Install
```bash
git clone https://github.com/janfeddersen-wq/ticca.git
cd ticca
uv sync
```

## 🎯 Quick Start

### Launch Ticca
```bash
# Start with TUI interface (recommended)
ticca

# Or use the short command
tic

# Start with performance profiling
./start.sh

# Start without profiling
./start.sh --no-profile
```

### Basic Usage
```bash
# Chat with the default Code Puppy agent
ticca "Write a Python function to process JSON data"

# Use a specific agent
ticca --agent security-auditor "Review this code for vulnerabilities"

# Enable TUI mode for interactive sessions
ticca --tui

# Execute with a specific model
ticca --model claude-4-5-sonnet "Analyze this React component"
```

## ⚙️ Configuration

Ticca stores configuration in `~/.ticca/`:

### Main Configuration (`~/.ticca/puppy.cfg`)
```ini
[default]
model = claude-4-5-sonnet
enable_tui = true
enable_dbos = false
enable_mcp = true

[agents]
code_puppy = code-agent
security = security-auditor
planning = planning-agent
```

### Model Configuration (`~/.ticca/models.json`)
```json
{
  "claude-4-5-sonnet": {
    "type": "anthropic",
    "name": "claude-sonnet-4-5-20250929",
    "context_length": 200000
  },
  "gpt-5": {
    "type": "openai", 
    "name": "gpt-5",
    "context_length": 272000
  }
}
```

### Environment Variables
```bash
# API Keys
export OPENAI_API_KEY="your-openai-key"
export ANTHROPIC_API_KEY="your-anthropic-key"
export CEREBRAS_API_KEY="your-cerebras-key"

# Optional
export TICCA_PROFILE=1          # Enable performance profiling
export DBOS_SYSTEM_DATABASE_URL="postgresql://..."  # DBOS database
```

## 🛠️ Available Agents

| Agent | Description | Specialization |
|-------|-------------|----------------|
| `code-agent` | Code Puppy | General code generation and modification |
| `security-auditor` | Security Expert | Vulnerability detection and security analysis |
| `planning-agent` | Project Planner | Architecture design and planning |
| `code-reviewer` | Code Reviewer | General code review and quality analysis |
| `python-reviewer` | Python Specialist | Python-specific code review |
| `javascript-reviewer` | JavaScript Specialist | JavaScript/TypeScript review |
| `cpp-reviewer` | C++ Specialist | C++ code review and optimization |

## 🌐 Browser Automation

Ticca includes powerful browser automation capabilities:

```python
# Initialize browser (in TUI mode or via commands)
browser_initialize()
browser_navigate("https://example.com")
browser_find_by_text("Submit")
browser_click(element)
browser_take_screenshot_and_analyze("What's on this page?")
```

### Supported Browsers
- Chromium (via Playwright)
- Firefox (via Camoufox)
- Headless and headed modes

## 🧪 Testing

```bash
# Run all tests
uv run pytest

# Run with coverage
uv run pytest --cov=ticca --cov-report=term-missing

# Run specific test categories
uv run pytest tests/unit/
uv run pytest tests/integration/
uv run pytest tests/tools/
```

## 🔌 Plugin System

Ticca supports extensible plugins:

### Available Plugins
- **OAuth Authentication** - ChatGPT and Claude Code OAuth
- **Custom Commands** - Define your own meta-commands
- **File Permissions** - Advanced file permission handling
- **Git Integration** - Enhanced Git workflow automation

### Creating Custom Plugins

```python
# ~/.ticca/plugins/my_plugin.py
def register_callbacks():
    """Register plugin callbacks."""
    # Add your plugin initialization here
    pass
```

## 📊 Performance

Ticca includes built-in performance profiling:

```bash
# Enable profiling
export TICCA_PROFILE=1

# View performance report
cat ~/.ticca/perf_report.txt
```

### Optimization Features
- Intelligent message history compression
- Lazy loading of heavy components
- Efficient token usage monitoring
- Session auto-save and restore

## 🤝 Contributing

We welcome contributions! Please see our [Contributing Guide](CONTRIBUTING.md) for details.

### Development Workflow
```bash
# Clone and setup
git clone https://github.com/janfeddersen-wq/ticca.git
cd ticca
uv sync

# Run linting and formatting
ruff check --fix
ruff format .

# Run tests before committing
uv run pytest

# Check everything works
pnpm check  # or git pre-commit hook
```

### Code Style Guidelines
- Follow DRY, YAGNI, SOLID principles
- Keep files under 600 lines
- Use type hints everywhere
- Write comprehensive tests
- Use ruff for linting and formatting

## 📚 Documentation

- [Agents Guide](docs/AGENTS.md) - Detailed agent documentation
- [Environment Variables](docs/ENVIRONMENT_VARIABLES.md) - Configuration options
- [Performance Guide](docs/PERFORMANCE.md) - Performance optimization
- [MCP Integration](docs/MCP.md) - Model Context Protocol setup
- [Browser Automation](docs/BROWSER.md) - Web automation examples

## 🔧 Troubleshooting

### Common Issues

**Q: Ticca can't find my API keys**
```bash
# Ensure environment variables are set
echo $OPENAI_API_KEY
echo $ANTHROPIC_API_KEY

# Or set them in puppy.cfg
[api_keys]
openai = sk-...
anthropic = sk-ant-...
```

**Q: Browser automation isn't working**
```bash
# Install required browsers
playwright install
playwright install-deps

# Or use camoufox
pip install camoufox
```

**Q: TUI mode crashes**
```bash
# Try CLI mode
ticca --no-tui

# Check terminal compatibility
ticca --help
```

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- Built with [Pydantic AI](https://pydantic-ai.com/) for agent management
- TUI powered by [Textual](https://textual.textual.io/)
- Browser automation via [Playwright](https://playwright.dev/) and [Camoufox](https://camoufox.org/)
- Model integration with [DBOS](https://www.dbos.dev/) for persistence

## 📞 Support

- 📖 [Documentation](docs/)
- 🐛 [Issue Tracker](https://github.com/janfeddersen-wq/ticca/issues)
- 💬 [Discussions](https://github.com/janfeddersen-wq/ticca/discussions)

---

**Ticca** - Making your terminal smarter, one command at a time! 🚀