#!/bin/bash
# Ticca - Terminal Injected Coding CLI Assistant
# Simple launcher script that starts Ticca in TUI mode

# Check if uv is installed
if command -v uv &> /dev/null; then
    echo "Starting Ticca with uv..."
    uv run python -m ticca
elif command -v python3 &> /dev/null; then
    echo "Starting Ticca with python3..."
    python3 -m ticca
elif command -v python &> /dev/null; then
    echo "Starting Ticca with python..."
    python -m ticca
else
    echo "Error: Python not found. Please install Python 3.11+ or UV."
    exit 1
fi
