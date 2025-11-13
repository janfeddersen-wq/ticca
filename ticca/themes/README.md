# Ticca Theme System

A comprehensive theming system for Ticca TUI that supports dynamic theme switching and customization.

## Overview

The theme system provides:
- **11 pre-defined themes** out of the box
- **Dynamic theme loading** from `~/.ticca/themes/`
- **Theme persistence** with JSON configuration files
- **CSS variable generation** for consistent styling across all components
- **Easy theme customization** and creation

## Available Themes

All themes are automatically generated in `~/.ticca/themes/` on first run:

1. **textual-dark** - Textual's default dark theme
2. **textual-light** - Textual's default light theme
3. **nord** - Cool, blue-tinted Scandinavian theme (default)
4. **gruvbox** - Retro, warm, earthy tones
5. **catppuccin-mocha** - Warm, dark, cozy theme
6. **catppuccin-latte** - Light, warm, soft theme
7. **dracula** - Dark purple with vibrant accents
8. **tokyo-night** - Dark, vibrant, modern theme
9. **monokai** - Classic, vibrant, high contrast
10. **flexoki** - Modern, balanced, flexible theme
11. **solarized-light** - Classic, soft, easy on eyes

## Theme Structure

Each theme is defined with the following color variables:

### Background Colors
- `background` - Main background
- `background_dark` - Darker background (for containers)
- `background_light` - Lighter background (for hover states)

### Foreground/Text Colors
- `foreground` - Primary text color
- `foreground_muted` - Dimmed/secondary text
- `foreground_bright` - Highlighted/bright text

### Accent Colors
- `primary` - Primary accent color
- `primary_light` - Lighter primary (hover states)
- `primary_dark` - Darker primary (borders)

### UI Element Colors
- `panel` - Panel background
- `panel_light` - Panel hover
- `border` - Border color

### Scrollbar Colors
- `scrollbar` - Scrollbar color
- `scrollbar_hover` - Scrollbar hover
- `scrollbar_active` - Scrollbar active/pressed

### Status Colors
- `success` - Success messages/states
- `warning` - Warning messages/states
- `error` - Error messages/states
- `info` - Info messages/states

### Message Type Colors
- `user_message` - User message text
- `agent_message` - Agent response text
- `system_message` - System message text
- `reasoning_message` - Agent reasoning text
- `tool_output` - Tool output text
- `command_output` - Command output text

### Button Colors
- `button_background` - Button background
- `button_hover` - Button hover state
- `button_active` - Button active/pressed state
- `button_text` - Button text color
- `button_border` - Button border color
- `button_border_light` - Button border (light variant)
- `button_border_dark` - Button border (dark variant)

### Modal/Overlay Colors
- `modal_background` - Modal container background
- `modal_overlay` - Semi-transparent overlay

## Using Themes

### Setting the Default Theme

The default theme can be set in `~/.ticca/puppy.cfg`:

```ini
[general]
tui_theme = nord
```

### Switching Themes Programmatically

```python
from ticca.themes import ThemeManager

# Set a theme
ThemeManager.set_current("dracula")

# Get available themes
themes = ThemeManager.list_themes()
print(themes)  # {'nord': 'Nord', 'dracula': 'Dracula', ...}

# Get current theme
theme = ThemeManager.get_current()
print(theme.name)  # 'nord'
```

### Using Theme Variables in Component CSS

All components should use theme variables instead of hardcoded colors:

```python
class MyComponent(Widget):
    DEFAULT_CSS = """
    MyComponent {
        background: $background;
        color: $text;
        border: solid $border;
    }

    MyComponent:hover {
        background: $surface;
        border: solid $primary;
    }

    .my-button {
        background: var(--button-background);
        color: var(--button-text);
    }

    .my-button:hover {
        background: var(--button-hover);
    }
    """
```

### CSS Variable Reference

Theme variables are available in two forms:

1. **Textual Design Tokens** (preferred for common variables):
   - `$background`, `$surface`, `$panel`
   - `$text`, `$text-muted`
   - `$primary`, `$primary-lighten-1`, `$primary-darken-1`
   - `$success`, `$warning`, `$error`, `$accent`
   - `$border`

2. **Direct Theme Variables** (for specific theme colors):
   - `var(--background)`, `var(--background-dark)`, `var(--background-light)`
   - `var(--foreground)`, `var(--foreground-muted)`, `var(--foreground-bright)`
   - `var(--button-background)`, `var(--button-hover)`, `var(--button-active)`
   - `var(--user-message)`, `var(--agent-message)`, `var(--system-message)`
   - etc.

## Creating Custom Themes

1. Create a new theme file in `~/.ticca/themes/my-theme.json`:

```json
{
  "name": "my-theme",
  "display_name": "My Custom Theme",
  "background": "#1a1b26",
  "background_dark": "#16161e",
  "background_light": "#24283b",
  "foreground": "#c0caf5",
  "foreground_muted": "#565f89",
  "foreground_bright": "#ffffff",
  "primary": "#7aa2f7",
  "primary_light": "#a9b7e8",
  "primary_dark": "#5884d9",
  "panel": "#24283b",
  "panel_light": "#2f3549",
  "border": "#414868",
  "scrollbar": "#7aa2f7",
  "scrollbar_hover": "#a9b7e8",
  "scrollbar_active": "#bb9af7",
  "success": "#9ece6a",
  "warning": "#e0af68",
  "error": "#f7768e",
  "info": "#7dcfff",
  "user_message": "#c0caf5",
  "agent_message": "#c0caf5",
  "system_message": "#7dcfff",
  "reasoning_message": "#bb9af7",
  "tool_output": "#73daca",
  "command_output": "#e0af68",
  "button_background": "#7aa2f7",
  "button_hover": "#a9b7e8",
  "button_active": "#2f3549",
  "button_text": "#1a1b26",
  "button_border": "#bb9af7",
  "button_border_light": "#c9a9ff",
  "button_border_dark": "#16161e",
  "modal_background": "rgba(26, 27, 38, 0.95)",
  "modal_overlay": "rgba(0, 0, 0, 0.7)"
}
```

2. Set your custom theme:

```python
from ticca.themes import ThemeManager

ThemeManager.set_current("my-theme")
```

## Theme File Location

All theme files are stored in: `~/.ticca/themes/`

Each theme is a JSON file named `{theme-name}.json`

## Migration from Hardcoded Colors

The following components have been updated to use the theme system:

- ✅ `app.py` - Main application
- ✅ `chat_view.py` - Chat message display
- ✅ `sidebar.py` - History sidebar
- ✅ `input_area.py` - Input area and buttons
- ✅ `file_editor_modal.py` - File editor modal
- ✅ `settings.py` - Settings screen

All hardcoded hex colors have been replaced with theme variables for proper theme switching.

## Architecture

```
ticca/themes/
├── __init__.py               # Public API
├── theme_models.py           # Theme data model
├── theme_definitions.py      # Pre-defined themes
├── theme_manager.py          # Theme loading/saving
├── css_generator.py          # CSS generation
└── README.md                 # This file
```

## API Reference

### ThemeManager

```python
from ticca.themes import ThemeManager

# Initialize theme system (called automatically by app)
ThemeManager.initialize()

# Get current theme
theme = ThemeManager.get_current()

# Set current theme
success = ThemeManager.set_current("dracula")

# List available themes
themes = ThemeManager.list_themes()

# Get a specific theme
theme = ThemeManager.get_theme("nord")

# Reload theme from disk
ThemeManager.reload()

# Save a theme
ThemeManager.save(theme)

# Get themes directory
path = ThemeManager.get_themes_dir()
```

### Theme Object

```python
from ticca.themes import Theme

# Access theme properties
print(theme.name)              # 'nord'
print(theme.display_name)      # 'Nord'
print(theme.background)        # '#2e3440'
print(theme.primary)           # '#5e81ac'

# Convert to dictionary
theme_dict = theme.to_dict()

# Convert to JSON
json_str = theme.to_json()

# Generate CSS
css = theme.to_css_variables()
```

## Troubleshooting

### Themes not loading?

1. Check that `~/.ticca/themes/` directory exists
2. Verify theme files are valid JSON
3. Ensure all required color fields are present

### Colors not changing?

1. Make sure components use theme variables, not hardcoded colors
2. Restart the application after changing themes
3. Check that the theme name is correct in config

### Custom theme not appearing?

1. Verify the JSON file is in `~/.ticca/themes/`
2. Check JSON syntax is valid
3. Ensure the `name` field matches the filename (without .json)

## Future Enhancements

Potential improvements for the theme system:

- [ ] Live theme switching without restart
- [ ] Theme editor in Settings UI
- [ ] Theme preview before applying
- [ ] Import/export theme functionality
- [ ] Dark/light mode auto-detection
- [ ] Per-component theme overrides
- [ ] Theme inheritance/composition
