"""
Helper functions for showing approval dialogs in TUI mode.
"""

import threading
from typing import Tuple
from ticca.tui_state import is_tui_mode, get_tui_app_instance


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
        app = get_tui_app_instance()
        if not app:
            return False, None

        from ticca.tui.screens.approval_modal import ApprovalModal

        # Use threading event to block until modal returns
        result_container = {}
        event = threading.Event()

        def callback(result):
            result_container['result'] = result
            event.set()

        # Show modal with callback
        app.push_screen(ApprovalModal(title, content, preview), callback)

        # Block until result is available
        event.wait()

        result = result_container.get('result')
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
        app = get_tui_app_instance()
        if not app:
            return None

        from ticca.tui.screens.human_feedback_modal import HumanFeedbackModal

        # Use threading event to block until modal returns
        result_container = {}
        event = threading.Event()

        def callback(result):
            result_container['result'] = result
            event.set()

        # Show modal with callback
        app.push_screen(HumanFeedbackModal(question, options or []), callback)

        # Block until result is available
        event.wait()

        return result_container.get('result')

    except Exception as e:
        import logging
        logger = logging.getLogger(__name__)
        logger.error(f"TUI human feedback modal failed: {e}")
        return None
