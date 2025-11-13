"""
KITT-style scanner widget for thinking indicator.
"""

import random
from statistics import mean

from textual.app import ComposeResult
from textual.containers import Horizontal
from textual.widgets import Label, Sparkline
from textual.reactive import reactive


class KittScanner(Horizontal):
    """A KITT-style scanning indicator using Sparkline with dual scanners."""

    # Track animation state
    left_pos: reactive[int] = reactive(4)
    right_pos: reactive[int] = reactive(25)
    moving_inward: reactive[bool] = reactive(True)
    is_active: reactive[bool] = reactive(False)

    DEFAULT_CSS = """
    KittScanner {
        height: 1;
        width: auto;
    }

    KittScanner > Label {
        color: $text;
        margin: 0 1;
    }

    KittScanner > Sparkline {
        width: 1fr;
        height: 1;
        color: $accent;
    }
    """

    # Animation modes
    MODE_DUAL_WAVE = "dual_wave"
    MODE_STREAMING = "streaming"

    def __init__(self, message: str = "Ticca is thinking... ", **kwargs):
        """Initialize the KITT scanner."""
        super().__init__(**kwargs)
        self.message = message
        self._timer = None
        self.data_size = 50  # Will be updated based on actual width
        self.data = [0.0] * self.data_size

        # Randomly choose animation mode
        self.animation_mode = random.choice([self.MODE_DUAL_WAVE, self.MODE_STREAMING])

        # Streaming mode state
        random.seed()  # Reset seed for true randomness

    def compose(self) -> ComposeResult:
        """Compose the scanner widget."""
        yield Label(self.message, id="scanner-label")
        yield Sparkline(self.data, summary_function=max, id="scanner-sparkline")

    def on_mount(self) -> None:
        """Initialize when mounted."""
        self.sparkline = self.query_one("#scanner-sparkline", Sparkline)
        self.label = self.query_one("#scanner-label", Label)

    def on_resize(self) -> None:
        """Handle resize to update data size based on available width."""
        if hasattr(self, 'sparkline'):
            # Get the actual width of the sparkline widget
            width = self.sparkline.size.width
            if width > 0 and width != self.data_size:
                self.data_size = width
                self.data = [0.0] * self.data_size
                # Reset positions for dual wave mode
                self.left_pos = min(4, self.data_size // 4)
                self.right_pos = max(self.data_size - 5, 3 * self.data_size // 4)

    def start_scanning(self) -> None:
        """Start the KITT scanning animation."""
        if not self.is_active:
            self.is_active = True

            # Randomly choose animation mode each time
            self.animation_mode = random.choice([self.MODE_DUAL_WAVE, self.MODE_STREAMING])

            if self.animation_mode == self.MODE_DUAL_WAVE:
                # Initialize dual wave positions
                self.left_pos = min(4, self.data_size // 4)
                self.right_pos = max(self.data_size - 5, 3 * self.data_size // 4)
                self.moving_inward = True
            else:
                # Initialize streaming mode with random data
                self.data = [random.expovariate(1 / 3) for _ in range(self.data_size)]

            # Update at ~15 FPS for smooth animation
            self._timer = self.set_interval(1/15, self._update_scan)

    def stop_scanning(self) -> None:
        """Stop the scanning animation."""
        self.is_active = False
        if self._timer:
            self._timer.stop()
            self._timer = None
        # Clear the sparkline
        self.data = [0.0] * self.data_size
        if hasattr(self, 'sparkline'):
            self.sparkline.data = self.data

    def update_message(self, message: str) -> None:
        """Update the message displayed next to the scanner."""
        self.message = message
        if hasattr(self, 'label'):
            self.label.update(message)

    def _update_scan(self) -> None:
        """Update the scanner animation based on current mode."""
        if not self.is_active:
            return

        if self.animation_mode == self.MODE_DUAL_WAVE:
            self._update_dual_wave()
        else:
            self._update_streaming()

        # Update the sparkline widget
        if hasattr(self, 'sparkline'):
            self.sparkline.data = self.data

    def _update_streaming(self) -> None:
        """Update streaming animation - add new data at start, drop from end."""
        # Add new random value at the beginning
        new_value = random.expovariate(1 / 3)

        # Shift data: insert at beginning, drop the last value
        self.data = [new_value] + self.data[:-1]

    def _update_dual_wave(self) -> None:
        """Update dual wave animation - two peaks moving from edges to center and back."""
        # Generate dual KITT effect: two peaks moving from edges to center and back
        new_data = [0.0] * self.data_size

        # Helper function to add a wave peak with symmetrical fade
        def add_wave(position: int) -> None:
            """Add a wave at position with symmetrical fade on both sides.

            Creates pattern: ▂▄█▄▂

            Args:
                position: Center peak position
            """
            if 0 <= position < self.data_size:
                # Main peak (█)
                new_data[position] = max(new_data[position], 1.0)

                # Add symmetrical fade on both sides
                # ▂▄█▄▂
                fade_offsets = [
                    (-2, 0.35),  # ▂ (left)
                    (-1, 0.65),  # ▄ (left)
                    (1, 0.65),   # ▄ (right)
                    (2, 0.35),   # ▂ (right)
                ]

                for offset, fade_value in fade_offsets:
                    fade_pos = position + offset
                    if 0 <= fade_pos < self.data_size:
                        new_data[fade_pos] = max(new_data[fade_pos], fade_value)

        # Add left wave
        add_wave(self.left_pos)

        # Add right wave
        add_wave(self.right_pos)

        self.data = new_data

        # Move positions
        if self.moving_inward:
            # Moving towards center
            self.left_pos += 1
            self.right_pos -= 1

            # Check if they've met in the middle (leave at least 1 position apart)
            if self.left_pos >= self.right_pos:
                # Reverse direction
                self.moving_inward = False
                # Ensure they're at valid positions in the center
                center = self.data_size // 2
                self.left_pos = center
                self.right_pos = center
        else:
            # Moving towards edges
            self.left_pos -= 1
            self.right_pos += 1

            # Check if they've reached the edges (with wave space: 2 positions on each side)
            max_left = min(4, self.data_size // 4)
            min_right = max(self.data_size - 5, 3 * self.data_size // 4)

            if self.left_pos <= max_left or self.right_pos >= min_right:
                # Reverse direction
                self.moving_inward = True
                # Reset to edges (leaving space for full wave pattern)
                self.left_pos = max_left
                self.right_pos = min_right
