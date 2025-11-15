"""Hybrid Storage System: SQLite + JSON + ChromaDB

This module implements a three-tier storage system for chat sessions:
1. SQLite - Fast metadata queries
2. JSON - Human-readable message storage
3. ChromaDB - Semantic search (optional)

See HYBRID_STORAGE.md for full documentation.
"""

import json
import sqlite3
from dataclasses import dataclass, asdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional

# Conditional ChromaDB import
try:
    import chromadb
    from chromadb.config import Settings
    CHROMADB_AVAILABLE = True
except ImportError:
    CHROMADB_AVAILABLE = False


@dataclass
class StoredMessage:
    """Simplified message format for storage."""
    role: str  # "user", "assistant", "system", "tool"
    content: str
    timestamp: str
    tool_name: Optional[str] = None
    tool_call_id: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None

    def to_dict(self) -> dict:
        """Convert to dictionary for JSON serialization."""
        return {k: v for k, v in asdict(self).items() if v is not None}

    @classmethod
    def from_dict(cls, data: dict) -> 'StoredMessage':
        """Create from dictionary."""
        return cls(**data)


@dataclass
class SessionMetadata:
    """Session metadata stored in SQLite."""
    session_id: str
    agent_name: str
    created_at: datetime
    updated_at: datetime
    message_count: int
    total_tokens: int
    auto_saved: bool


class HybridStorage:
    """Hybrid storage implementation with SQLite + JSON + optional ChromaDB."""

    def __init__(self, base_dir: Path, enable_semantic_search: bool = False):
        # Ensure base_dir is always an absolute path under ~/.ticca/
        self.base_dir = Path(base_dir).expanduser().resolve()
        self.base_dir.mkdir(parents=True, exist_ok=True)

        # Setup SQLite
        self.db_path = self.base_dir / "sessions.db"
        self._init_database()

        # Setup JSON storage directory
        self.json_dir = self.base_dir / "sessions"
        self.json_dir.mkdir(parents=True, exist_ok=True)

        # Setup ChromaDB (optional)
        self.enable_semantic_search = enable_semantic_search and CHROMADB_AVAILABLE
        self.chroma_client = None
        self.chroma_collection = None

        if self.enable_semantic_search:
            try:
                self._init_chromadb()
            except Exception as e:
                print(f"Warning: Failed to initialize ChromaDB: {e}")
                self.enable_semantic_search = False

    def _init_database(self):
        """Initialize SQLite database schema."""
        conn = sqlite3.connect(str(self.db_path))
        try:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS sessions (
                    session_id TEXT PRIMARY KEY,
                    agent_name TEXT NOT NULL,
                    created_at TIMESTAMP NOT NULL,
                    updated_at TIMESTAMP NOT NULL,
                    message_count INTEGER NOT NULL DEFAULT 0,
                    total_tokens INTEGER NOT NULL DEFAULT 0,
                    auto_saved BOOLEAN NOT NULL DEFAULT 0
                )
            """)
            conn.execute("CREATE INDEX IF NOT EXISTS idx_created_at ON sessions(created_at DESC)")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_agent_name ON sessions(agent_name)")
            conn.commit()
        finally:
            conn.close()

    def _init_chromadb(self):
        """Initialize ChromaDB for semantic search."""
        if not CHROMADB_AVAILABLE:
            return

        chroma_dir = self.base_dir / "chroma"
        chroma_dir.mkdir(parents=True, exist_ok=True)

        self.chroma_client = chromadb.PersistentClient(
            path=str(chroma_dir),
            settings=Settings(anonymized_telemetry=False)
        )
        self.chroma_collection = self.chroma_client.get_or_create_collection(
            name="ticca_messages"
        )

    def _convert_message_to_stored(self, msg: Any) -> StoredMessage:
        """Convert pydantic_ai ModelMessage to StoredMessage."""
        from pydantic_ai.messages import TextPart, ToolCallPart, ToolReturnPart

        # Import additional part types that contain user content
        try:
            from pydantic_ai.messages import UserPromptPart, SystemPromptPart, RetryPromptPart
        except ImportError:
            # Fallback for older versions
            UserPromptPart = None
            SystemPromptPart = None
            RetryPromptPart = None

        role = "unknown"
        content = ""
        tool_name = None
        tool_call_id = None

        # Determine role from message type
        msg_type = type(msg).__name__
        if "Request" in msg_type:
            role = "user"
        elif "Response" in msg_type:
            role = "assistant"

        # Extract content from parts
        if hasattr(msg, 'parts'):
            for part in msg.parts:
                # Handle all text-containing parts
                if isinstance(part, TextPart):
                    content += part.content
                elif UserPromptPart and isinstance(part, UserPromptPart):
                    # This is the actual user's message!
                    content += part.content
                elif SystemPromptPart and isinstance(part, SystemPromptPart):
                    content += part.content
                    role = "system"
                elif RetryPromptPart and isinstance(part, RetryPromptPart):
                    content += part.content
                elif isinstance(part, ToolCallPart):
                    tool_name = part.tool_name
                    tool_call_id = part.tool_call_id
                    role = "tool_call"
                    content = f"Tool call: {tool_name}"
                elif isinstance(part, ToolReturnPart):
                    tool_name = part.tool_name
                    tool_call_id = part.tool_call_id
                    role = "tool"
                    content = str(part.content) if part.content else ""
                elif hasattr(part, 'content') and hasattr(part, 'part_kind'):
                    # Fallback: any part with content attribute (future-proofing)
                    part_content = getattr(part, 'content', '')
                    if part_content and isinstance(part_content, str):
                        content += part_content

        timestamp = datetime.now(timezone.utc).isoformat()

        return StoredMessage(
            role=role,
            content=content,
            timestamp=timestamp,
            tool_name=tool_name,
            tool_call_id=tool_call_id
        )

    def save_session(
        self,
        session_id: str,
        messages: List[Any],
        agent_name: str = "unknown",
        auto_saved: bool = False,
        token_estimator: Optional[Callable[[Any], int]] = None
    ) -> SessionMetadata:
        """Save a session to hybrid storage.

        Args:
            session_id: Unique session identifier
            messages: List of pydantic_ai ModelMessage objects
            agent_name: Name of the agent
            auto_saved: Whether this is an autosave
            token_estimator: Optional function to estimate tokens

        Returns:
            SessionMetadata for the saved session
        """
        # Convert messages to storable format
        stored_messages = [self._convert_message_to_stored(msg) for msg in messages]

        # Save to JSON
        json_path = self.json_dir / f"{session_id}.json"
        with json_path.open('w', encoding='utf-8') as f:
            json.dump(
                [msg.to_dict() for msg in stored_messages],
                f,
                indent=2,
                ensure_ascii=False
            )

        # Calculate tokens
        total_tokens = 0
        if token_estimator:
            total_tokens = sum(token_estimator(msg) for msg in messages)

        # Save metadata to SQLite
        now = datetime.now(timezone.utc)
        conn = sqlite3.connect(str(self.db_path))
        try:
            conn.execute("""
                INSERT OR REPLACE INTO sessions
                (session_id, agent_name, created_at, updated_at, message_count, total_tokens, auto_saved)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (session_id, agent_name, now, now, len(messages), total_tokens, auto_saved))
            conn.commit()
        finally:
            conn.close()

        # Index in ChromaDB (if enabled)
        if self.enable_semantic_search and self.chroma_collection:
            try:
                self._index_messages_in_chromadb(session_id, stored_messages, agent_name)
            except Exception as e:
                print(f"Warning: Failed to index in ChromaDB: {e}")

        return SessionMetadata(
            session_id=session_id,
            agent_name=agent_name,
            created_at=now,
            updated_at=now,
            message_count=len(messages),
            total_tokens=total_tokens,
            auto_saved=auto_saved
        )

    def _index_messages_in_chromadb(self, session_id: str, messages: List[StoredMessage], agent_name: str):
        """Index messages in ChromaDB for semantic search."""
        if not self.chroma_collection:
            return

        # Only index user and assistant messages (skip tool calls)
        indexable = [msg for msg in messages if msg.role in ("user", "assistant")]
        if not indexable:
            return

        ids = [f"{session_id}_{i}" for i in range(len(indexable))]
        documents = [msg.content for msg in indexable]
        metadatas = [
            {
                "session_id": session_id,
                "agent_name": agent_name,
                "role": msg.role,
                "timestamp": msg.timestamp,
                "message_index": i
            }
            for i, msg in enumerate(indexable)
        ]

        self.chroma_collection.add(
            ids=ids,
            documents=documents,
            metadatas=metadatas
        )

    def load_session(self, session_id: str) -> List[StoredMessage]:
        """Load a session from JSON storage.

        Args:
            session_id: Session identifier

        Returns:
            List of StoredMessage objects

        Raises:
            FileNotFoundError: If session doesn't exist
        """
        json_path = self.json_dir / f"{session_id}.json"
        if not json_path.exists():
            raise FileNotFoundError(f"Session '{session_id}' not found")

        with json_path.open('r', encoding='utf-8') as f:
            data = json.load(f)

        return [StoredMessage.from_dict(msg_data) for msg_data in data]

    def get_session_metadata(self, session_id: str) -> Optional[SessionMetadata]:
        """Get metadata for a session from SQLite.

        Args:
            session_id: Session identifier

        Returns:
            SessionMetadata or None if not found
        """
        conn = sqlite3.connect(str(self.db_path))
        try:
            cursor = conn.execute(
                "SELECT * FROM sessions WHERE session_id = ?",
                (session_id,)
            )
            row = cursor.fetchone()
            if not row:
                return None

            return SessionMetadata(
                session_id=row[0],
                agent_name=row[1],
                created_at=datetime.fromisoformat(row[2]),
                updated_at=datetime.fromisoformat(row[3]),
                message_count=row[4],
                total_tokens=row[5],
                auto_saved=bool(row[6])
            )
        finally:
            conn.close()

    def list_sessions(
        self,
        agent_name: Optional[str] = None,
        auto_saved_only: bool = False,
        limit: int = 100
    ) -> List[SessionMetadata]:
        """List sessions with optional filtering.

        Args:
            agent_name: Filter by agent name (optional)
            auto_saved_only: Only return autosaved sessions
            limit: Maximum number of results

        Returns:
            List of SessionMetadata objects
        """
        conn = sqlite3.connect(str(self.db_path))
        try:
            query = "SELECT * FROM sessions WHERE 1=1"
            params = []

            if agent_name:
                query += " AND agent_name = ?"
                params.append(agent_name)

            if auto_saved_only:
                query += " AND auto_saved = 1"

            query += " ORDER BY created_at DESC LIMIT ?"
            params.append(limit)

            cursor = conn.execute(query, params)
            rows = cursor.fetchall()

            return [
                SessionMetadata(
                    session_id=row[0],
                    agent_name=row[1],
                    created_at=datetime.fromisoformat(row[2]),
                    updated_at=datetime.fromisoformat(row[3]),
                    message_count=row[4],
                    total_tokens=row[5],
                    auto_saved=bool(row[6])
                )
                for row in rows
            ]
        finally:
            conn.close()

    def semantic_search(
        self,
        query: str,
        n_results: int = 10,
        agent_name: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """Search sessions by semantic similarity (requires ChromaDB).

        Args:
            query: Search query
            n_results: Number of results to return
            agent_name: Filter by agent name (optional)

        Returns:
            List of search results with content, metadata, and distances
        """
        if not self.enable_semantic_search or not self.chroma_collection:
            return []

        where_filter = {}
        if agent_name:
            where_filter["agent_name"] = agent_name

        results = self.chroma_collection.query(
            query_texts=[query],
            n_results=n_results,
            where=where_filter if where_filter else None
        )

        output = []
        for i in range(len(results['ids'][0])):
            output.append({
                'id': results['ids'][0][i],
                'content': results['documents'][0][i],
                'metadata': results['metadatas'][0][i],
                'distance': results['distances'][0][i] if 'distances' in results else None
            })

        return output

    def cleanup_old_sessions(self, max_sessions: int) -> List[str]:
        """Delete old sessions, keeping only the most recent ones.

        Args:
            max_sessions: Maximum number of sessions to keep

        Returns:
            List of deleted session IDs
        """
        conn = sqlite3.connect(str(self.db_path))
        try:
            # Get sessions to delete (oldest first)
            cursor = conn.execute("""
                SELECT session_id FROM sessions
                ORDER BY created_at DESC
                LIMIT -1 OFFSET ?
            """, (max_sessions,))

            to_delete = [row[0] for row in cursor.fetchall()]

            # Delete from SQLite
            for session_id in to_delete:
                conn.execute("DELETE FROM sessions WHERE session_id = ?", (session_id,))

                # Delete JSON file
                json_path = self.json_dir / f"{session_id}.json"
                if json_path.exists():
                    json_path.unlink()

                # Delete from ChromaDB
                if self.enable_semantic_search and self.chroma_collection:
                    try:
                        # Delete all messages from this session
                        self.chroma_collection.delete(
                            where={"session_id": session_id}
                        )
                    except Exception:
                        pass

            conn.commit()
            return to_delete
        finally:
            conn.close()


def create_storage(
    base_dir: Path,
    enable_semantic_search: bool = False
) -> HybridStorage:
    """Create a hybrid storage instance.

    Args:
        base_dir: Base directory for storage
        enable_semantic_search: Whether to enable ChromaDB semantic search

    Returns:
        HybridStorage instance
    """
    return HybridStorage(base_dir, enable_semantic_search)
