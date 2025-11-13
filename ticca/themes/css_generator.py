"""
CSS generator for converting theme objects to Textual CSS.

Provides utilities for generating CSS from theme definitions that can be
dynamically injected into Textual applications.
"""

from textual.theme import Theme as TextualTheme
from .theme_models import Theme


def create_textual_theme(theme: Theme) -> TextualTheme:
    """
    Convert our Theme object to a Textual Theme object.

    Args:
        theme: Our custom Theme object

    Returns:
        Textual Theme object that can be registered with the app
    """
    return TextualTheme(
        name=theme.name,
        primary=theme.primary,
        secondary=theme.panel_light,
        warning=theme.warning,
        error=theme.error,
        success=theme.success,
        accent=theme.info,
        background=theme.background,
        surface=theme.background_light,
        panel=theme.panel,
        dark=(theme.background.startswith("#") and int(theme.background[1:3], 16) < 128),
        variables={
            "border": theme.border,
            "foreground": theme.foreground,
        }
    )


def generate_theme_css(theme: Theme) -> str:
    """
    Generate complete CSS for a theme that can be used in Textual applications.

    Only uses official Textual design tokens as per:
    https://textual.textualize.io/guide/design/

    Args:
        theme: Theme object to generate CSS from

    Returns:
        String containing CSS variable definitions using Textual's official design tokens
    """
    # Map theme colors to ONLY official Textual design tokens
    css_lines = [
        "/* Auto-generated theme CSS - Official Textual Design Tokens Only */",
        "",
        "/* Background tokens */",
        "$background: " + theme.background + ";",
        "$surface: " + theme.background_light + ";",
        "$panel: " + theme.panel + ";",
        "",
        "/* Primary color and modifiers */",
        "$primary: " + theme.primary + ";",
        "$primary-lighten-1: " + theme.primary_light + ";",
        "$primary-lighten-2: " + theme.primary_light + ";",
        "$primary-lighten-3: " + theme.primary_light + ";",
        "$primary-darken-1: " + theme.primary_dark + ";",
        "$primary-darken-2: " + theme.primary_dark + ";",
        "$primary-darken-3: " + theme.primary_dark + ";",
        "",
        "/* Secondary color */",
        "$secondary: " + theme.panel_light + ";",
        "",
        "/* Status colors */",
        "$success: " + theme.success + ";",
        "$warning: " + theme.warning + ";",
        "$error: " + theme.error + ";",
        "$accent: " + theme.info + ";",
        "",
        "/* Text colors */",
        "$foreground: " + theme.foreground + ";",
        "$text: " + theme.foreground + ";",
        "$text-muted: " + theme.foreground_muted + ";",
        "",
        "/* Border */",
        "$border: " + theme.border + ";",
        "",
        "/* Boost (highlight color) */",
        "$boost: " + theme.primary_light + ";",
    ]

    return "\n".join(css_lines)


def inject_theme_css_into_app(app, theme: Theme) -> None:
    """
    Inject theme CSS into a running Textual app.

    This modifies the app's stylesheet at runtime to apply the theme.

    Args:
        app: Textual App instance
        theme: Theme to apply
    """
    # Generate the CSS
    theme_css = generate_theme_css(theme)

    # Try to inject it into the app
    try:
        # Textual apps have a stylesheet that can be modified
        if hasattr(app, 'stylesheet'):
            # Parse and add the theme CSS
            app.stylesheet.parse(theme_css)
            # Force a refresh to apply changes
            app.refresh(layout=True)
    except Exception as e:
        # If injection fails, log but don't crash
        print(f"Warning: Could not inject theme CSS: {e}")


def get_component_css_template() -> str:
    """
    Get a CSS template for components that use theme variables.

    This template shows how to use theme variables in component CSS.

    Returns:
        String containing example CSS using theme variables
    """
    return """
/* Example component CSS using theme variables */
MyComponent {
    background: var(--background);
    color: var(--foreground);
    border: solid var(--border);
}

MyComponent:hover {
    background: var(--background-light);
    color: var(--foreground-bright);
}

MyComponent:focus {
    border: solid var(--primary);
}

/* Or use Textual design tokens */
MyComponent {
    background: $background;
    color: $text;
    border: solid $border;
}

MyComponent:hover {
    background: $surface;
    color: $text;
}

MyComponent:focus {
    border: solid $primary;
}
"""
