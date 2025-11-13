# Ticca

**Terminal Injected Coding CLI Assistant** - A professional AI-powered coding assistant for your terminal. Built for developers who value efficiency and privacy.

[![License](https://img.shields.io/badge/License-MIT-green?style=for-the-badge)](LICENSE)
[![Python](https://img.shields.io/badge/Python-3.11%2B-blue?style=for-the-badge&logo=python&logoColor=white)](https://python.org)

## Features

- **TUI by Default**: Beautiful terminal UI powered by Textual
- **Multi-Model Support**: OpenAI, Anthropic Claude, Google Gemini, Cerebras, Ollama, and more
- **MCP Servers**: Extend capabilities with Model Context Protocol
- **Specialized Agents**: Task-specific AI agents for coding
- **Load Balancing**: Round-robin distribution across multiple API keys
- **100% Private**: No telemetry, no tracking—your code stays yours
- **Durable Execution**: Optional DBOS integration for workflow recovery

## Quick Start

```bash
uvx ticca          # Recommended (requires UV)
pip install ticca  # Or use pip
ticca              # Start TUI mode
```

## Configuration

Set API keys as environment variables:

```bash
export OPENAI_API_KEY=<key>
export ANTHROPIC_API_KEY=<key>
export GEMINI_API_KEY=<key>
```

Or configure via TUI settings menu. Models are configured in `~/.ticca/models.json`.

## Commands

```bash
ticca              # Start TUI mode (default)
ticca -i           # Interactive CLI mode
ticca -w           # Web interface
ticca -p "prompt"  # Execute single prompt and exit
ticca -m model     # Specify model
ticca -a agent     # Specify agent

/agent <name>      # Switch agent
/mcp list          # List MCP servers
/set <key> <val>   # Configure settings
```

## Custom Commands

Create markdown files in `.claude/commands/`, `.github/prompts/`, or `.agents/commands/`:

```bash
echo "Review this code" > .claude/commands/review.md
/review            # Now available as a command
```

## Advanced Setup

### Round-Robin Load Balancing

Configure in `~/.ticca/extra_models.json` to distribute requests across multiple API keys.

### Durable Execution (DBOS)

Enable with `/set enable_dbos true`. Configure via:
- `DBOS_CONDUCTOR_KEY`: Connect to DBOS Management Console
- `DBOS_SYSTEM_DATABASE_URL`: Database URL (default: SQLite)

### MCP Servers

Manage servers via `/mcp` commands or TUI settings.

## Requirements

- Python 3.11+
- API keys for your LLM provider(s) or a local server (Ollama, VLLM, etc.)

## Privacy

✅ Zero telemetry • ✅ Zero prompt logging • ✅ No data sharing • ✅ Local LLM support

## Links

- **Repository**: https://github.com/mpfaffenberger/ticca
- **Issues**: https://github.com/mpfaffenberger/ticca/issues
- **License**: [MIT](LICENSE)

---

Built with privacy and efficiency in mind.
