"""
GAC (Git Auto Commit) plugin for ticca.

This plugin integrates gac's AI-powered commit message generation
with ticca's model configuration and API keys.

Commands:
    /commit              - Generate commit message and create commit
    /commit-message      - Generate commit message only (no commit)

Options:
    --stage-all, -a      - Stage all changes before generating (git add .)
    --one-liner, -o      - Generate a one-line commit message
    --hint <text>        - Provide additional context for the message
    --no-verify, -n      - Skip git hooks when committing (commit only)

Examples:
    /commit --stage-all              - Stage all changes and commit
    /commit-message --one-liner      - Generate one-line message
    /commit --hint "fix bug #123"    - Add context to generation
"""

from __future__ import annotations

from . import register_callbacks  # noqa: F401
from .gac_wrapper import create_commit, generate_commit_message

__all__ = ["create_commit", "generate_commit_message"]
