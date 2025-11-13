"""
Helper functions for showing approval dialogs in TUI mode.
"""

from typing import Tuple
from ticca.tui_state import is_tui_mode, get_tui_app


def show_tui_approval(
    title: str,
    content: str,
    preview: str | None = None
) -> Tuple[bool, str | None]:
    """Show approval dialog in TUI mode.

    Args:
        title: Title of the approval dialog
        content: Main content describing what needs approval
        preview: Optional preview (like diff)

    Returns:
        Tuple of (approved: bool, feedback: str | None)
    """
    if not is_tui_mode():
        # Not in TUI mode, return False to use CLI fallback
        return False, None

    try:
        app = get_tui_app()
        if not app:
            return False, None

        from ticca.tui.screens.approval_modal import ApprovalModal

        # Show modal and wait for result
        result = app.push_screen_wait(
            ApprovalModal(title, content, preview)
        )

        if result:
            return result.get("approved", False), result.get("feedback", None)
        else:
            return False, None

    except Exception as e:
        # If TUI fails, return False to use CLI fallback
        import logging
        logger = logging.getLogger(__name__)
        logger.error(f"TUI approval modal failed: {e}")
        return False, None


def show_tui_human_feedback(
    question: str,
    options: list[str] | None = None
) -> str | None:
    """Show human feedback dialog in TUI mode.

    Args:
        question: Question to ask the human
        options: Up to 3 predefined options (can also provide custom answer)

    Returns:
        Human's answer string, or None if cancelled
    """
    if not is_tui_mode():
        return None

    try:
        app = get_tui_app()
        if not app:
            return None

        from ticca.tui.screens.human_feedback_modal import HumanFeedbackModal

        # Show modal and wait for result
        result = app.push_screen_wait(
            HumanFeedbackModal(question, options or [])
        )

        return result

    except Exception as e:
        import logging
        logger = logging.getLogger(__name__)
        logger.error(f"TUI human feedback modal failed: {e}")
        return None
