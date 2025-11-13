"""
Tool for agents to ask humans for feedback/input.
"""

from pydantic import BaseModel
from pydantic_ai import RunContext
from rich.panel import Panel
from rich.text import Text
from ticca.messaging import emit_info
from ticca.tui_state import is_tui_mode
from ticca.tools.common import arrow_select, console


class HumanFeedbackOutput(BaseModel):
    """Output from asking human for feedback."""

    success: bool
    answer: str | None = None
    error: str | None = None


def ask_human_for_feedback(
    context: RunContext,
    question: str,
    options: list[str] | None = None
) -> HumanFeedbackOutput:
    """Ask the human for feedback with optional predefined options.

    Args:
        question: The question to ask the human
        options: Up to 3 predefined options for the human to choose from.
                If None, human can provide free-form text.

    Returns:
        HumanFeedbackOutput with the human's answer
    """
    if not question or not question.strip():
        return HumanFeedbackOutput(
            success=False,
            error="Question cannot be empty"
        )

    # Validate options - should have at least 2 for better UX
    if options is not None and len(options) < 2:
        return HumanFeedbackOutput(
            success=False,
            error="Please provide at least 2 options for the user to choose from"
        )

    # Limit to 3 options max
    if options and len(options) > 3:
        options = options[:3]

    emit_info("\n[bold white on purple] AGENT ASKING FOR HELP [/bold white on purple]")

    # Check if we're in TUI mode
    if is_tui_mode():
        # Use TUI modal
        try:
            from ticca.tui.approval_helpers import show_tui_human_feedback

            result = show_tui_human_feedback(question, options)

            if result:
                return HumanFeedbackOutput(
                    success=True,
                    answer=result
                )
            else:
                return HumanFeedbackOutput(
                    success=False,
                    error="User cancelled the feedback request"
                )
        except Exception as e:
            emit_info(f"[yellow]TUI modal failed, falling back to CLI: {e}[/yellow]")

    # CLI mode - use Rich console
    panel_content = Text()
    panel_content.append("🤔 ", style="bold")
    panel_content.append(question, style="bold white")

    panel = Panel(
        panel_content,
        title="[bold white]Agent Needs Your Input[/bold white]",
        border_style="purple",
        padding=(1, 2),
    )

    console.print()
    console.print(panel)
    console.print()

    try:
        if options and len(options) > 0:
            # Use arrow selector with options + custom option
            choices = list(options)
            choices.append("Other (custom answer)")

            choice = arrow_select(
                "💭 Please select an option:",
                choices
            )

            if choice == "Other (custom answer)":
                # Get custom input
                from rich.prompt import Prompt
                console.print()
                console.print("[bold cyan]Enter your custom answer:[/bold cyan]")
                answer = Prompt.ask(
                    "[bold green]➤[/bold green]",
                    default="",
                ).strip()

                if not answer:
                    return HumanFeedbackOutput(
                        success=False,
                        error="No answer provided"
                    )

                return HumanFeedbackOutput(
                    success=True,
                    answer=answer
                )
            else:
                return HumanFeedbackOutput(
                    success=True,
                    answer=choice
                )
        else:
            # Free-form text input
            from rich.prompt import Prompt
            console.print()
            console.print("[bold cyan]Your answer:[/bold cyan]")
            answer = Prompt.ask(
                "[bold green]➤[/bold green]",
                default="",
            ).strip()

            if not answer:
                return HumanFeedbackOutput(
                    success=False,
                    error="No answer provided"
                )

            return HumanFeedbackOutput(
                success=True,
                answer=answer
            )

    except (KeyboardInterrupt, EOFError):
        console.print("\n[bold red]⊗ Cancelled by user[/bold red]")
        return HumanFeedbackOutput(
            success=False,
            error="User cancelled the feedback request"
        )


def register_ask_human_feedback_tool(agent):
    """Register the ask_human_for_feedback tool."""

    @agent.tool
    def agent_ask_human_for_feedback(
        context: RunContext,
        question: str,
        options: list[str]
    ) -> HumanFeedbackOutput:
        """Ask the human for feedback or input when you're unsure about something.

        Use this tool when:
        - You need clarification on requirements
        - You're uncertain which approach to take
        - You need the user to make a decision
        - You want to confirm before taking a risky action

        Args:
            question: A clear, concise question for the human.
                     Should explain the context and what you need help with.
            options: List of 2-3 predefined answer options for the human to choose from.
                    REQUIRED - You must always provide at least 2 suggested options.
                    The human can also provide a custom answer if none fit.
                    Maximum 3 options are recommended.

        Returns:
            HumanFeedbackOutput: Contains the human's answer if successful,
                                or an error if the request was cancelled.

        Examples:
            >>> # Ask with predefined options (ALWAYS do this)
            >>> result = agent_ask_human_for_feedback(
            ...     ctx,
            ...     "Should I use TypeScript or JavaScript for this project?",
            ...     ["TypeScript", "JavaScript", "Let me decide later"]
            ... )
            >>> if result.success:
            ...     print(f"User chose: {result.answer}")

            >>> # Another example with 2 options
            >>> result = agent_ask_human_for_feedback(
            ...     ctx,
            ...     "Which approach should I take for authentication?",
            ...     ["JWT tokens", "Session cookies"]
            ... )
            >>> if result.success:
            ...     print(f"User chose: {result.answer}")

        Best Practices:
            - Keep questions clear and concise
            - ALWAYS provide 2-3 relevant options for the user to choose from
            - Provide context about why you're asking
            - Options should cover the most likely choices
            - Always check result.success before using result.answer
            - Respect the user's answer and don't ask repeatedly
        """
        return ask_human_for_feedback(context, question, options)
