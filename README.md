# Ticca: Terminal Injected Coding CLI Assistant ⚡

A powerful AI-powered coding assistant that runs entirely in your terminal. Ticca combines specialized agents, browser automation, and advanced tooling to help you write, test, and deploy code faster.

## ✨ Key Features

- **🤖 Multi-Agent System**: Specialized agents for different programming languages, security auditing, QA, and planning
- **🌐 Browser Automation**: Full Playwright-based control for web scraping, testing, and automation
- **📊 AI Model Flexibility**: Support for OpenAI GPT-5, Claude 4.x, Cerebras, and custom model endpoints
- **🖥️ Dual Interface**: Both interactive TUI (Textual) and simple CLI modes
- **🔧 Rich Tooling**: File operations, shell commands, code search with ripgrep, and agent collaboration
- **📝 Session Persistence**: Autosave/restore conversations with hybrid storage
- **🔌 Plugin Architecture**: Extensible system with OAuth integrations and custom commands

## 🚀 Quick Start

### Installation

```bash
# Clone the repository
git clone https://github.com/janfeddersen-wq/ticca.git
cd ticca

# Install dependencies (recommended)
uv sync

# Or traditional installation
pip install -e .
```

### Basic Usage

```bash
# Start with TUI interface (recommended)
uv run ticca

# Or use the launcher script
./start.sh

# Quick CLI mode
uv run ticca --no-tui
```

## 🎯 Core Capabilities

### Agent System
```bash
# Switch between specialized agents
/agent code-reviewer
/agent security-auditor 
/agent python-programmer
/agent planning

# Available agents:
# - Code-Puppy (default)
# - Code Reviewer
# - Security Auditor
# - Python Programmer
# - Planning Agent
```

### Browser Automation
```bash
# Browser setup
/browser_initialize
/browser_navigate https://github.com

# Interact with elements
/browser_find_by_text "Repository"
/browser_click
/browser_screenshot_analyze
```

### File Operations
```bash
# Code search and analysis
/list_files --recursive
/grep "TODO" --directory src/
/read_file main.py
/edit_file
```

### Agent Collaboration
```bash
# Delegate to specialists
/invoke_agent security-auditor "Review authentication code"
/list_agents
```

## 🔧 Configuration

Ticca stores configuration in `~/.ticca/`:

```bash
# Set your preferences
/set owner_name "Your Name"
/model gpt-5

# Available models include:
# - OpenAI: gpt-5, gpt-5-codex-api
# - Anthropic: claude-4-0-sonnet, claude-4-5-sonnet, claude-4-1-opus
# - Cerebras: Multiple GLM and Qwen variants
# - Custom: Synthetic API endpoints
```

## 🔌 Extensions

### MCP Server Support
```bash
# Model Context Protocol integration
/mcp install <server-name>
/mcp start <server-name>
/mcp status
/mcp logs
```

### OAuth Plugins
```bash
# Claude Code integration
/claude-code-auth
/claude-code-status
```

## 📊 Session Management

```bash
# Save and resume work
/session save my-project
/session restore my-project

# Autosave is enabled by default
# Sessions stored in ~/.ticca/autosaves/
```

## 🛠️ Development

```bash
# Install development dependencies
uv sync --group dev

# Run tests
pytest

# Code formatting
ruff format
ruff check --fix

# Git hooks
lefthook install
```

## 🎯 Use Cases

### API Development
```
/agent python-programmer
Create a FastAPI application with authentication and CRUD operations
```

### Web Testing
```
/browser_initialize
/browser_navigate https://myapp.com
/browser_find_by_label "Username"
/browser_set_text test@example.com
/browser_click_by_text "Login"
```

### Code Review
```
/invoke-agent security-auditor
Review this code for vulnerabilities:

[paste code or upload file]
```

## 📄 License

MIT License - see [LICENSE](LICENSE) for details.

---

**Ticca** - Your loyal coding companion in the terminal! 🐶✨