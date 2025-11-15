# Hybrid Storage System: SQLite + JSON + ChromaDB

## Overview

Ticca now uses a **three-tier hybrid storage system** that replaces the old pickle-based storage:

### **Tier 1: SQLite** - Fast Metadata Queries
- **Purpose**: Session management and fast filtering
- **Stores**: Session metadata (ID, agent, timestamps, token counts)
- **Benefits**: Instant queries, proper indexing, ACID transactions

### **Tier 2: JSON** - Human-Readable Message Storage
- **Purpose**: Durable, inspectable conversation data
- **Stores**: Full message content and conversation history
- **Benefits**: Debug-friendly, safe (no code execution), version-control-ready

### **Tier 3: ChromaDB** - Semantic Search (Optional)
- **Purpose**: Vector search and intelligent features
- **Stores**: Message embeddings for similarity search
- **Benefits**: Find sessions by meaning, smart context compaction

---

## Why This Is Better Than Pickle

| Feature | Old (Pickle) | New (Hybrid) |
|---------|-------------|--------------|
| **Security** | ⚠️ Can execute malicious code | ✅ Safe JSON format |
| **Debugging** | ❌ Binary, need Python to read | ✅ Human-readable JSON |
| **Queries** | ❌ Must load all files | ✅ Fast SQL queries |
| **Search** | ❌ Text matching only | ✅ Semantic search by meaning |
| **Migration** | ❌ Breaks between Python versions | ✅ JSON is future-proof |
| **Size** | 🟡 Compact but opaque | 🟡 Slightly larger but inspectable |

---

## Configuration

Add these settings to `~/.ticca/puppy.cfg`:

```ini
[puppy]
# Enable/disable semantic search (ChromaDB)
enable_semantic_search = true

# Embedding model for semantic search
# Options:
#   - Qwen/Qwen3-Embedding-0.6B (free, local, ~600MB, fast, multilingual)
#   - sentence-transformers/all-MiniLM-L6-v2 (free, local, ~100MB)
#   - openai:text-embedding-3-small (paid API, fastest, best quality)
embedding_model = Qwen/Qwen3-Embedding-0.6B
```

---

## Migration from Pickle

The system **automatically migrates** old pickle files on first access:

### Automatic Migration (Recommended)
Just use ticca normally - old pickle sessions will be migrated transparently when accessed.

### Manual Migration (Advanced)
For bulk migration, use the migration script:

```bash
# Dry run - see what would be migrated
python -m ticca.migrate_to_hybrid_storage --dry-run

# Migrate all sessions
python -m ticca.migrate_to_hybrid_storage

# Migrate with semantic search disabled (faster)
python -m ticca.migrate_to_hybrid_storage --disable-semantic-search

# Force overwrite if sessions already exist
python -m ticca.migrate_to_hybrid_storage --force
```

**What gets migrated:**
- ✅ Autosave sessions (`~/.ticca/autosaves/*.pkl`)
- ✅ Subagent sessions (`~/.ticca/subagent_sessions/*.pkl`)
- ✅ Message history and metadata

**Old pickle files are renamed** to `.pkl.old` after successful migration (not deleted, for safety).

---

## Storage Locations

```
~/.ticca/
├── autosaves/              # Autosave sessions (hybrid storage)
│   ├── sessions.db         # SQLite: session metadata
│   ├── sessions/           # JSON: message content
│   │   ├── auto_session_20250114_120000.json
│   │   └── auto_session_20250114_130000.json
│   └── chroma/             # ChromaDB: embeddings (if enabled)
│
└── subagent_sessions/      # Subagent sessions (hybrid storage)
    ├── sessions.db
    ├── sessions/
    │   ├── qa-expert-session-1.json
    │   └── code-reviewer-session-2.json
    └── chroma/
```

---

## Usage Examples

### Basic Session Operations (Automatic)

No changes needed! Existing code continues to work:

```python
from ticca.session_storage import save_session, load_session, list_sessions

# Save session (now uses hybrid storage under the hood)
save_session(
    history=messages,
    session_name="my-session",
    base_dir=Path("~/.ticca/autosaves"),
    timestamp=datetime.now().isoformat(),
    token_estimator=lambda msg: len(str(msg))
)

# Load session (auto-migrates pickle if needed)
messages = load_session("my-session", Path("~/.ticca/autosaves"))

# List all sessions (includes both old and new formats)
sessions = list_sessions(Path("~/.ticca/autosaves"))
```

### Advanced: Direct Hybrid Storage API

For new code, use the hybrid storage API directly:

```python
from ticca.hybrid_storage import create_storage
from pathlib import Path

# Create storage instance
storage = create_storage(
    base_dir=Path("~/.ticca/my_sessions"),
    enable_semantic_search=True
)

# Save a session
storage.save_session(
    session_id="implement-oauth-abc123",
    messages=message_list,
    agent_name="code-agent",
    auto_saved=False
)

# Load a session
messages = storage.load_session("implement-oauth-abc123")

# List sessions with filtering
sessions = storage.list_sessions(
    agent_name="code-agent",
    auto_saved_only=False,
    limit=50
)

# Semantic search (if enabled)
results = storage.semantic_search(
    query="sessions about authentication",
    n_results=10,
    agent_name="code-agent"  # optional filter
)

for result in results:
    print(f"Session: {result['metadata']['session_id']}")
    print(f"Content: {result['content'][:100]}...")
    print(f"Similarity: {result['distance']}\n")
```

---

## Semantic Search Features

When `enable_semantic_search = true`, you get:

### 1. Find Sessions by Meaning

```python
# Find sessions about a topic, even if exact words differ
results = storage.semantic_search(
    query="help me implement OAuth",
    n_results=5
)
# Returns sessions about "authentication", "sign-in", "login", etc.
```

### 2. Intelligent Context Compaction (Future)

ChromaDB enables smart message deduplication:
- Identify semantically similar messages
- Keep diverse, unique information
- Remove repetitive confirmations

### 3. Agent Memory (Future)

Agents can recall relevant past conversations:
```python
# Agent query: "Remember when we discussed OAuth flow?"
# ChromaDB finds relevant past sessions automatically
```

---

## Performance Considerations

### Embedding Models

| Model | Speed | Size | Quality | Cost | Notes |
|-------|-------|------|---------|------|-------|
| `Qwen/Qwen3-Embedding-0.6B` | Fast | ~600MB | Excellent | Free | **Default**, multilingual, SOTA |
| `sentence-transformers/all-MiniLM-L6-v2` | Fast | ~100MB | Good | Free | Smaller alternative |
| `openai:text-embedding-3-small` | Very Fast | API | Better | $0.02/1M tokens | Cloud-based |

**Recommendation**: **Qwen3-Embedding-0.6B** (default) offers the best balance of quality, speed, and multilingual support. Use `all-MiniLM` if you need smaller disk footprint.

### Storage Size

- **JSON files**: ~2-3x larger than pickle (but human-readable)
- **SQLite DB**: ~10KB per 100 sessions (negligible)
- **ChromaDB embeddings**: ~1.5KB per message (only user/assistant messages indexed)

**Example**: 100 sessions with 50 messages each:
- JSON: ~5MB (inspectable, safe)
- SQLite: ~100KB (fast queries)
- ChromaDB: ~7.5MB (semantic search)
- **Total**: ~13MB vs ~4MB pickle (worth it!)

---

## Troubleshooting

### ChromaDB fails to initialize

**Symptom**: `Warning: Failed to initialize ChromaDB`

**Solution**:
1. Install dependencies: `uv pip install chromadb sentence-transformers`
2. Or disable semantic search: `enable_semantic_search = false` in config

### Migration script errors

**Symptom**: `Failed to load {session}.pkl`

**Solution**:
- Some pickle files may be corrupted
- The script continues and migrates what it can
- Check `--force` flag to overwrite existing sessions

### Sessions not appearing

**Symptom**: `list_sessions()` returns empty

**Solution**:
- Check `~/.ticca/autosaves/sessions/` directory exists
- Verify `sessions.db` file is present
- Try manual migration: `python -m ticca.migrate_to_hybrid_storage`

---

## FAQ

### Q: Will my old pickle sessions still work?
**A**: Yes! The system automatically migrates them on first access.

### Q: Can I disable ChromaDB?
**A**: Yes, set `enable_semantic_search = false` in config. Core storage still works.

### Q: Can I export sessions?
**A**: Yes! Just copy the JSON files from `~/.ticca/*/sessions/` - they're human-readable.

### Q: What if I want to go back to pickle?
**A**: Old `.pkl.old` files are preserved. You can restore them manually if needed.

### Q: Does this work with subagent sessions?
**A**: Yes! Both autosave and subagent sessions use hybrid storage.

### Q: How do I search across all my past sessions?
**A**: Use the semantic search API (requires `enable_semantic_search = true`):

```python
storage = create_storage(base_dir=Path("~/.ticca/autosaves"))
results = storage.semantic_search("sessions about database design", n_results=20)
```

---

## Implementation Details

### Message Serialization

Messages are converted to a simplified `StoredMessage` format:

```python
@dataclass
class StoredMessage:
    role: str  # "user", "assistant", "system", "tool"
    content: str
    timestamp: str
    tool_name: Optional[str] = None
    tool_call_id: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None
```

### Database Schema

```sql
CREATE TABLE sessions (
    session_id TEXT PRIMARY KEY,
    agent_name TEXT NOT NULL,
    created_at TIMESTAMP NOT NULL,
    updated_at TIMESTAMP NOT NULL,
    message_count INTEGER NOT NULL DEFAULT 0,
    total_tokens INTEGER NOT NULL DEFAULT 0,
    auto_saved BOOLEAN NOT NULL DEFAULT 0
);

CREATE INDEX idx_created_at ON sessions(created_at DESC);
CREATE INDEX idx_agent_name ON sessions(agent_name);
```

### ChromaDB Collection

- **Collection name**: `ticca_messages`
- **Indexed content**: User and assistant messages only (tool calls skipped)
- **Metadata**: `session_id`, `agent_name`, `role`, `timestamp`, `message_index`

---

## Contributing

Found a bug or have a feature request? Open an issue on GitHub!

**Future enhancements:**
- [ ] Session export/import tools
- [ ] Web UI for browsing sessions
- [ ] Advanced semantic search queries
- [ ] Automatic context compaction using ChromaDB
- [ ] Multi-user session sharing

---

**Happy coding with ticca's new hybrid storage! 🚀**
