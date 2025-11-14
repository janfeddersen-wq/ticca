"""
GAC (Git Auto Commit) wrapper for ticca.

This module provides integration between ticca and gac, allowing ticca
to use its own model configuration and API keys to generate git commit messages.
"""

import os
import subprocess
from pathlib import Path
from typing import Optional

from ticca.config import get_global_model_name, get_gac_model, get_gac_enabled
from ticca.messaging import emit_error, emit_info, emit_warning
from ticca.model_factory import ModelFactory


def _get_gac_provider_and_model(model_name: str) -> tuple[Optional[str], Optional[str]]:
    """
    Get the GAC provider and model name from ticca's model configuration.

    Args:
        model_name: The ticca model name

    Returns:
        Tuple of (gac_provider, gac_model_name) or (None, None) if not found
        Format for GAC: provider:model_name (e.g., "anthropic:claude-haiku-4-5")
    """
    try:
        config = ModelFactory.load_config()
        model_config = config.get(model_name)

        if not model_config:
            return None, None

        model_type = model_config.get("type")
        actual_model_name = model_config.get("name", model_name)

        # Map ticca model types to GAC provider names
        # GAC providers: anthropic, cerebras, claude-code, custom-anthropic, custom-openai,
        # deepseek, fireworks, gemini, groq, lm-studio, minimax, mistral, ollama,
        # openai, openrouter, streamlake, synthetic, together, zai, zai-coding
        provider_map = {
            "openai": "openai",
            "custom_openai": "custom-openai",
            "anthropic": "anthropic",
            "custom_anthropic": "custom-anthropic",
            "claude_code": "claude-code",
            "gemini": "gemini",
            "custom_gemini": "gemini",
            "cerebras": "cerebras",
            "azure_openai": "openai",
            "openrouter": "openrouter",
            "deepseek": "deepseek",
            "groq": "groq",
            "ollama": "ollama",
            "mistral": "mistral",
            "together": "together",
            "fireworks": "fireworks",
            "synthetic": "synthetic",
        }

        gac_provider = provider_map.get(model_type)
        if not gac_provider:
            emit_warning(f"Unknown model type for GAC: {model_type}")
            return None, None

        return gac_provider, actual_model_name

    except Exception as e:
        emit_warning(f"Failed to load model configuration: {e}")
        return None, None


def _ensure_api_keys_in_environment():
    """
    Ensure all API keys from ticca config are loaded into environment variables.
    GAC reads API keys directly from os.environ, so we need to set them.
    """
    from ticca.config import load_api_keys_to_environment

    # This function loads API keys from both .env and puppy.cfg into environment
    load_api_keys_to_environment()


def _check_git_repository() -> bool:
    """Check if we're in a git repository."""
    try:
        result = subprocess.run(
            ["git", "rev-parse", "--is-inside-work-tree"],
            capture_output=True,
            text=True,
            check=False
        )
        return result.returncode == 0
    except FileNotFoundError:
        emit_error("git command not found. Please ensure git is installed.")
        return False


def _check_staged_changes() -> bool:
    """Check if there are any staged changes."""
    try:
        result = subprocess.run(
            ["git", "diff", "--cached", "--quiet"],
            check=False
        )
        # Returns 0 if no changes, 1 if there are changes
        return result.returncode == 1
    except Exception as e:
        emit_warning(f"Failed to check staged changes: {e}")
        return False


def _stage_all_changes() -> bool:
    """Stage all changes in the current repository."""
    try:
        result = subprocess.run(
            ["git", "add", "."],
            capture_output=True,
            text=True,
            check=False
        )

        if result.returncode == 0:
            emit_info("✓ Staged all changes")
            return True
        else:
            emit_error(f"Failed to stage changes: {result.stderr.strip()}")
            return False
    except Exception as e:
        emit_error(f"Failed to stage changes: {e}")
        return False


def _get_git_diff() -> Optional[str]:
    """Get the staged git diff."""
    try:
        result = subprocess.run(
            ["git", "diff", "--cached"],
            capture_output=True,
            text=True,
            check=False
        )

        if result.returncode == 0:
            return result.stdout
        return None
    except Exception as e:
        emit_warning(f"Failed to get git diff: {e}")
        return None


def generate_commit_message(
    model_name: Optional[str] = None,
    one_liner: bool = False,
    language: str = "en",
    hint: Optional[str] = None,
    stage_all: bool = False
) -> Optional[str]:
    """
    Generate a commit message using GAC with ticca's model configuration.

    Args:
        model_name: The ticca model name to use (defaults to configured gac model or global model)
        one_liner: Generate a one-line commit message
        language: Language for the commit message (default: 'en')
        hint: Additional context hint for the commit message
        stage_all: Whether to stage all changes before generating (default: False)

    Returns:
        Generated commit message or None if generation failed
    """
    # Check if gac is enabled
    if not get_gac_enabled():
        emit_error("GAC plugin is disabled. Enable it in settings (Ctrl+3)")
        return None

    # Validate git repository
    if not _check_git_repository():
        emit_error("Not in a git repository")
        return None

    # Stage all changes if requested
    if stage_all:
        if not _stage_all_changes():
            return None

    # Check for staged changes
    if not _check_staged_changes():
        emit_warning("No staged changes found. Stage your changes with 'git add' first.")
        return None

    # Get model configuration - priority: 1) provided model_name, 2) configured gac model, 3) global model
    if model_name is None:
        gac_model = get_gac_model()
        if gac_model:
            model_name = gac_model
        else:
            model_name = get_global_model_name()

    # Get GAC provider and model name
    gac_provider, gac_model_name = _get_gac_provider_and_model(model_name)

    if not gac_provider or not gac_model_name:
        emit_error(f"Could not determine GAC provider for model: {model_name}")
        return None

    # Ensure API keys are loaded into environment variables
    # GAC reads API keys directly from environment variables
    _ensure_api_keys_in_environment()

    # Format model string for GAC: provider:model_name
    gac_model_string = f"{gac_provider}:{gac_model_name}"

    emit_info(f"Using GAC with {gac_model_string} to generate commit message...")

    try:
        # Import GAC functions
        from gac.git import get_diff, get_staged_status
        from gac.prompt import build_prompt
        from gac.main import generate_commit_message as gac_generate

        # Get the staged diff using GAC's git module
        diff_text = get_diff(staged=True, color=False)
        if not diff_text:
            emit_error("No staged changes to generate message from")
            return None

        # Get the status summary
        status_text = get_staged_status()

        # Build the prompt using GAC's prompt builder
        system_prompt, user_prompt = build_prompt(
            status=status_text,
            processed_diff=diff_text,
            diff_stat="",  # Optional diff statistics
            one_liner=one_liner,
            hint=hint or "",
            language=language if language != "en" else None,
        )

        # Generate the commit message using GAC
        message = gac_generate(
            model=gac_model_string,
            prompt=(system_prompt, user_prompt),
            quiet=True,  # Suppress GAC's own output
            skip_success_message=True,
        )

        if message:
            return message.strip()
        else:
            emit_error("GAC returned empty commit message")
            return None

    except ImportError as e:
        emit_error(
            f"Failed to import gac library: {e}\n"
            "Please install gac: uv tool install gac or pip install gac"
        )
        return None
    except Exception as e:
        emit_error(f"Failed to generate commit message: {e}")
        return None


def create_commit(
    model_name: Optional[str] = None,
    one_liner: bool = False,
    language: str = "en",
    hint: Optional[str] = None,
    no_verify: bool = False,
    stage_all: bool = False
) -> bool:
    """
    Generate a commit message and create a git commit.

    Args:
        model_name: The ticca model name to use (defaults to global model)
        one_liner: Generate a one-line commit message
        language: Language for the commit message (default: 'en')
        hint: Additional context hint for the commit message
        no_verify: Skip git hooks (--no-verify)
        stage_all: Whether to stage all changes before generating (default: False)

    Returns:
        True if commit was created successfully, False otherwise
    """
    message = generate_commit_message(model_name, one_liner, language, hint, stage_all)

    if not message:
        return False

    emit_info(f"\nGenerated commit message:\n\n{message}\n")

    # Create the commit
    cmd = ["git", "commit", "-m", message]

    if no_verify:
        cmd.append("--no-verify")

    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            check=False
        )

        if result.returncode == 0:
            emit_info(f"✓ Commit created successfully")
            # Show the commit output
            if result.stdout:
                emit_info(result.stdout.strip())
            return True
        else:
            emit_error(f"Failed to create commit: {result.stderr.strip()}")
            return False

    except Exception as e:
        emit_error(f"Failed to create commit: {e}")
        return False
