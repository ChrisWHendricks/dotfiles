"""Utilities for managing Claude Code profiles and settings."""

import json
import shutil
from datetime import datetime
from pathlib import Path
from typing import Dict, Optional

from dot.core.config import config as config_manager


def get_claude_settings_path() -> Path:
    """Get the path to the Claude Code settings file.

    Returns:
        Path to settings.json
    """
    return Path.home() / ".claude" / "settings.json"


def backup_settings_file() -> Optional[Path]:
    """Backup current Claude settings file.

    Returns:
        Path to the backup file, or None if settings.json doesn't exist.
    """
    settings_path = get_claude_settings_path()

    if not settings_path.exists():
        return None

    # Create backup with timestamp
    timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    backup_path = settings_path.parent / f"settings.backup-{timestamp}.json"

    shutil.copy2(settings_path, backup_path)
    backup_path.chmod(0o600)

    return backup_path


def restore_settings_file(profile: str) -> bool:
    """Restore settings file for the specified profile.

    Args:
        profile: Profile name ('bedrock' or 'personal').

    Returns:
        True if successful, False otherwise.
    """
    # Get the profile-specific settings file path
    settings_file_key = f"claude.{profile}.settings_file"
    settings_file = config_manager.get(settings_file_key)

    if not settings_file:
        return False

    # Expand user home directory
    source_path = Path(settings_file).expanduser()

    if not source_path.exists():
        return False

    # Backup current settings first
    backup_settings_file()

    # Copy profile settings to settings.json
    dest_path = get_claude_settings_path()
    shutil.copy2(source_path, dest_path)
    dest_path.chmod(0o600)

    return True


def get_profile_env_vars(profile: str) -> Dict[str, Optional[str]]:
    """Get environment variables for the specified profile.

    Args:
        profile: Profile name ('bedrock' or 'personal').

    Returns:
        Dictionary mapping variable names to values (None means unset).
    """
    if profile == "bedrock":
        aws_profile = config_manager.get("claude.bedrock.aws_profile", "ClaudeCodeUnix")
        aws_region = config_manager.get("claude.bedrock.aws_region", "us-west-2")

        return {
            "AWS_PROFILE": aws_profile,
            "AWS_REGION": aws_region,
            "AWS_DEFAULT_REGION": aws_region,
            "CLAUDE_CODE_USE_BEDROCK": "1",
            "CLAUDE_CODE_ENABLE_TELEMETRY": "1",
            "OTEL_EXPORTER_OTLP_ENDPOINT": "https://claudecode-telemetry.tylertechai.com",
            "OTEL_EXPORTER_OTLP_PROTOCOL": "http/protobuf",
            "OTEL_LOGS_EXPORTER": "otlp",
            "OTEL_METRICS_EXPORTER": "otlp",
            "OTEL_RESOURCE_ATTRIBUTES": "department=engineering,team.id=default,cost_center=default,organization=default",
        }
    elif profile == "personal":
        # Personal profile unsets all AWS and telemetry variables
        return {
            "AWS_PROFILE": None,
            "AWS_REGION": None,
            "AWS_DEFAULT_REGION": None,
            "CLAUDE_CODE_USE_BEDROCK": None,
            "CLAUDE_CODE_ENABLE_TELEMETRY": None,
            "OTEL_EXPORTER_OTLP_ENDPOINT": None,
            "OTEL_EXPORTER_OTLP_PROTOCOL": None,
            "OTEL_LOGS_EXPORTER": None,
            "OTEL_METRICS_EXPORTER": None,
            "OTEL_RESOURCE_ATTRIBUTES": None,
        }
    else:
        return {}


def generate_shell_commands(profile: str) -> str:
    """Generate shell commands to set/unset environment variables.

    Args:
        profile: Profile name ('bedrock' or 'personal').

    Returns:
        Shell commands as a string.
    """
    env_vars = get_profile_env_vars(profile)
    commands = []

    for var_name, var_value in env_vars.items():
        if var_value is None:
            commands.append(f"unset {var_name}")
        else:
            # Escape any special characters in the value
            escaped_value = var_value.replace('"', '\\"')
            commands.append(f'export {var_name}="{escaped_value}"')

    return "\n".join(commands)


def get_current_profile_from_env() -> Optional[str]:
    """Detect the current Claude profile from environment variables.

    Returns:
        Profile name ('bedrock' or 'personal') or None if cannot determine.
    """
    import os

    # If CLAUDE_CODE_USE_BEDROCK is set, it's bedrock profile
    if os.environ.get("CLAUDE_CODE_USE_BEDROCK") == "1":
        return "bedrock"

    # If AWS_PROFILE is set for ClaudeCodeUnix, probably bedrock
    if os.environ.get("AWS_PROFILE") == "ClaudeCodeUnix":
        return "bedrock"

    # If none of the bedrock markers are present, likely personal
    if not os.environ.get("CLAUDE_CODE_USE_BEDROCK") and not os.environ.get("OTEL_EXPORTER_OTLP_ENDPOINT"):
        return "personal"

    return None


def verify_settings_file(profile: str) -> bool:
    """Verify that the settings file for a profile exists.

    Args:
        profile: Profile name ('bedrock' or 'personal').

    Returns:
        True if the settings file exists, False otherwise.
    """
    settings_file_key = f"claude.{profile}.settings_file"
    settings_file = config_manager.get(settings_file_key)

    if not settings_file:
        return False

    source_path = Path(settings_file).expanduser()
    return source_path.exists()
