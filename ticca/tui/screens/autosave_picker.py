"""
Autosave Picker modal for TUI.
Lists recent autosave sessions and lets the user load one.
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import List, Optional, Tuple

from textual import on
from textual.app import ComposeResult
from textual.containers import Container, Horizontal
from textual.screen import ModalScreen
from textual.widgets import Button, Label, ListItem, ListView, Static

from ticca.session_storage import list_sessions


@dataclass(slots=True)
class AutosaveEntry:
    name: str
    timestamp: Optional[str]
    message_count: Optional[int]
    last_user_message: Optional[str] = None


def _load_metadata(base_dir: Path, name: str) -> Tuple[Optional[str], Optional[int], Optional[str]]:
    """Load metadata and last user message from session.

    Returns:
        Tuple of (timestamp, message_count, last_user_message)
    """
    meta_path = base_dir / f"{name}_meta.json"
    timestamp = None
    message_count = None

    try:
        with meta_path.open("r", encoding="utf-8") as meta_file:
            data = json.load(meta_file)
        timestamp = data.get("timestamp")
        message_count = data.get("message_count")
    except Exception:
        pass

    # Get last user message from session JSON (now fixed to save properly!)
    last_user_message = None
    try:
        # Try new JSON format first
        json_path = base_dir / "sessions" / f"{name}.json"
        if json_path.exists():
            with json_path.open("r", encoding="utf-8") as f:
                messages = json.load(f)
                # Find the last user message with non-empty content (iterate backwards)
                for msg in reversed(messages):
                    if msg.get("role") == "user":
                        content = msg.get("content", "").strip()
                        if content:  # Only use if content is not empty
                            # Truncate to fit in one line (max 80 chars)
                            if len(content) > 80:
                                last_user_message = content[:77] + "..."
                            else:
                                last_user_message = content
                            break
    except Exception:
        pass

    return timestamp, message_count, last_user_message


class AutosavePicker(ModalScreen):
    """Modal to present available autosave sessions for selection."""

    DEFAULT_CSS = """
    AutosavePicker {
        align: center middle;
    }

    #modal-container {
        width: 80%;
        max-width: 100;
        height: 24;
        min-height: 18;
        background: rgba(46, 52, 64, 0.5);
        border: solid $primary;
        padding: 1 2;
        layout: vertical;
    }

    #list-label {
        width: 100%;
        height: 1;
        color: $text;
        text-align: left;
    }

    #autosave-list {
        height: 1fr;
        overflow: auto;
        border: solid $primary-darken-2;
        background: transparent;
        margin: 1 0;
    }

    .button-row {
        height: 3;
        align-horizontal: right;
        margin-top: 1;
    }

    #cancel-button { background: $primary-darken-1; }
    #load-button { background: $success; }
    """

    def __init__(self, autosave_dir: Path, **kwargs):
        super().__init__(**kwargs)
        self.autosave_dir = autosave_dir
        self.entries: List[AutosaveEntry] = []
        self.list_view: Optional[ListView] = None

    def on_mount(self) -> None:
        names = list_sessions(self.autosave_dir)
        raw_entries: List[Tuple[str, Optional[str], Optional[int], Optional[str]]] = []
        for name in names:
            ts, count, last_msg = _load_metadata(self.autosave_dir, name)
            raw_entries.append((name, ts, count, last_msg))

        def sort_key(entry):
            _, ts, _, _ = entry
            if ts:
                try:
                    return datetime.fromisoformat(ts)
                except ValueError:
                    return datetime.min
            return datetime.min

        raw_entries.sort(key=sort_key, reverse=True)
        self.entries = [AutosaveEntry(*e) for e in raw_entries]

        # Populate the ListView now that entries are ready
        if self.list_view is None:
            try:
                self.list_view = self.query_one("#autosave-list", ListView)
            except Exception:
                self.list_view = None

        if self.list_view is not None:
            # Clear existing items if any
            try:
                self.list_view.clear()
            except Exception:
                # Fallback: remove children manually
                self.list_view.children.clear()  # type: ignore

            for entry in self.entries[:50]:
                # Format timestamp as date/time
                if entry.timestamp:
                    try:
                        dt = datetime.fromisoformat(entry.timestamp.replace("Z", "+00:00"))
                        ts_display = dt.strftime("%Y-%m-%d %H:%M")
                    except Exception:
                        ts_display = entry.timestamp
                else:
                    ts_display = "unknown time"

                count = (
                    f"{entry.message_count} msgs"
                    if entry.message_count is not None
                    else "unknown"
                )

                # Build label with timestamp, message count, and last user message
                if entry.last_user_message:
                    label = f"{ts_display} | {count} | {entry.last_user_message}"
                else:
                    label = f"{ts_display} | {count}"
                self.list_view.append(ListItem(Static(label)))

            # Focus and select first item for better UX
            if len(self.entries) > 0:
                self.list_view.index = 0
                self.list_view.focus()

    def compose(self) -> ComposeResult:
        with Container(id="modal-container"):
            yield Label("Select a session to resume (Esc to cancel)", id="list-label")
            self.list_view = ListView(id="autosave-list")
            # populate items
            for entry in self.entries[:50]:  # cap to avoid long lists
                # Format timestamp as date/time
                if entry.timestamp:
                    try:
                        dt = datetime.fromisoformat(entry.timestamp.replace("Z", "+00:00"))
                        ts_display = dt.strftime("%Y-%m-%d %H:%M")
                    except Exception:
                        ts_display = entry.timestamp
                else:
                    ts_display = "unknown time"

                count = (
                    f"{entry.message_count} msgs"
                    if entry.message_count is not None
                    else "unknown"
                )

                # Build label with timestamp, message count, and last user message
                if entry.last_user_message:
                    label = f"{ts_display} | {count} | {entry.last_user_message}"
                else:
                    label = f"{ts_display} | {count}"
                self.list_view.append(ListItem(Static(label)))
            yield self.list_view
            with Horizontal(classes="button-row"):
                yield Button("Cancel", id="cancel-button")
                yield Button("Load", id="load-button", variant="primary")

    @on(Button.Pressed, "#cancel-button")
    def cancel(self) -> None:
        self.dismiss(None)

    @on(Button.Pressed, "#load-button")
    def load_selected(self) -> None:
        if not self.list_view or not self.entries:
            self.dismiss(None)
            return
        idx = self.list_view.index if self.list_view.index is not None else 0
        if 0 <= idx < len(self.entries):
            self.dismiss(self.entries[idx].name)
        else:
            self.dismiss(None)

    def on_list_view_selected(self, event: ListView.Selected) -> None:  # type: ignore
        # Double-enter may select; we just map to load button
        self.load_selected()
