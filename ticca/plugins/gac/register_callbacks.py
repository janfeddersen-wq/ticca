"""
Register gac plugin callbacks for ticca.

This module registers custom commands for git commit message generation.
"""

from typing import Any, List, Optional, Tuple

from ticca.callbacks import register_callback
from ticca.messaging import emit_error, emit_info

from .gac_wrapper import create_commit, generate_commit_message


class CommitMessageResult:
    """Special marker for commit message results that should be displayed."""

    def __init__(self, message: str):
        self.message = message

    def __str__(self) -> str:
        return self.message

    def __repr__(self) -> str:
        return f"CommitMessageResult({len(self.message)} chars)"


def _custom_help() -> List[Tuple[str, str]]:
    """Return help entries for gac commands."""
    return [
        ("commit", "Generate AI-powered commit message and create commit"),
        ("commit-message", "Generate AI-powered commit message (without committing)"),
    ]


def _handle_commit_command(command: str, name: str) -> Optional[Any]:
    """Handle the /commit command.

    Args:
        command: The full command string (e.g., "/commit --one-liner")
        name: The command name without leading slash (e.g., "commit")

    Returns:
        CommitMessageResult with the generated message, or None if failed
    """
    if name not in ["commit", "commit-message"]:
        return None

    # Parse command arguments
    parts = command.split()
    one_liner = "--one-liner" in parts or "-o" in parts
    no_verify = "--no-verify" in parts or "-n" in parts
    stage_all = "--stage-all" in parts or "-a" in parts

    # Extract hint if provided (everything after --hint or -h)
    hint = None
    try:
        if "--hint" in parts:
            hint_idx = parts.index("--hint")
            hint = " ".join(parts[hint_idx + 1:])
        elif "-h" in parts and parts.index("-h") > 0:  # Make sure it's not the help flag
            hint_idx = parts.index("-h")
            hint = " ".join(parts[hint_idx + 1:])
    except (IndexError, ValueError):
        pass

    if name == "commit":
        # Full commit: generate message and commit
        emit_info("🚀 Generating commit message and creating commit...")
        success = create_commit(
            model_name=None,  # Use default model
            one_liner=one_liner,
            language="en",
            hint=hint,
            no_verify=no_verify,
            stage_all=stage_all
        )

        if success:
            return CommitMessageResult("Commit created successfully")
        else:
            return CommitMessageResult("Failed to create commit")

    elif name == "commit-message":
        # Just generate the message, don't commit
        emit_info("💭 Generating commit message...")
        message = generate_commit_message(
            model_name=None,  # Use default model
            one_liner=one_liner,
            language="en",
            hint=hint,
            stage_all=stage_all
        )

        if message:
            emit_info(f"\n📝 Generated commit message:\n\n{message}\n")
            return CommitMessageResult(message)
        else:
            emit_error("Failed to generate commit message")
            return None

    return None


# Register callbacks
register_callback("custom_command_help", _custom_help)
register_callback("custom_command", _handle_commit_command)

__all__ = ["CommitMessageResult"]
