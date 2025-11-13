# Ticca

**Terminal Injected Coding CLI Assistant**

A privacy-focused AI coding assistant for your terminal. Multi-model support, specialized agents, and zero telemetry.

[![License](https://img.shields.io/badge/License-MIT-green?style=for-the-badge)](LICENSE)
[![Python](https://img.shields.io/badge/Python-3.11%2B-blue?style=for-the-badge&logo=python&logoColor=white)](https://python.org)

## Quick Start

```bash
# Using UV (recommended)
curl -LsSf https://astral.sh/uv/install.sh | sh
uvx ticca

# Using pip
pip install ticca
ticca
```

## Features

- 🎨 **Beautiful TUI** - Terminal interface powered by Textual
- 🤖 **Multi-Model** - OpenAI, Claude, Gemini, Cerebras, Ollama, custom endpoints
- 🎯 **Specialized Agents** - Code review, debugging, security auditing, refactoring
- 🔌 **MCP Integration** - Extend with Model Context Protocol servers
- 🔒 **Privacy First** - Zero telemetry, local-only option, no data collection
- ⚡ **Load Balancing** - Round-robin across multiple API keys

## Usage

```bash
ticca                                    # Start TUI
ticca -i                                 # Interactive CLI
ticca -p "Explain this code"             # Single prompt
ticca -m gpt-4 -a code-reviewer          # Specify model and agent
```

### In-Session Commands

```bash
/agent <name>              # Switch agent (code-reviewer, security-auditor, etc.)
/model <name>              # Switch model
/mcp list                  # Manage MCP servers
/set <key> <value>         # Configure settings
/help                      # Show help
```

## Configuration

### API Keys

Set via environment variables or TUI settings:

```bash
export OPENAI_API_KEY=sk-...
export ANTHROPIC_API_KEY=sk-ant-...
export GEMINI_API_KEY=...
```

### Models

Configure in `~/.ticca/models.json` or `~/.ticca/extra_models.json`:

```json
{
  "gpt-4": {
    "type": "openai",
    "model": "gpt-4",
    "max_tokens": 8000
  }
}
```

### Custom Commands

Create markdown files in `.claude/commands/`, `.github/prompts/`, or `.agents/commands/`:

```bash
cat > .claude/commands/review.md << 'EOF'
# Code Review
Review for security, performance, style, and best practices.
EOF

/review  # Use in Ticca
```

## Agents

Built-in specialized agents:

- **code-reviewer** - Code quality and best practices
- **security-auditor** - Security vulnerability analysis  
- **debugger** - Bug identification and fixes
- **refactorer** - Code improvements
- **documenter** - Documentation generation

Create custom agents in `~/.ticca/agents/` as JSON files or use `/agent agent-creator`.

## MCP Servers

Extend capabilities with Model Context Protocol:

```bash
/mcp list                  # Show servers
/mcp start <server>        # Start server
/mcp status                # Check status
```

Configure in `~/.ticca/mcp_servers.json`:

```json
{
  "file-server": {
    "enabled": true,
    "path": "/usr/local/bin/mcp-file-server",
    "config": {}
  }
}
```

## Advanced Features

### Load Balancing

Rotate across multiple API keys:

```json
{
  "gpt4-balanced": {
    "type": "round_robin",
    "models": ["openai-key-1", "openai-key-2"],
    "rotate_every": 5
  }
}
```

### Custom Endpoints

Self-hosted or private models:

```json
{
  "local-llama": {
    "type": "openai",
    "model": "llama-2",
    "custom_endpoint": {
      "url": "http://localhost:8000/v1",
      "api_key": "not-needed"
    }
  }
}
```

### DBOS (Optional)

Durable execution with automatic recovery:

```bash
/set enable_dbos true
```

## Privacy

✅ Zero telemetry or tracking  
✅ No cloud storage of conversations  
✅ Local-only mode available (Ollama)  
✅ Direct API communication (no proxies)  
✅ Your code never leaves your machine

## Requirements

- Python 3.11+
- One of: OpenAI, Anthropic, Gemini, Cerebras API key, or local LLM (Ollama, VLLM)

## Installation

### UV (Recommended)

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
export UV_MANAGED_PYTHON=1
uvx ticca
```

### pip

```bash
pip install ticca
ticca
```

### From Source

```bash
git clone https://github.com/mpfaffenberger/ticca.git
cd ticca
./start.sh
```

## Contributing

Contributions welcome! Please:

- Follow existing code style
- Include tests (`pytest`)
- Update documentation
- Maintain backward compatibility

See [CONTRIBUTING.md](CONTRIBUTING.md) for details.

## License

MIT License - see [LICENSE](LICENSE) for details.

## Links

- **Repository**: https://github.com/mpfaffenberger/ticca
- **Issues**: https://github.com/mpfaffenberger/ticca/issues
- **Discussions**: https://github.com/mpfaffenberger/ticca/discussions
- **AGENT.md**: https://agent.md
- **MCP**: https://modelcontextprotocol.io

---

**Ticca** - Built with ❤️ for developers who value efficiency, privacy, and simplicity.
