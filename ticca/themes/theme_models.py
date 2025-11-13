"""
Theme data models for Ticca TUI.

Defines the structure of theme configuration with all color variables
used throughout the application.
"""

from dataclasses import dataclass, asdict
from typing import Dict
import json


@dataclass
class Theme:
    """Complete theme definition with all color variables."""

    # Basic theme info
    name: str
    display_name: str

    # Background colors
    background: str  # Main background
    background_dark: str  # Darker background (for containers)
    background_light: str  # Lighter background (for hover states)

    # Foreground/Text colors
    foreground: str  # Primary text color
    foreground_muted: str  # Dimmed/secondary text
    foreground_bright: str  # Highlighted/bright text

    # Accent colors
    primary: str  # Primary accent color
    primary_light: str  # Lighter primary (hover states)
    primary_dark: str  # Darker primary (borders)

    # UI element colors
    panel: str  # Panel background
    panel_light: str  # Panel hover
    border: str  # Border color

    # Scrollbar colors
    scrollbar: str  # Scrollbar color
    scrollbar_hover: str  # Scrollbar hover
    scrollbar_active: str  # Scrollbar active/pressed

    # Status colors
    success: str  # Success messages/states
    warning: str  # Warning messages/states
    error: str  # Error messages/states
    info: str  # Info messages/states

    # Message type colors
    user_message: str  # User message text
    agent_message: str  # Agent response text
    system_message: str  # System message text
    reasoning_message: str  # Agent reasoning text
    tool_output: str  # Tool output text
    command_output: str  # Command output text

    # Button colors
    button_background: str
    button_hover: str
    button_active: str
    button_text: str
    button_border: str
    button_border_light: str
    button_border_dark: str

    # Modal/overlay colors
    modal_background: str  # Modal container background
    modal_overlay: str  # Semi-transparent overlay

    # Diff colors
    diff_addition: str  # Color for diff additions
    diff_deletion: str  # Color for diff deletions

    def to_dict(self) -> Dict[str, str]:
        """Convert theme to dictionary."""
        return asdict(self)

    def to_json(self) -> str:
        """Convert theme to JSON string."""
        return json.dumps(self.to_dict(), indent=2)

    @classmethod
    def from_dict(cls, data: Dict[str, str]) -> "Theme":
        """Create theme from dictionary."""
        return cls(**data)

    @classmethod
    def from_json(cls, json_str: str) -> "Theme":
        """Create theme from JSON string."""
        data = json.loads(json_str)
        return cls.from_dict(data)

    def to_css_variables(self) -> str:
        """
        Generate CSS variable definitions for use in Textual CSS.
        Returns a string that can be included in DEFAULT_CSS.
        """
        css_lines = []
        for key, value in self.to_dict().items():
            if key not in ('name', 'display_name'):
                # Convert snake_case to kebab-case for CSS variables
                css_var = key.replace('_', '-')
                css_lines.append(f"    ${css_var}: {value};")

        return "\n".join(css_lines)
