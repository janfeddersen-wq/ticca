"""
Collapsible widget for thinking messages (agent reasoning and planned next steps).
"""

from textual.containers import Container
from textual.widgets import Static
from textual.reactive import reactive


class CollapsibleThinking(Container):
    """A collapsible container for thinking messages."""

    DEFAULT_CSS = """
    CollapsibleThinking {
        width: 1fr;
        height: auto;
        margin: 1 0;
        border: round $border;
        background: transparent;
    }

    CollapsibleThinking .thinking-header {
        width: 1fr;
        height: auto;
        padding: 0 2;
        background: $panel;
        color: $text;
        text-style: bold;
    }

    CollapsibleThinking .thinking-header:hover {
        background: $primary;
        color: $background;
    }

    CollapsibleThinking .thinking-content {
        width: 1fr;
        height: auto;
        padding: 1 2;
        background: transparent;
        color: $text;
    }

    CollapsibleThinking.collapsed .thinking-content {
        display: none;
    }
    """

    collapsed = reactive(True)  # Start collapsed by default

    def __init__(self, title: str, content, **kwargs):
        super().__init__(**kwargs)
        self.title = title
        self.content_widget = content
        self.header_widget = None

    def compose(self):
        """Create the collapsible structure."""
        # Header with collapse indicator
        header_text = f"▶ {self.title}" if self.collapsed else f"▼ {self.title}"
        self.header_widget = Static(header_text, classes="thinking-header")
        yield self.header_widget

        # Content container with the content widget
        with Container(classes="thinking-content"):
            yield self.content_widget

    def on_mount(self):
        """Set initial collapsed state."""
        if self.collapsed:
            self.add_class("collapsed")
        else:
            self.remove_class("collapsed")

    def watch_collapsed(self, collapsed: bool):
        """React to collapsed state changes."""
        if collapsed:
            self.add_class("collapsed")
            if self.header_widget:
                self.header_widget.update(f"▶ {self.title}")
        else:
            self.remove_class("collapsed")
            if self.header_widget:
                self.header_widget.update(f"▼ {self.title}")

    def toggle(self):
        """Toggle the collapsed state."""
        self.collapsed = not self.collapsed

    def on_click(self, event):
        """Handle click events to toggle collapsed state."""
        # Check if click was on the header
        if hasattr(event, 'widget'):
            # Check if the clicked widget is the header or any of its children
            widget = event.widget
            # Walk up the widget tree to see if we're inside the header
            while widget is not None:
                if widget == self.header_widget:
                    self.toggle()
                    event.stop()
                    return
                if widget == self:
                    break
                widget = widget.parent
