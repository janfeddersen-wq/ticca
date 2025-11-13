"""
Theme manager for loading, saving, and managing themes.

Handles theme persistence in ~/.ticca/themes/ directory and provides
runtime theme switching capabilities.
"""

import json
import os
from pathlib import Path
from typing import Dict, Optional

from .theme_models import Theme
from .theme_definitions import ALL_THEMES


# Global theme cache and current theme
_theme_cache: Dict[str, Theme] = {}
_current_theme: Optional[Theme] = None


def get_themes_directory() -> Path:
    """Get the themes directory path, creating it if necessary."""
    themes_dir = Path.home() / ".ticca" / "themes"
    themes_dir.mkdir(parents=True, exist_ok=True)
    return themes_dir


def ensure_default_themes_exist() -> None:
    """
    Ensure all default themes exist in ~/.ticca/themes/.
    Creates theme files for any missing themes.
    """
    themes_dir = get_themes_directory()

    for theme_name, theme in ALL_THEMES.items():
        theme_file = themes_dir / f"{theme_name}.json"
        if not theme_file.exists():
            # Create the theme file
            save_theme(theme, theme_file)
            print(f"Created theme file: {theme_file}")


def save_theme(theme: Theme, path: Optional[Path] = None) -> None:
    """
    Save a theme to a JSON file.

    Args:
        theme: Theme object to save
        path: Optional custom path. If not provided, saves to ~/.ticca/themes/{name}.json
    """
    if path is None:
        themes_dir = get_themes_directory()
        path = themes_dir / f"{theme.name}.json"

    with open(path, 'w') as f:
        f.write(theme.to_json())


def load_theme_from_file(path: Path) -> Optional[Theme]:
    """
    Load a theme from a JSON file.

    Args:
        path: Path to the theme JSON file

    Returns:
        Theme object or None if loading fails
    """
    try:
        with open(path, 'r') as f:
            data = json.load(f)
        return Theme.from_dict(data)
    except Exception as e:
        print(f"Error loading theme from {path}: {e}")
        return None


def load_theme(theme_name: str) -> Optional[Theme]:
    """
    Load a theme by name.

    First checks the cache, then tries to load from ~/.ticca/themes/,
    then falls back to built-in themes.

    Args:
        theme_name: Name of the theme to load

    Returns:
        Theme object or None if not found
    """
    # Check cache first
    if theme_name in _theme_cache:
        return _theme_cache[theme_name]

    # Try to load from file
    themes_dir = get_themes_directory()
    theme_file = themes_dir / f"{theme_name}.json"

    if theme_file.exists():
        theme = load_theme_from_file(theme_file)
        if theme:
            _theme_cache[theme_name] = theme
            return theme

    # Fall back to built-in themes
    if theme_name in ALL_THEMES:
        theme = ALL_THEMES[theme_name]
        _theme_cache[theme_name] = theme
        # Save it to file for future use
        save_theme(theme)
        return theme

    return None


def get_available_themes() -> Dict[str, str]:
    """
    Get all available themes (both built-in and user-created).

    Returns:
        Dictionary mapping theme names to display names
    """
    themes = {}

    # Add built-in themes
    for theme_name, theme in ALL_THEMES.items():
        themes[theme_name] = theme.display_name

    # Check for user-created themes in ~/.ticca/themes/
    themes_dir = get_themes_directory()
    if themes_dir.exists():
        for theme_file in themes_dir.glob("*.json"):
            theme_name = theme_file.stem
            if theme_name not in themes:
                # Load the theme to get its display name
                theme = load_theme_from_file(theme_file)
                if theme:
                    themes[theme_name] = theme.display_name

    return themes


def set_theme(theme_name: str) -> bool:
    """
    Set the current theme.

    Args:
        theme_name: Name of the theme to set

    Returns:
        True if successful, False otherwise
    """
    global _current_theme

    theme = load_theme(theme_name)
    if theme:
        _current_theme = theme
        # Save the preference to config
        from ticca.config import set_config_value
        try:
            set_config_value("tui_theme", theme_name)
        except Exception:
            pass  # Silently fail if config update fails
        return True
    return False


def get_current_theme() -> Theme:
    """
    Get the current theme.

    If no theme is set, loads the default theme from config or falls back to Nord.

    Returns:
        Current Theme object
    """
    global _current_theme

    if _current_theme is None:
        # Try to load from config
        from ticca.config import get_value
        try:
            theme_name = get_value("tui_theme")
            if not theme_name:
                theme_name = "nord"
        except Exception:
            theme_name = "nord"

        # Ensure default themes exist
        ensure_default_themes_exist()

        # Load the theme
        theme = load_theme(theme_name)
        if theme:
            _current_theme = theme
        else:
            # Ultimate fallback to Nord
            _current_theme = ALL_THEMES["nord"]

    return _current_theme


def reload_theme() -> None:
    """
    Reload the current theme from disk.
    Useful after theme files have been modified.
    """
    global _current_theme, _theme_cache

    if _current_theme:
        theme_name = _current_theme.name
        # Clear cache for this theme
        if theme_name in _theme_cache:
            del _theme_cache[theme_name]
        # Reload
        _current_theme = load_theme(theme_name)


class ThemeManager:
    """
    Convenience class for managing themes.
    Provides a simple interface for theme operations.
    """

    @staticmethod
    def initialize() -> None:
        """Initialize the theme system."""
        ensure_default_themes_exist()
        get_current_theme()  # Load the current theme

    @staticmethod
    def get_theme(theme_name: str) -> Optional[Theme]:
        """Get a theme by name."""
        return load_theme(theme_name)

    @staticmethod
    def get_current() -> Theme:
        """Get the current theme."""
        return get_current_theme()

    @staticmethod
    def set_current(theme_name: str) -> bool:
        """Set the current theme."""
        return set_theme(theme_name)

    @staticmethod
    def list_themes() -> Dict[str, str]:
        """List all available themes."""
        return get_available_themes()

    @staticmethod
    def reload() -> None:
        """Reload the current theme."""
        reload_theme()

    @staticmethod
    def save(theme: Theme) -> None:
        """Save a theme to disk."""
        save_theme(theme)

    @staticmethod
    def get_themes_dir() -> Path:
        """Get the themes directory path."""
        return get_themes_directory()
