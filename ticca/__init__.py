import importlib.metadata

# Ticca - Terminal Injected Coding CLI Assistant ⚡
try:
    __version__ = importlib.metadata.version("ticca")
except Exception:
    # Fallback for dev environments where metadata might not be available
    __version__ = "0.0.0-dev"
