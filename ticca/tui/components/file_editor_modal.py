"""
Modal component for editing files.
"""

from pathlib import Path
from textual import on
from textual.app import ComposeResult
from textual.containers import Container, Horizontal
from textual.events import Key
from textual.screen import ModalScreen
from textual.widgets import Button, Static, TextArea

try:
    from .custom_widgets import CustomTextArea
except ImportError:
    # Fallback to regular TextArea if CustomTextArea isn't available
    CustomTextArea = TextArea


class FileEditorModal(ModalScreen):
    """Modal for editing file contents."""

    def __init__(self, file_path: Path, **kwargs):
        """Initialize the modal with file information.

        Args:
            file_path: Path to the file to edit
            **kwargs: Additional arguments to pass to the parent class
        """
        super().__init__(**kwargs)
        self.file_path = file_path
        self.original_content = ""
        self.load_file_content()

    DEFAULT_CSS = """
    FileEditorModal {
        align: center middle;
        background: transparent;
    }

    #editor-container {
        width: 90%;
        max-width: 120;
        height: 80%;
        min-height: 30;
        background: $surface;
        border: solid $primary;
        padding: 1 2;
        layout: vertical;
    }

    #file-title {
        width: 100%;
        margin-bottom: 0;
        color: $accent;
        text-align: center;
        text-style: bold;
        height: 1;
    }

    #file-info {
        width: 100%;
        margin-bottom: 1;
        color: $primary-lighten-1;
        text-align: center;
        height: 1;
        text-style: dim italic;
    }

    #editor-text-area {
        width: 100%;
        height: 1fr;
        border: none;
        margin-bottom: 1;
    }

    #button-container {
        width: 100%;
        height: 3;
        align: center bottom;
        layout: horizontal;
    }

    #save-button, #cancel-button {
        width: auto;
        height: 3;
        margin: 0 1;
        min-width: 15;
        content-align: center middle;
        border: wide $accent;
        border-bottom: wide $accent-darken-1;
        border-right: wide $accent-darken-1;
        background: $primary;
        color: $background;
        text-style: bold;
    }

    #save-button:hover, #cancel-button:hover {
        border: wide $accent-lighten-1;
        border-bottom: wide $accent-darken-1;
        border-right: wide $accent-darken-1;
        background: $primary-lighten-1;
        color: $background;
    }

    #save-button:focus, #cancel-button:focus {
        border: wide $accent-darken-1;
        border-top: wide $accent;
        border-left: wide $accent;
        background: $primary-darken-1;
        color: $accent;
    }

    #hint-text {
        width: 100%;
        color: $text;
        text-align: center;
        height: 1;
        margin-top: 1;
        text-style: italic dim;
    }
    """

    def load_file_content(self) -> None:
        """Load the file content."""
        try:
            # Try UTF-8 first, then fall back to latin-1
            try:
                self.original_content = self.file_path.read_text(encoding='utf-8')
            except UnicodeDecodeError:
                self.original_content = self.file_path.read_text(encoding='latin-1')
        except Exception as e:
            self.original_content = f"Error loading file: {e}"

    def _detect_language(self) -> str:
        """Detect the language based on file extension.

        Returns a language name supported by Textual's TextArea.
        Available: bash, css, go, html, java, javascript, json, markdown,
                   python, regex, rust, sql, toml, xml, yaml
        """
        suffix = self.file_path.suffix.lower()
        language_map = {
            # Python
            ".py": "python",
            ".pyw": "python",
            # JavaScript/TypeScript (TypeScript not supported, fall back to javascript)
            ".js": "javascript",
            ".mjs": "javascript",
            ".cjs": "javascript",
            ".ts": "javascript",  # TypeScript -> JavaScript highlighting
            ".tsx": "javascript",
            ".jsx": "javascript",
            # Markup
            ".json": "json",
            ".md": "markdown",
            ".markdown": "markdown",
            ".yaml": "yaml",
            ".yml": "yaml",
            ".toml": "toml",
            ".css": "css",
            ".html": "html",
            ".htm": "html",
            ".xml": "xml",
            # Shell
            ".sh": "bash",
            ".bash": "bash",
            ".zsh": "bash",
            # Other languages
            ".rs": "rust",
            ".go": "go",
            ".java": "java",
            ".sql": "sql",
            # Regex
            ".re": "regex",
        }
        return language_map.get(suffix, None)  # Return None for unsupported

    def compose(self) -> ComposeResult:
        """Create the modal layout."""
        language = self._detect_language()

        # Get file size
        try:
            file_size = self.file_path.stat().st_size
            if file_size < 1024:
                size_str = f"{file_size} bytes"
            elif file_size < 1024 * 1024:
                size_str = f"{file_size / 1024:.1f} KB"
            else:
                size_str = f"{file_size / (1024 * 1024):.2f} MB"
        except Exception:
            size_str = "Unknown size"

        # Get line count
        try:
            line_count = len(self.original_content.splitlines())
        except Exception:
            line_count = 0

        with Container(id="editor-container"):
            # Show relative path from current working directory
            try:
                from pathlib import Path
                import os
                cwd = Path(os.getcwd())
                rel_path = self.file_path.relative_to(cwd)
                display_path = f"./{rel_path}"
            except (ValueError, Exception):
                # If not relative to cwd, show absolute path
                display_path = str(self.file_path)

            yield Static(f"Editing: {display_path}", id="file-title")

            # Show language info
            lang_display = language.title() if language else "Plain Text"
            yield Static(
                f"Language: {lang_display} • Size: {size_str} • Lines: {line_count}",
                id="file-info"
            )

            # Create TextArea with or without syntax highlighting
            if language:
                # Syntax highlighting available
                text_area = TextArea(
                    self.original_content,
                    id="editor-text-area",
                    language=language,
                    theme="monokai",  # Use monokai theme for better highlighting
                    show_line_numbers=True
                )
            else:
                # No syntax highlighting for this file type
                text_area = TextArea(
                    self.original_content,
                    id="editor-text-area",
                    show_line_numbers=True
                )

            yield text_area

            with Horizontal(id="button-container"):
                yield Button("Save", id="save-button")
                yield Button("Cancel", id="cancel-button")
            yield Static("Ctrl+S to save • Escape to cancel", id="hint-text")

    def on_mount(self) -> None:
        """Focus the editor when modal opens."""
        try:
            editor = self.query_one("#editor-text-area", TextArea)
            editor.focus()
        except Exception as e:
            print(f"FileEditorModal on_mount exception: {e}")

    @on(Button.Pressed, "#save-button")
    def on_save_clicked(self) -> None:
        """Handle save button click."""
        self._save_file()

    @on(Button.Pressed, "#cancel-button")
    def on_cancel_clicked(self) -> None:
        """Handle cancel button click."""
        self._close_modal()

    def on_key(self, event: Key) -> None:
        """Handle key events."""
        if event.key == "escape":
            self._close_modal()
            event.prevent_default()
        elif event.key == "ctrl+s":
            self._save_file()
            event.prevent_default()

    def _save_file(self) -> None:
        """Save the file content."""
        try:
            editor = self.query_one("#editor-text-area", TextArea)
            content = editor.text

            # Write the file with UTF-8 encoding
            self.file_path.write_text(content, encoding='utf-8')

            # Show success message
            from ticca.messaging import emit_info
            file_size = self.file_path.stat().st_size
            if file_size < 1024:
                size_str = f"{file_size} bytes"
            elif file_size < 1024 * 1024:
                size_str = f"{file_size / 1024:.1f} KB"
            else:
                size_str = f"{file_size / (1024 * 1024):.2f} MB"
            emit_info(f"✓ Saved: {self.file_path.name} ({size_str})")

            # Close the modal
            self.dismiss()
        except Exception as e:
            from ticca.messaging import emit_error
            emit_error(f"Error saving file: {e}")

    def _close_modal(self) -> None:
        """Close the modal without saving."""
        self.dismiss()
