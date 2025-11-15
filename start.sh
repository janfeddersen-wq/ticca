#!/bin/bash
# Ticca - Terminal Injected Coding CLI Assistant
# Simple launcher script that starts Ticca in TUI mode
#
# This script automatically enables performance profiling to help identify
# slow startup operations. The performance report will be saved to:
#   ~/.ticca/perf_report.txt
#
# Usage:
#   ./start.sh            # With profiling (default)
#   ./start.sh --no-profile   # Without profiling
#
# To run WITHOUT profiling (alternative methods):
#   uv run ticca
#   python -m ticca
#   ticca

# Parse arguments
ENABLE_PROFILING=1
TICCA_ARGS=()

for arg in "$@"; do
    if [ "$arg" = "--no-profile" ]; then
        ENABLE_PROFILING=0
    else
        TICCA_ARGS+=("$arg")
    fi
done

# Enable performance profiling unless --no-profile is passed
if [ $ENABLE_PROFILING -eq 1 ]; then
    export TICCA_PROFILE=1
    PROFILE_MSG="(profiling enabled)"
else
    unset TICCA_PROFILE
    PROFILE_MSG="(profiling disabled)"
fi

# Check if uv is installed
if command -v uv &> /dev/null; then
    echo "Starting Ticca with uv $PROFILE_MSG..."
    uv run python -m ticca "${TICCA_ARGS[@]}"
elif command -v python3 &> /dev/null; then
    echo "Starting Ticca with python3 $PROFILE_MSG..."
    python3 -m ticca "${TICCA_ARGS[@]}"
elif command -v python &> /dev/null; then
    echo "Starting Ticca with python $PROFILE_MSG..."
    python -m ticca "${TICCA_ARGS[@]}"
else
    echo "Error: Python not found. Please install Python 3.11+ or UV."
    exit 1
fi
