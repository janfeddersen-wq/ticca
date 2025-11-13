"""
Theme system for Ticca TUI.

This module provides a comprehensive theming system with support for multiple
pre-defined themes and user customization.
"""

from .theme_manager import ThemeManager, load_theme, get_current_theme, set_theme
from .theme_models import Theme

__all__ = ["ThemeManager", "load_theme", "get_current_theme", "set_theme", "Theme"]
