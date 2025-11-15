"""Hybrid storage system stub.

This module provides a minimal implementation to support session storage.
The full hybrid storage system (SQLite + JSON + ChromaDB) is documented
in HYBRID_STORAGE.md but not yet fully implemented.

For now, this provides stub implementations that allow the session storage
to function without errors.
"""

from dataclasses import dataclass
from typing import Any, Dict, List, Optional
from pathlib import Path


@dataclass
class StoredMessage:
    """Simplified message format for storage."""
    role: str  # "user", "assistant", "system", "tool"
    content: str
    timestamp: str
    tool_name: Optional[str] = None
    tool_call_id: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None


class HybridStorage:
    """Stub implementation of hybrid storage.

    This is a placeholder until the full implementation is complete.
    Currently just provides the interface without actual functionality.
    """

    def __init__(self, base_dir: Path, enable_semantic_search: bool = False):
        self.base_dir = Path(base_dir).expanduser()
        self.enable_semantic_search = enable_semantic_search

    def save_session(
        self,
        session_id: str,
        messages: List[Any],
        agent_name: str = "default",
        auto_saved: bool = False
    ):
        """Stub: Save session (not implemented)."""
        pass

    def load_session(self, session_id: str) -> List[Any]:
        """Stub: Load session (not implemented)."""
        return []

    def list_sessions(
        self,
        agent_name: Optional[str] = None,
        auto_saved_only: bool = False,
        limit: int = 100
    ) -> List[Dict[str, Any]]:
        """Stub: List sessions (not implemented)."""
        return []

    def semantic_search(
        self,
        query: str,
        n_results: int = 10,
        agent_name: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """Stub: Semantic search (not implemented)."""
        return []


def create_storage(
    base_dir: Path,
    enable_semantic_search: bool = False
) -> HybridStorage:
    """Create a hybrid storage instance.

    Args:
        base_dir: Base directory for storage
        enable_semantic_search: Whether to enable ChromaDB semantic search

    Returns:
        HybridStorage instance (currently a stub)
    """
    return HybridStorage(base_dir, enable_semantic_search)
