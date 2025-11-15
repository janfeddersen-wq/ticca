"""Shared helpers for persisting and restoring chat sessions.

This module provides a backward-compatible interface to the new hybrid storage system
(SQLite + JSON + ChromaDB) while maintaining the same API as the old pickle-based system.

Migration Path:
1. Old code continues to work (calls these functions)
2. These functions now use hybrid_storage under the hood
3. Old pickle files are automatically migrated on first access
4. New sessions are saved in the better format
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Callable, List

# Import hybrid storage
from ticca.hybrid_storage import create_storage, StoredMessage

SessionHistory = List[Any]
TokenEstimator = Callable[[Any], int]


@dataclass(slots=True)
class SessionPaths:
    """Legacy path structure for backward compatibility."""
    pickle_path: Path  # Now points to JSON file
    metadata_path: Path  # Still used for compatibility


@dataclass(slots=True)
class SessionMetadata:
    """Session metadata structure."""
    session_name: str
    timestamp: str
    message_count: int
    total_tokens: int
    pickle_path: Path  # Legacy name, actually JSON now
    metadata_path: Path
    auto_saved: bool = False

    def as_serialisable(self) -> dict[str, Any]:
        return {
            "session_name": self.session_name,
            "timestamp": self.timestamp,
            "message_count": self.message_count,
            "total_tokens": self.total_tokens,
            "file_path": str(self.pickle_path),
            "auto_saved": self.auto_saved,
        }


def ensure_directory(path: Path) -> Path:
    """Ensure a directory exists."""
    path.mkdir(parents=True, exist_ok=True)
    return path


def build_session_paths(base_dir: Path, session_name: str) -> SessionPaths:
    """Build session file paths (now using JSON instead of pickle)."""
    # New: use .json instead of .pkl
    json_path = base_dir / f"{session_name}.json"
    metadata_path = base_dir / f"{session_name}_meta.json"
    return SessionPaths(pickle_path=json_path, metadata_path=metadata_path)


def _get_storage(base_dir: Path):
    """Get or create a hybrid storage instance for the given directory.

    This centralizes storage creation with proper configuration.
    """
    return create_storage(base_dir=base_dir)


def _migrate_pickle_if_exists(base_dir: Path, session_name: str) -> bool:
    """Automatically migrate old pickle files to new format if they exist.

    Args:
        base_dir: Base directory for sessions
        session_name: Name of the session

    Returns:
        True if migration occurred, False otherwise
    """
    import pickle
    from datetime import datetime

    # Check for old pickle file
    old_pickle_path = base_dir / f"{session_name}.pkl"
    if not old_pickle_path.exists():
        return False

    # Load from pickle
    try:
        with open(old_pickle_path, 'rb') as f:
            messages = pickle.load(f)
    except Exception:
        # Can't load pickle, skip migration
        return False

    # Get metadata if it exists
    meta_path = base_dir / f"{session_name}_meta.json"
    agent_name = "unknown"
    auto_saved = False

    if meta_path.exists():
        try:
            with open(meta_path, 'r') as f:
                meta_data = json.load(f)
                agent_name = meta_data.get('agent_name', 'unknown')
                auto_saved = meta_data.get('auto_saved', False)
        except Exception:
            pass

    # Migrate to new storage
    storage = _get_storage(base_dir)
    storage.save_session(
        session_id=session_name,
        messages=messages,
        agent_name=agent_name,
        auto_saved=auto_saved
    )

    # Rename old pickle to .pkl.old (don't delete, just in case)
    try:
        old_pickle_path.rename(old_pickle_path.with_suffix('.pkl.old'))
    except Exception:
        pass  # If rename fails, it's okay

    return True


def save_session(
    *,
    history: SessionHistory,
    session_name: str,
    base_dir: Path,
    timestamp: str,
    token_estimator: TokenEstimator,
    auto_saved: bool = False,
) -> SessionMetadata:
    """Save a session using hybrid storage (SQLite + JSON + ChromaDB).

    This maintains API compatibility with old pickle-based system.
    """
    ensure_directory(base_dir)

    # Use hybrid storage
    storage = _get_storage(base_dir)

    # Determine agent name (try to infer from context)
    agent_name = "unknown"
    try:
        from ticca.agents.agent_manager import get_current_agent
        current_agent = get_current_agent()
        if current_agent:
            agent_name = current_agent.display_name
    except Exception:
        pass

    # Save to hybrid storage
    storage_metadata = storage.save_session(
        session_id=session_name,
        messages=history,
        agent_name=agent_name,
        token_estimator=token_estimator,
        auto_saved=auto_saved
    )

    # Build legacy paths
    paths = build_session_paths(base_dir, session_name)

    # Create legacy metadata JSON for backward compatibility
    total_tokens = sum(token_estimator(message) for message in history)
    metadata = SessionMetadata(
        session_name=session_name,
        timestamp=timestamp,
        message_count=len(history),
        total_tokens=total_tokens,
        pickle_path=paths.pickle_path,
        metadata_path=paths.metadata_path,
        auto_saved=auto_saved,
    )

    with paths.metadata_path.open("w", encoding="utf-8") as metadata_file:
        json.dump(metadata.as_serialisable(), metadata_file, indent=2)

    return metadata


def load_session(session_name: str, base_dir: Path) -> SessionHistory:
    """Load a session from hybrid storage.

    Automatically migrates old pickle files on first access.
    """
    # Check if we need to migrate from pickle
    _migrate_pickle_if_exists(base_dir, session_name)

    # Load from hybrid storage
    storage = _get_storage(base_dir)

    try:
        stored_messages = storage.load_session(session_name)

        # Convert StoredMessage back to pydantic_ai ModelMessage format
        from pydantic_ai.messages import ModelRequest, ModelResponse, TextPart, ToolReturnPart

        converted_messages = []
        for msg in stored_messages:
            # Create appropriate message type based on role
            if msg.role == 'user':
                # User messages are ModelRequest with TextPart
                converted_messages.append(
                    ModelRequest(parts=[TextPart(content=msg.content)])
                )
            elif msg.role == 'assistant':
                # Assistant messages are ModelResponse with TextPart
                converted_messages.append(
                    ModelResponse(parts=[TextPart(content=msg.content)])
                )
            elif msg.role == 'tool':
                # Tool return messages
                if msg.tool_call_id:
                    converted_messages.append(
                        ModelResponse(parts=[
                            ToolReturnPart(
                                tool_name=msg.tool_name or '',
                                content=msg.content,
                                tool_call_id=msg.tool_call_id
                            )
                        ])
                    )
                else:
                    # Fallback if no tool_call_id
                    converted_messages.append(
                        ModelResponse(parts=[TextPart(content=msg.content)])
                    )
            else:
                # System or other messages - use TextPart
                converted_messages.append(
                    ModelRequest(parts=[TextPart(content=msg.content)])
                )

        return converted_messages
    except FileNotFoundError:
        # If not in new storage, try old pickle as fallback
        paths = build_session_paths(base_dir, session_name)
        old_pickle = paths.pickle_path.with_suffix('.pkl')

        if old_pickle.exists():
            import pickle
            with old_pickle.open("rb") as f:
                return pickle.load(f)

        # Really not found
        raise FileNotFoundError(f"Session '{session_name}' not found")


def list_sessions(base_dir: Path) -> List[str]:
    """List all available sessions.

    Returns session names (IDs) from both old and new storage.
    """
    if not base_dir.exists():
        return []

    session_names = set()

    # Get from hybrid storage
    try:
        storage = _get_storage(base_dir)
        metadata_list = storage.list_sessions(limit=999999)
        session_names.update(meta.session_id for meta in metadata_list)
    except Exception:
        pass

    # Also check for old pickle files
    for pkl_file in base_dir.glob("*.pkl"):
        session_names.add(pkl_file.stem)

    return sorted(session_names)


def cleanup_sessions(base_dir: Path, max_sessions: int) -> List[str]:
    """Clean up old sessions, keeping only the most recent ones.

    Args:
        base_dir: Directory containing sessions
        max_sessions: Maximum number of sessions to keep (0 = keep all)

    Returns:
        List of deleted session names
    """
    if max_sessions <= 0:
        return []

    if not base_dir.exists():
        return []

    # Use hybrid storage cleanup
    storage = _get_storage(base_dir)
    return storage.cleanup_old_sessions(max_sessions)


async def restore_autosave_interactively(base_dir: Path) -> None:
    """Prompt the user to load an autosave session from base_dir, if any exist.

    This uses hybrid storage but maintains the same interactive flow.
    """
    sessions = list_sessions(base_dir)
    if not sessions:
        return

    # Import locally to avoid pulling the messaging layer into storage modules
    from datetime import datetime
    from prompt_toolkit.formatted_text import FormattedText

    from ticca.agents.agent_manager import get_current_agent
    from ticca.command_line.prompt_toolkit_completion import (
        get_input_with_combined_completion,
    )
    from ticca.messaging import emit_success, emit_system_message, emit_warning

    # Get metadata from hybrid storage
    storage = _get_storage(base_dir)
    entries = []

    for name in sessions:
        try:
            metadata = storage.get_session_metadata(name)
            if metadata:
                timestamp = metadata.created_at.isoformat()
                message_count = metadata.message_count
            else:
                # Fallback to legacy metadata
                meta_path = base_dir / f"{name}_meta.json"
                if meta_path.exists():
                    with meta_path.open("r", encoding="utf-8") as f:
                        data = json.load(f)
                    timestamp = data.get("timestamp")
                    message_count = data.get("message_count")
                else:
                    timestamp = None
                    message_count = None
            entries.append((name, timestamp, message_count))
        except Exception:
            timestamp = None
            message_count = None
            entries.append((name, timestamp, message_count))

    def sort_key(entry):
        _, timestamp, _ = entry
        if timestamp:
            try:
                return datetime.fromisoformat(timestamp)
            except ValueError:
                return datetime.min
        return datetime.min

    entries.sort(key=sort_key, reverse=True)

    PAGE_SIZE = 5
    total = len(entries)
    page = 0

    def render_page() -> None:
        start = page * PAGE_SIZE
        end = min(start + PAGE_SIZE, total)
        page_entries = entries[start:end]
        emit_system_message("[bold magenta]Autosave Sessions Available:[/bold magenta]")
        for idx, (name, timestamp, message_count) in enumerate(page_entries, start=1):
            timestamp_display = timestamp or "unknown time"
            message_display = (
                f"{message_count} messages"
                if message_count is not None
                else "unknown size"
            )
            emit_system_message(
                f"  [{idx}] {name} ({message_display}, saved at {timestamp_display})"
            )
        if total > PAGE_SIZE:
            page_count = (total + PAGE_SIZE - 1) // PAGE_SIZE
            is_last_page = (page + 1) >= page_count
            remaining = total - (page * PAGE_SIZE + len(page_entries))
            summary = (
                f" and {remaining} more" if (remaining > 0 and not is_last_page) else ""
            )
            label = "Return to first page" if is_last_page else f"Next page{summary}"
            emit_system_message(f"  [6] {label}")
        emit_system_message("  [Enter] Skip loading autosave")

    chosen_name: str | None = None

    while True:
        render_page()
        try:
            selection = await get_input_with_combined_completion(
                FormattedText(
                    [
                        (
                            "class:prompt",
                            "Pick 1-5 to load, 6 for next, or name/Enter: ",
                        )
                    ]
                )
            )
        except (KeyboardInterrupt, EOFError):
            emit_warning("Autosave selection cancelled")
            return

        selection = (selection or "").strip()
        if not selection:
            return

        if selection.isdigit():
            num = int(selection)
            if num == 6 and total > PAGE_SIZE:
                page = (page + 1) % ((total + PAGE_SIZE - 1) // PAGE_SIZE)
                continue
            if 1 <= num <= 5:
                start = page * PAGE_SIZE
                idx = start + (num - 1)
                if 0 <= idx < total:
                    chosen_name = entries[idx][0]
                    break
                else:
                    emit_warning("Invalid selection for this page")
                    continue
            emit_warning("Invalid selection; choose 1-5 or 6 for next")
            continue

        for name, _ts, _mc in entries:
            if name == selection:
                chosen_name = name
                break
        if chosen_name:
            break
        emit_warning("No autosave loaded (invalid selection)")

    if not chosen_name:
        return

    try:
        history = load_session(chosen_name, base_dir)
    except FileNotFoundError:
        emit_warning(f"Autosave '{chosen_name}' could not be found")
        return
    except Exception as exc:
        emit_warning(f"Failed to load autosave '{chosen_name}': {exc}")
        return

    agent = get_current_agent()
    agent.set_message_history(history)

    # Set current autosave session id
    try:
        from ticca.config import set_current_autosave_from_session_name
        set_current_autosave_from_session_name(chosen_name)
    except Exception:
        pass

    total_tokens = sum(agent.estimate_tokens_for_message(msg) for msg in history)

    session_path = base_dir / f"{chosen_name}.json"
    emit_success(
        f"✅ Autosave loaded: {len(history)} messages ({total_tokens} tokens)\n"
        f"📁 From: {session_path}"
    )
