"""
Modal component for viewing images.
"""

from pathlib import Path
from textual import on
from textual.app import ComposeResult
from textual.containers import Container, Horizontal, VerticalScroll
from textual.events import Key
from textual.screen import ModalScreen
from textual.widgets import Button, Static


class ImageViewerModal(ModalScreen):
    """Modal for viewing image files."""

    def __init__(self, file_path: Path, **kwargs):
        """Initialize the modal with image information.

        Args:
            file_path: Path to the image file to view
            **kwargs: Additional arguments to pass to the parent class
        """
        super().__init__(**kwargs)
        self.file_path = file_path

    DEFAULT_CSS = """
    ImageViewerModal {
        align: center middle;
        background: transparent;
    }

    #viewer-container {
        width: 90%;
        max-width: 120;
        height: 85%;
        min-height: 30;
        background: $surface;
        border: solid $primary;
        padding: 1 2;
        layout: vertical;
    }

    #image-title {
        width: 100%;
        margin-bottom: 1;
        color: $accent;
        text-align: center;
        text-style: bold;
        height: 1;
    }

    #image-scroll {
        width: 100%;
        height: 1fr;
        border: solid $primary;
        background: transparent;
        margin-bottom: 1;
        align: center top;
    }

    #image-content {
        width: auto;
        height: auto;
        background: transparent;
    }

    #button-container {
        width: 100%;
        height: 3;
        align: center bottom;
        layout: horizontal;
    }

    #close-button {
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

    #close-button:hover {
        border: wide $accent-lighten-1;
        border-bottom: wide $accent-darken-1;
        border-right: wide $accent-darken-1;
        background: $primary-lighten-1;
        color: $background;
    }

    #close-button:focus {
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

    def compose(self) -> ComposeResult:
        """Create the modal layout."""
        with Container(id="viewer-container"):
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

            yield Static(f"Viewing: {display_path}", id="image-title")
            with VerticalScroll(id="image-scroll"):
                # Create a Static widget that will render the image
                image_widget = Static(id="image-content")
                # Load and render the image
                try:
                    # Textual can render images directly from file paths
                    from rich.console import RenderableType
                    from textual.widgets import Static as TextualStatic

                    # Use a simple text representation for now
                    # We'll try to load the actual image content
                    image_widget.update(f"[Image: {self.file_path.name}]")
                except Exception as e:
                    image_widget.update(f"Error loading image: {e}")

                yield image_widget
            with Horizontal(id="button-container"):
                yield Button("Close", id="close-button")
            yield Static("Escape to close", id="hint-text")

    def on_mount(self) -> None:
        """Load and display the image when modal opens."""
        try:
            image_widget = self.query_one("#image-content", Static)

            # Display image metadata and helpful info
            try:
                from PIL import Image as PILImage
                from rich.table import Table
                from rich.panel import Panel
                from rich.text import Text

                # Load image to get metadata
                pil_img = PILImage.open(self.file_path)
                width, height = pil_img.size

                # Get file size
                file_size = self.file_path.stat().st_size
                if file_size < 1024:
                    size_str = f"{file_size} bytes"
                elif file_size < 1024 * 1024:
                    size_str = f"{file_size / 1024:.2f} KB"
                else:
                    size_str = f"{file_size / (1024 * 1024):.2f} MB"

                # Calculate aspect ratio
                from math import gcd
                divisor = gcd(width, height)
                aspect_w = width // divisor
                aspect_h = height // divisor

                # Create a nice table with image info
                table = Table(show_header=False, box=None, padding=(0, 2))
                table.add_column("Property", style="#88c0d0")
                table.add_column("Value", style="#d8dee9")

                table.add_row("📷 File", f"[bold]{self.file_path.name}[/]")
                table.add_row("📁 Location", str(self.file_path.parent))
                table.add_row("🎨 Format", pil_img.format or "Unknown")
                table.add_row("📐 Dimensions", f"{width} × {height} pixels")
                table.add_row("📊 Aspect Ratio", f"{aspect_w}:{aspect_h}")
                table.add_row("🎭 Color Mode", pil_img.mode)
                table.add_row("💾 File Size", size_str)

                # Add color palette info for palette-based images
                if pil_img.mode == "P" and pil_img.palette:
                    table.add_row("🎨 Palette", f"{len(pil_img.palette.palette) // 3} colors")

                # Create tip text
                tip_text = Text()
                tip_text.append("\n💡 Tip: ", style="bold #88c0d0")
                tip_text.append("Use your system's image viewer to see the full image:\n", style="#d8dee9")
                tip_text.append(f"  xdg-open '{self.file_path}'\n", style="dim #81a1c1")
                tip_text.append(f"  or: open '{self.file_path}'  (macOS)", style="dim #81a1c1")

                # Combine table and tip
                from rich.console import Group
                content = Group(table, tip_text)

                image_widget.update(content)

            except ImportError:
                # PIL not available
                file_size = self.file_path.stat().st_size
                if file_size < 1024:
                    size_str = f"{file_size} bytes"
                elif file_size < 1024 * 1024:
                    size_str = f"{file_size / 1024:.2f} KB"
                else:
                    size_str = f"{file_size / (1024 * 1024):.2f} MB"

                image_widget.update(
                    f"📷 [bold #88c0d0]{self.file_path.name}[/]\n\n"
                    f"[#d8dee9]File size: {size_str}[/]\n\n"
                    f"[dim #81a1c1]Install Pillow for image metadata:\n"
                    f"pip install pillow[/]"
                )
            except Exception as e:
                image_widget.update(f"[#bf616a]Error loading image: {e}[/]")

        except Exception as e:
            print(f"ImageViewerModal on_mount exception: {e}")

    @on(Button.Pressed, "#close-button")
    def on_close_clicked(self) -> None:
        """Handle close button click."""
        self._close_modal()

    def on_key(self, event: Key) -> None:
        """Handle key events."""
        if event.key == "escape":
            self._close_modal()
            event.prevent_default()

    def _close_modal(self) -> None:
        """Close the modal."""
        self.dismiss()
