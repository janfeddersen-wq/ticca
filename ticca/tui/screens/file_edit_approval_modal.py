"""
File Edit Approval modal with side-by-side diff view for TUI mode.
"""

import difflib
from textual import on
from textual.app import ComposeResult
from textual.containers import Container, Horizontal, Vertical, VerticalScroll
from textual.screen import ModalScreen
from textual.widgets import Button, Input, Label, Static


class FileEditApprovalModal(ModalScreen):
    """Modal screen for approving file edits with VSCode-like side-by-side diff view."""

    DEFAULT_CSS = """
    FileEditApprovalModal {
        align: center middle;
    }

    #file-edit-dialog {
        width: 95%;
        height: 90%;
        border: round $primary;
        background: $surface;
        padding: 1 2;
    }

    #file-edit-title {
        text-align: center;
        text-style: bold;
        color: $accent;
        margin: 0 0 1 0;
    }

    #file-path-label {
        text-align: center;
        color: $text;
        margin: 0 0 1 0;
    }

    #diff-scroll-container {
        width: 100%;
        height: 1fr;
        margin: 0 0 1 0;
        overflow-y: auto;
        overflow-x: hidden;
    }

    #diff-container {
        width: 100%;
        height: auto;
        layout: horizontal;
    }

    #old-content-panel {
        width: 1fr;
        height: auto;
        border: round $error;
        border-title-color: $error;
        border-title-style: bold;
        margin: 0 1;
        background: $panel;
    }

    #new-content-panel {
        width: 1fr;
        height: auto;
        border: round $success;
        border-title-color: $success;
        border-title-style: bold;
        margin: 0 1;
        background: $panel;
    }

    .file-content {
        width: 100%;
        height: auto;
        padding: 0 1;
    }

    #old-file-content, #new-file-content {
        width: 100%;
        height: auto;
    }

    #action-buttons {
        layout: horizontal;
        height: 3;
        align: center middle;
        margin: 1 0 0 0;
    }

    #approve-btn, #reject-btn, #feedback-btn {
        margin: 0 1;
        min-width: 15;
        height: 3;
    }

    #approve-btn {
        border: wide $success;
        background: $success;
        color: $background;
    }

    #approve-btn:hover {
        border: wide $success;
        background: $success-darken-1;
    }

    #reject-btn {
        border: wide $error;
        background: $error;
        color: $background;
    }

    #reject-btn:hover {
        border: wide $error;
        background: $error-darken-1;
    }

    #feedback-btn {
        border: wide $warning;
        background: $warning;
        color: $background;
    }

    #feedback-btn:hover {
        border: wide $warning;
        background: $warning-darken-1;
    }

    #feedback-container {
        display: none;
        margin: 1 0 0 0;
    }

    #feedback-container.visible {
        display: block;
    }

    #feedback-input {
        width: 100%;
        margin: 1 0;
    }

    #submit-feedback-btn {
        width: 100%;
        height: 3;
        border: wide $accent;
        background: $primary;
        color: $background;
    }
    """

    def __init__(
        self,
        file_path: str,
        old_content: str,
        new_content: str,
        **kwargs
    ):
        super().__init__(**kwargs)
        self.file_path = file_path
        self.old_content = old_content or ""
        self.new_content = new_content or ""
        self.result = {"approved": False, "feedback": None}

    def compose(self) -> ComposeResult:
        with Container(id="file-edit-dialog"):
            yield Label("📝 File Edit Approval", id="file-edit-title")
            yield Label(f"📄 {self.file_path}", id="file-path-label")

            # Single scroll container for both panels
            with VerticalScroll(id="diff-scroll-container") as scroll_widget:
                with Horizontal(id="diff-container"):
                    # Old content panel with border title
                    old_panel = Vertical(id="old-content-panel")
                    old_panel.border_title = "OLD"
                    with old_panel:
                        yield Static(
                            self._render_full_file(self.old_content, is_old=True),
                            classes="file-content",
                            id="old-file-content"
                        )

                    # New content panel with border title
                    new_panel = Vertical(id="new-content-panel")
                    new_panel.border_title = "NEW"
                    with new_panel:
                        yield Static(
                            self._render_full_file(self.new_content, is_old=False),
                            classes="file-content",
                            id="new-file-content"
                        )

            # Action buttons
            with Container(id="action-buttons"):
                yield Button("✓ Approve", id="approve-btn", variant="success")
                yield Button("✗ Reject", id="reject-btn", variant="error")
                yield Button("💬 Reject with Feedback", id="feedback-btn", variant="warning")

            # Feedback input (hidden by default)
            with Vertical(id="feedback-container"):
                yield Label("Provide feedback to the agent:")
                yield Input(
                    placeholder="Tell the agent what to change...",
                    id="feedback-input"
                )
                yield Button("Submit Feedback", id="submit-feedback-btn")

    def _render_full_file(self, content: str, is_old: bool) -> str:
        """Render the complete file with VSCode-like diff highlighting.

        This shows the FULL file content with line numbers and highlights changes.
        Both sides are padded to the same height for synchronized scrolling.

        Args:
            content: Complete file content to render
            is_old: True if this is the old/original content, False for new

        Returns:
            Rendered content with Rich markup for diff highlighting
        """
        if not content and not (self.old_content or self.new_content):
            return "[dim italic]  (empty file)[/dim italic]"

        old_lines = self.old_content.splitlines() if self.old_content else []
        new_lines = self.new_content.splitlines() if self.new_content else []

        # Use SequenceMatcher to get precise line-by-line diff information
        matcher = difflib.SequenceMatcher(None, old_lines, new_lines)

        # Build aligned line mappings for VSCode-style sync scrolling
        # Each side gets a list of (line_number, line_content, is_deleted, is_added, is_changed)
        old_aligned = []
        new_aligned = []

        for tag, i1, i2, j1, j2 in matcher.get_opcodes():
            if tag == 'equal':
                # Same lines on both sides
                for i in range(i2 - i1):
                    old_aligned.append((i1 + i + 1, old_lines[i1 + i], False, False, False))
                    new_aligned.append((j1 + i + 1, new_lines[j1 + i], False, False, False))
            elif tag == 'replace':
                # Changed lines - pad to equal length
                old_count = i2 - i1
                new_count = j2 - j1
                max_count = max(old_count, new_count)

                for idx in range(max_count):
                    if idx < old_count:
                        old_aligned.append((i1 + idx + 1, old_lines[i1 + idx], False, False, True))
                    else:
                        old_aligned.append((None, "", False, False, False))  # Padding

                    if idx < new_count:
                        new_aligned.append((j1 + idx + 1, new_lines[j1 + idx], False, False, True))
                    else:
                        new_aligned.append((None, "", False, False, False))  # Padding
            elif tag == 'delete':
                # Lines only in old - show as deleted on old side, empty on new side
                for i in range(i1, i2):
                    old_aligned.append((i + 1, old_lines[i], True, False, False))
                    new_aligned.append((None, "", False, False, False))  # Empty padding on new side
            elif tag == 'insert':
                # Lines only in new - show as added on new side, empty on old side
                for j in range(j1, j2):
                    old_aligned.append((None, "", False, False, False))  # Empty padding on old side
                    new_aligned.append((j + 1, new_lines[j], False, True, False))

        # Calculate wrap width for each side (accounting for line numbers and prefixes)
        # Assuming roughly 50% width each, minus borders/padding
        # A safe estimate is ~80 characters per line
        WRAP_WIDTH = 80

        # Pre-wrap all lines and build aligned pairs with equal visual line counts
        old_wrapped = []
        new_wrapped = []

        for idx, (old_item, new_item) in enumerate(zip(old_aligned, new_aligned)):
            old_ln, old_content, old_del, old_add, old_chg = old_item
            new_ln, new_content, new_del, new_add, new_chg = new_item

            # Wrap each side's content
            old_lines = self._wrap_line(old_content, WRAP_WIDTH) if old_content else [""]
            new_lines = self._wrap_line(new_content, WRAP_WIDTH) if new_content else [""]

            # Ensure both sides have the same number of wrapped lines
            max_wrapped = max(len(old_lines), len(new_lines))
            old_lines.extend([""] * (max_wrapped - len(old_lines)))
            new_lines.extend([""] * (max_wrapped - len(new_lines)))

            # Add wrapped lines to the aligned lists
            for i, (old_wrap, new_wrap) in enumerate(zip(old_lines, new_lines)):
                # Only show line number on the first wrapped line
                show_old_ln = old_ln if i == 0 else None
                show_new_ln = new_ln if i == 0 else None

                old_wrapped.append((show_old_ln, old_wrap, old_del, old_add, old_chg))
                new_wrapped.append((show_new_ln, new_wrap, new_del, new_add, new_chg))

        # Render the appropriate side
        wrapped = old_wrapped if is_old else new_wrapped

        # Get max line number from the original aligned list (before wrapping)
        aligned_source = old_aligned if is_old else new_aligned
        max_line_num = max((ln for ln, _, _, _, _ in aligned_source if ln), default=0)
        max_line_num_width = len(str(max_line_num)) if max_line_num > 0 else 1

        rendered = []
        for line_num, line_content, is_deleted, is_added, is_changed in wrapped:
            # Escape any Rich markup in the line content
            escaped_line = line_content.replace("[", "\\[") if line_content else ""

            if line_num is None:
                # Padding line (empty space to align with other side) or continuation
                rendered.append(
                    f"[dim]{' ' * max_line_num_width}[/dim]  "
                    f"[dim]{escaped_line}[/dim]"
                )
            elif is_deleted:
                # Deleted line - red background
                line_num_str = str(line_num).rjust(max_line_num_width)
                rendered.append(
                    f"[bold red]{line_num_str}[/bold red] "
                    f"[on #3d0000][red]- {escaped_line}[/red][/on #3d0000]"
                )
            elif is_added:
                # Added line - green background
                line_num_str = str(line_num).rjust(max_line_num_width)
                rendered.append(
                    f"[bold green]{line_num_str}[/bold green] "
                    f"[on #003d00][green]+ {escaped_line}[/green][/on #003d00]"
                )
            elif is_changed:
                # Changed line
                line_num_str = str(line_num).rjust(max_line_num_width)
                if is_old:
                    rendered.append(
                        f"[dim]{line_num_str}[/dim] "
                        f"[on #3d0000][dim red]{escaped_line}[/dim red][/on #3d0000]"
                    )
                else:
                    rendered.append(
                        f"[dim]{line_num_str}[/dim] "
                        f"[on #003d00][dim green]{escaped_line}[/dim green][/on #003d00]"
                    )
            else:
                # Unchanged context line
                line_num_str = str(line_num).rjust(max_line_num_width)
                rendered.append(
                    f"[dim blue]{line_num_str}[/dim blue] "
                    f"[dim]{escaped_line}[/dim]"
                )

        return "\n".join(rendered)

    def _wrap_line(self, line: str, width: int) -> list[str]:
        """Wrap a line to a maximum width, breaking at word boundaries.

        Args:
            line: The line to wrap
            width: Maximum width in characters

        Returns:
            List of wrapped lines
        """
        if not line or len(line) <= width:
            return [line]

        words = line.split()
        wrapped = []
        current = []
        current_len = 0

        for word in words:
            word_len = len(word)
            # +1 for the space
            if current and current_len + word_len + 1 > width:
                wrapped.append(" ".join(current))
                current = [word]
                current_len = word_len
            else:
                current.append(word)
                current_len += word_len + (1 if current_len > 0 else 0)

        if current:
            wrapped.append(" ".join(current))

        return wrapped if wrapped else [line]

    @on(Button.Pressed, "#approve-btn")
    def approve(self) -> None:
        """Approve the file edit."""
        self.result = {"approved": True, "feedback": None}
        self.dismiss(self.result)

    @on(Button.Pressed, "#reject-btn")
    def reject(self) -> None:
        """Reject the file edit."""
        self.result = {"approved": False, "feedback": None}
        self.dismiss(self.result)

    @on(Button.Pressed, "#feedback-btn")
    def show_feedback_input(self) -> None:
        """Show feedback input."""
        feedback_container = self.query_one("#feedback-container")
        feedback_container.add_class("visible")

        # Hide buttons
        self.query_one("#action-buttons").display = False

        # Focus input
        self.query_one("#feedback-input", Input).focus()

    @on(Button.Pressed, "#submit-feedback-btn")
    def submit_feedback(self) -> None:
        """Submit feedback and reject."""
        feedback = self.query_one("#feedback-input", Input).value.strip()
        self.result = {
            "approved": False,
            "feedback": feedback if feedback else None
        }
        self.dismiss(self.result)

    def on_mount(self) -> None:
        """Focus the scroll container when mounted."""
        try:
            scroll = self.query_one("#diff-scroll-container")
            scroll.focus()
        except Exception:
            pass

    def on_key(self, event) -> None:
        """Handle key events."""
        if event.key == "escape":
            self.reject()
