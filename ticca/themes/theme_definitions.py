"""
Pre-defined theme configurations for all supported themes.

Each theme is defined with a complete set of color variables that map
to the Theme dataclass structure.
"""

from .theme_models import Theme


# Nord Theme (Cool, blue-tinted, Scandinavian)
NORD_THEME = Theme(
    name="nord",
    display_name="Nord",
    # Backgrounds
    background="#2e3440",
    background_dark="#242933",
    background_light="#3b4252",
    # Foreground
    foreground="#d8dee9",
    foreground_muted="#6c7789",
    foreground_bright="#eceff4",
    # Primary accent
    primary="#5e81ac",
    primary_light="#81a1c1",
    primary_dark="#4c668a",
    # UI elements
    panel="#3b4252",
    panel_light="#434c5e",
    border="#4c566a",
    # Scrollbar
    scrollbar="#5e81ac",
    scrollbar_hover="#81a1c1",
    scrollbar_active="#88c0d0",
    # Status
    success="#a3be8c",
    warning="#ebcb8b",
    error="#bf616a",
    info="#81a1c1",
    # Messages
    user_message="#eceff4",
    agent_message="#d8dee9",
    system_message="#88c0d0",
    reasoning_message="#b48ead",
    tool_output="#8fbcbb",
    command_output="#ebcb8b",
    # Buttons
    button_background="#5e81ac",
    button_hover="#81a1c1",
    button_active="#4c566a",
    button_text="#eceff4",
    button_border="#88c0d0",
    button_border_light="#a3d5d9",
    button_border_dark="#3b4252",
    # Modal
    modal_background="rgba(46, 52, 64, 0.95)",
    modal_overlay="rgba(0, 0, 0, 0.6)",
    # Diff
    diff_addition="#a3be8c",  # Nord green
    diff_deletion="#d08770",  # Nord orange
)


# Dracula Theme (Dark purple with vibrant accents)
DRACULA_THEME = Theme(
    name="dracula",
    display_name="Dracula",
    # Backgrounds
    background="#282a36",
    background_dark="#1e1f29",
    background_light="#343746",
    # Foreground
    foreground="#f8f8f2",
    foreground_muted="#6272a4",
    foreground_bright="#ffffff",
    # Primary accent
    primary="#bd93f9",
    primary_light="#d4bbff",
    primary_dark="#9966cc",
    # UI elements
    panel="#343746",
    panel_light="#44475a",
    border="#6272a4",
    # Scrollbar
    scrollbar="#bd93f9",
    scrollbar_hover="#d4bbff",
    scrollbar_active="#ff79c6",
    # Status
    success="#50fa7b",
    warning="#f1fa8c",
    error="#ff5555",
    info="#8be9fd",
    # Messages
    user_message="#ffffff",
    agent_message="#f8f8f2",
    system_message="#8be9fd",
    reasoning_message="#bd93f9",
    tool_output="#50fa7b",
    command_output="#f1fa8c",
    # Buttons
    button_background="#bd93f9",
    button_hover="#d4bbff",
    button_active="#44475a",
    button_text="#282a36",
    button_border="#ff79c6",
    button_border_light="#ffb3e6",
    button_border_dark="#1e1f29",
    # Modal
    modal_background="rgba(40, 42, 54, 0.95)",
    modal_overlay="rgba(0, 0, 0, 0.7)",
    # Diff
    diff_addition="#50fa7b",  # Dracula green
    diff_deletion="#ffb86c",  # Dracula orange
)


# Gruvbox Theme (Retro, warm, earthy)
GRUVBOX_THEME = Theme(
    name="gruvbox",
    display_name="Gruvbox",
    # Backgrounds
    background="#282828",
    background_dark="#1d2021",
    background_light="#3c3836",
    # Foreground
    foreground="#ebdbb2",
    foreground_muted="#928374",
    foreground_bright="#fbf1c7",
    # Primary accent
    primary="#83a598",
    primary_light="#a8c8e0",
    primary_dark="#6d8699",
    # UI elements
    panel="#3c3836",
    panel_light="#504945",
    border="#504945",
    # Scrollbar
    scrollbar="#83a598",
    scrollbar_hover="#a8c8e0",
    scrollbar_active="#b8bb26",
    # Status
    success="#b8bb26",
    warning="#fabd2f",
    error="#fb4934",
    info="#83a598",
    # Messages
    user_message="#fbf1c7",
    agent_message="#ebdbb2",
    system_message="#8ec07c",
    reasoning_message="#d3869b",
    tool_output="#83a598",
    command_output="#fabd2f",
    # Buttons
    button_background="#83a598",
    button_hover="#a8c8e0",
    button_active="#3c3836",
    button_text="#282828",
    button_border="#8ec07c",
    button_border_light="#b8bb26",
    button_border_dark="#1d2021",
    # Modal
    modal_background="rgba(40, 40, 40, 0.95)",
    modal_overlay="rgba(0, 0, 0, 0.6)",
    # Diff
    diff_addition="#b8bb26",  # Gruvbox green
    diff_deletion="#fe8019",  # Gruvbox orange
)


# Tokyo Night Theme (Dark, vibrant, modern)
TOKYO_NIGHT_THEME = Theme(
    name="tokyo-night",
    display_name="Tokyo Night",
    # Backgrounds
    background="#1a1b26",
    background_dark="#16161e",
    background_light="#24283b",
    # Foreground
    foreground="#c0caf5",
    foreground_muted="#565f89",
    foreground_bright="#ffffff",
    # Primary accent
    primary="#7aa2f7",
    primary_light="#a9b7e8",
    primary_dark="#5884d9",
    # UI elements
    panel="#24283b",
    panel_light="#2f3549",
    border="#414868",
    # Scrollbar
    scrollbar="#7aa2f7",
    scrollbar_hover="#a9b7e8",
    scrollbar_active="#bb9af7",
    # Status
    success="#9ece6a",
    warning="#e0af68",
    error="#f7768e",
    info="#7dcfff",
    # Messages
    user_message="#ffffff",
    agent_message="#c0caf5",
    system_message="#7dcfff",
    reasoning_message="#bb9af7",
    tool_output="#73daca",
    command_output="#e0af68",
    # Buttons
    button_background="#7aa2f7",
    button_hover="#a9b7e8",
    button_active="#2f3549",
    button_text="#1a1b26",
    button_border="#bb9af7",
    button_border_light="#c9a9ff",
    button_border_dark="#16161e",
    # Modal
    modal_background="rgba(26, 27, 38, 0.95)",
    modal_overlay="rgba(0, 0, 0, 0.7)",
    # Diff
    diff_addition="#9ece6a",  # Tokyo Night green
    diff_deletion="#f7768e",  # Tokyo Night red/pink
)


# Monokai Theme (Classic, vibrant, high contrast)
MONOKAI_THEME = Theme(
    name="monokai",
    display_name="Monokai",
    # Backgrounds
    background="#272822",
    background_dark="#1e1f1c",
    background_light="#383830",
    # Foreground
    foreground="#f8f8f2",
    foreground_muted="#75715e",
    foreground_bright="#ffffff",
    # Primary accent
    primary="#66d9ef",
    primary_light="#8de9ff",
    primary_dark="#4dbbd9",
    # UI elements
    panel="#3e3d32",
    panel_light="#49483e",
    border="#49483e",
    # Scrollbar
    scrollbar="#66d9ef",
    scrollbar_hover="#8de9ff",
    scrollbar_active="#a6e22e",
    # Status
    success="#a6e22e",
    warning="#e6db74",
    error="#f92672",
    info="#66d9ef",
    # Messages
    user_message="#ffffff",
    agent_message="#f8f8f2",
    system_message="#66d9ef",
    reasoning_message="#ae81ff",
    tool_output="#a6e22e",
    command_output="#e6db74",
    # Buttons
    button_background="#66d9ef",
    button_hover="#8de9ff",
    button_active="#49483e",
    button_text="#272822",
    button_border="#a6e22e",
    button_border_light="#c0ff3e",
    button_border_dark="#1e1f1c",
    # Modal
    modal_background="rgba(39, 40, 34, 0.95)",
    modal_overlay="rgba(0, 0, 0, 0.7)",
    # Diff
    diff_addition="#a6e22e",  # Monokai green
    diff_deletion="#fd971f",  # Monokai orange
)


# Catppuccin Mocha Theme (Warm, dark, cozy)
CATPPUCCIN_MOCHA_THEME = Theme(
    name="catppuccin-mocha",
    display_name="Catppuccin Mocha",
    # Backgrounds
    background="#1e1e2e",
    background_dark="#181825",
    background_light="#313244",
    # Foreground
    foreground="#cdd6f4",
    foreground_muted="#6c7086",
    foreground_bright="#ffffff",
    # Primary accent
    primary="#89b4fa",
    primary_light="#a6c7ff",
    primary_dark="#6a8fcf",
    # UI elements
    panel="#313244",
    panel_light="#45475a",
    border="#585b70",
    # Scrollbar
    scrollbar="#89b4fa",
    scrollbar_hover="#a6c7ff",
    scrollbar_active="#cba6f7",
    # Status
    success="#a6e3a1",
    warning="#f9e2af",
    error="#f38ba8",
    info="#89dceb",
    # Messages
    user_message="#f5e0dc",
    agent_message="#cdd6f4",
    system_message="#89dceb",
    reasoning_message="#cba6f7",
    tool_output="#94e2d5",
    command_output="#f9e2af",
    # Buttons
    button_background="#89b4fa",
    button_hover="#a6c7ff",
    button_active="#45475a",
    button_text="#1e1e2e",
    button_border="#cba6f7",
    button_border_light="#dbb7ff",
    button_border_dark="#181825",
    # Modal
    modal_background="rgba(30, 30, 46, 0.95)",
    modal_overlay="rgba(0, 0, 0, 0.7)",
    # Diff
    diff_addition="#a6e3a1",  # Catppuccin Mocha green
    diff_deletion="#f38ba8",  # Catppuccin Mocha red
)


# Catppuccin Latte Theme (Light, warm, soft)
CATPPUCCIN_LATTE_THEME = Theme(
    name="catppuccin-latte",
    display_name="Catppuccin Latte",
    # Backgrounds
    background="#eff1f5",
    background_dark="#e6e9ef",
    background_light="#ffffff",
    # Foreground
    foreground="#4c4f69",
    foreground_muted="#9ca0b0",
    foreground_bright="#2c2f44",
    # Primary accent
    primary="#1e66f5",
    primary_light="#4e8fff",
    primary_dark="#0e4fbf",
    # UI elements
    panel="#e6e9ef",
    panel_light="#dce0e8",
    border="#acb0be",
    # Scrollbar
    scrollbar="#1e66f5",
    scrollbar_hover="#4e8fff",
    scrollbar_active="#8839ef",
    # Status
    success="#40a02b",
    warning="#df8e1d",
    error="#d20f39",
    info="#04a5e5",
    # Messages
    user_message="#2c2f44",
    agent_message="#4c4f69",
    system_message="#04a5e5",
    reasoning_message="#8839ef",
    tool_output="#179299",
    command_output="#df8e1d",
    # Buttons
    button_background="#1e66f5",
    button_hover="#4e8fff",
    button_active="#dce0e8",
    button_text="#ffffff",
    button_border="#8839ef",
    button_border_light="#a46fff",
    button_border_dark="#e6e9ef",
    # Modal
    modal_background="rgba(239, 241, 245, 0.95)",
    modal_overlay="rgba(0, 0, 0, 0.4)",
    # Diff
    diff_addition="#40a02b",  # Catppuccin Latte green
    diff_deletion="#d20f39",  # Catppuccin Latte red
)


# Solarized Light Theme (Classic, soft, easy on eyes)
SOLARIZED_LIGHT_THEME = Theme(
    name="solarized-light",
    display_name="Solarized Light",
    # Backgrounds
    background="#fdf6e3",
    background_dark="#eee8d5",
    background_light="#ffffff",
    # Foreground
    foreground="#657b83",
    foreground_muted="#93a1a1",
    foreground_bright="#073642",
    # Primary accent
    primary="#268bd2",
    primary_light="#4fa8e8",
    primary_dark="#1e6ea8",
    # UI elements
    panel="#eee8d5",
    panel_light="#e3ddc3",
    border="#93a1a1",
    # Scrollbar
    scrollbar="#268bd2",
    scrollbar_hover="#4fa8e8",
    scrollbar_active="#6c71c4",
    # Status
    success="#859900",
    warning="#b58900",
    error="#dc322f",
    info="#2aa198",
    # Messages
    user_message="#073642",
    agent_message="#657b83",
    system_message="#2aa198",
    reasoning_message="#6c71c4",
    tool_output="#859900",
    command_output="#b58900",
    # Buttons
    button_background="#268bd2",
    button_hover="#4fa8e8",
    button_active="#e3ddc3",
    button_text="#fdf6e3",
    button_border="#2aa198",
    button_border_light="#35c9bc",
    button_border_dark="#eee8d5",
    # Modal
    modal_background="rgba(253, 246, 227, 0.95)",
    modal_overlay="rgba(0, 0, 0, 0.3)",
    # Diff
    diff_addition="#859900",  # Solarized green
    diff_deletion="#dc322f",  # Solarized red
)


# Flexoki Theme (Modern, balanced, flexible)
FLEXOKI_THEME = Theme(
    name="flexoki",
    display_name="Flexoki",
    # Backgrounds
    background="#100f0f",
    background_dark="#0d0c0c",
    background_light="#1c1b1a",
    # Foreground
    foreground="#cecdc3",
    foreground_muted="#878580",
    foreground_bright="#fffcf0",
    # Primary accent
    primary="#4385be",
    primary_light="#5ea2d9",
    primary_dark="#2f669e",
    # UI elements
    panel="#1c1b1a",
    panel_light="#282726",
    border="#403e3c",
    # Scrollbar
    scrollbar="#4385be",
    scrollbar_hover="#5ea2d9",
    scrollbar_active="#8b7ec8",
    # Status
    success="#4c9f70",
    warning="#d0a215",
    error="#af3029",
    info="#3aa99f",
    # Messages
    user_message="#fffcf0",
    agent_message="#cecdc3",
    system_message="#3aa99f",
    reasoning_message="#8b7ec8",
    tool_output="#4c9f70",
    command_output="#d0a215",
    # Buttons
    button_background="#4385be",
    button_hover="#5ea2d9",
    button_active="#282726",
    button_text="#100f0f",
    button_border="#3aa99f",
    button_border_light="#52c9bd",
    button_border_dark="#0d0c0c",
    # Modal
    modal_background="rgba(16, 15, 15, 0.95)",
    modal_overlay="rgba(0, 0, 0, 0.7)",
    # Diff
    diff_addition="#4c9f70",  # Flexoki green
    diff_deletion="#af3029",  # Flexoki red
)


# Textual Dark Theme (Textual default dark)
TEXTUAL_DARK_THEME = Theme(
    name="textual-dark",
    display_name="Textual Dark",
    # Backgrounds
    background="#0c0c0c",
    background_dark="#000000",
    background_light="#1e1e1e",
    # Foreground
    foreground="#e0e0e0",
    foreground_muted="#808080",
    foreground_bright="#ffffff",
    # Primary accent
    primary="#0178d4",
    primary_light="#3e9de8",
    primary_dark="#0062b0",
    # UI elements
    panel="#1e1e1e",
    panel_light="#2a2a2a",
    border="#404040",
    # Scrollbar
    scrollbar="#0178d4",
    scrollbar_hover="#3e9de8",
    scrollbar_active="#0dc5ff",
    # Status
    success="#00d000",
    warning="#ffa500",
    error="#ff0000",
    info="#00b0ff",
    # Messages
    user_message="#ffffff",
    agent_message="#e0e0e0",
    system_message="#00b0ff",
    reasoning_message="#c080ff",
    tool_output="#00d000",
    command_output="#ffa500",
    # Buttons
    button_background="#0178d4",
    button_hover="#3e9de8",
    button_active="#2a2a2a",
    button_text="#ffffff",
    button_border="#0dc5ff",
    button_border_light="#5dd5ff",
    button_border_dark="#000000",
    # Modal
    modal_background="rgba(12, 12, 12, 0.95)",
    modal_overlay="rgba(0, 0, 0, 0.7)",
    # Diff
    diff_addition="#00d000",  # Textual Dark green
    diff_deletion="#ff5555",  # Textual Dark red
)


# Textual Light Theme (Textual default light)
TEXTUAL_LIGHT_THEME = Theme(
    name="textual-light",
    display_name="Textual Light",
    # Backgrounds
    background="#f4f4f4",
    background_dark="#e8e8e8",
    background_light="#ffffff",
    # Foreground
    foreground="#2c2c2c",
    foreground_muted="#808080",
    foreground_bright="#000000",
    # Primary accent
    primary="#0178d4",
    primary_light="#3e9de8",
    primary_dark="#0062b0",
    # UI elements
    panel="#e8e8e8",
    panel_light="#d8d8d8",
    border="#c0c0c0",
    # Scrollbar
    scrollbar="#0178d4",
    scrollbar_hover="#3e9de8",
    scrollbar_active="#0dc5ff",
    # Status
    success="#008000",
    warning="#ff8c00",
    error="#cc0000",
    info="#0080ff",
    # Messages
    user_message="#000000",
    agent_message="#2c2c2c",
    system_message="#0080ff",
    reasoning_message="#8000ff",
    tool_output="#008000",
    command_output="#ff8c00",
    # Buttons
    button_background="#0178d4",
    button_hover="#3e9de8",
    button_active="#d8d8d8",
    button_text="#ffffff",
    button_border="#0dc5ff",
    button_border_light="#5dd5ff",
    button_border_dark="#e8e8e8",
    # Modal
    modal_background="rgba(244, 244, 244, 0.95)",
    modal_overlay="rgba(0, 0, 0, 0.3)",
    # Diff
    diff_addition="#008000",  # Textual Light green
    diff_deletion="#cc0000",  # Textual Light red
)


# Dictionary of all available themes
ALL_THEMES = {
    "textual-dark": TEXTUAL_DARK_THEME,
    "textual-light": TEXTUAL_LIGHT_THEME,
    "nord": NORD_THEME,
    "gruvbox": GRUVBOX_THEME,
    "catppuccin-mocha": CATPPUCCIN_MOCHA_THEME,
    "dracula": DRACULA_THEME,
    "tokyo-night": TOKYO_NIGHT_THEME,
    "monokai": MONOKAI_THEME,
    "flexoki": FLEXOKI_THEME,
    "catppuccin-latte": CATPPUCCIN_LATTE_THEME,
    "solarized-light": SOLARIZED_LIGHT_THEME,
}
