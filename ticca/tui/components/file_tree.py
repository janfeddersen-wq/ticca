"""
File tree panel component for the left sidebar.
"""

from pathlib import Path
from textual import on
from textual.widgets import DirectoryTree, Static
from textual.containers import Container
from textual.app import ComposeResult
from textual.message import Message


class FileTreePanel(Container):
    """Left sidebar panel showing file/folder tree."""

    DEFAULT_CSS = """
    FileTreePanel {
        dock: left;
        width: 30;
        min-width: 25;
        max-width: 45;
        background: $background;
        border-right: solid $panel;
        padding: 0;
    }

    FileTreePanel DirectoryTree {
        background: $background;
        padding: 1;
        scrollbar-background: transparent;
        scrollbar-color: $primary;
        scrollbar-color-hover: $primary-lighten-1;
        scrollbar-color-active: $accent;
        scrollbar-size: 1 1;
    }

    FileTreePanel DirectoryTree:focus {
        background: $background;
    }

    /* Style for selected/highlighted items */
    FileTreePanel .tree--cursor {
        background: $secondary;
        color: $text;
    }

    FileTreePanel .tree--highlight {
        background: $border;
        color: $accent;
    }

    FileTreePanel .tree--cursor.tree--highlight {
        background: $primary;
        color: $text;
        text-style: bold;
    }
    """

    def __init__(self, working_directory: str = ".", **kwargs):
        """Initialize file tree panel.

        Args:
            working_directory: Directory to display
            **kwargs: Additional keyword arguments
        """
        super().__init__(**kwargs)
        self.working_directory = working_directory
        self.id = "file-tree-panel"

    def compose(self) -> ComposeResult:
        """Compose the file tree panel.

        Yields:
            Child widgets
        """
        yield DirectoryTree(self.working_directory, id="file-tree")

    def get_tree(self) -> DirectoryTree:
        """Get the directory tree widget.

        Returns:
            DirectoryTree widget
        """
        return self.query_one("#file-tree", DirectoryTree)

    def refresh_tree(self, new_directory: str | None = None) -> None:
        """Refresh the file tree.

        Args:
            new_directory: Optional new directory to display
        """
        if new_directory:
            self.working_directory = new_directory

        tree = self.get_tree()
        tree.path = self.working_directory
        tree.reload()

    def get_selected_path(self) -> Path | None:
        """Get the currently selected file/folder path.

        Returns:
            Selected path or None
        """
        tree = self.get_tree()
        if tree.cursor_node:
            return tree.cursor_node.data.path
        return None

    @on(DirectoryTree.FileSelected)
    def on_file_selected(self, event: DirectoryTree.FileSelected) -> None:
        """Handle file selection (double-click opens editor).

        Args:
            event: File selected event
        """
        # Post a message to the parent to open the file editor
        self.post_message(self.FileDoubleClicked(event.path))

    class FileDoubleClicked(Message):
        """File was double-clicked in the tree."""

        def __init__(self, path: Path) -> None:
            """Initialize the message.

            Args:
                path: Path to the file that was double-clicked
            """
            self.path = path
            super().__init__()
