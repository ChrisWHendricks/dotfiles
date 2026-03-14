"""Configuration command for managing dotfiles settings."""

import os
import subprocess
from pathlib import Path
from typing import Any

import click
import questionary

from dot.core.config import (
    config as config_manager,
    Config,
    ConfigValidationError,
    DEFAULT_CONFIG,
    VALIDATION_RULES,
)
from dot.utils.claude import (
    backup_settings_file,
    generate_shell_commands,
    get_current_profile_from_env,
    get_profile_env_vars,
    restore_settings_file,
    verify_settings_file,
)
from dot.utils.output import (
    console,
    create_table,
    print_error,
    print_header,
    print_info,
    print_success,
    print_table,
    print_warning,
)


@click.group()
def config_cmd():
    """Manage dotfiles configuration settings.

    Use 'dot config <subcommand> --help' for more information.
    """
    pass


@config_cmd.command()
@click.option("--format", "output_format", type=click.Choice(["table", "yaml"]), default="table", help="Output format")
def list(output_format):
    """Display all configuration settings."""
    print_header("Configuration Settings")

    user_config = config_manager.load_user_config()

    if output_format == "yaml":
        import yaml
        console.print(yaml.safe_dump(user_config or {}, default_flow_style=False, sort_keys=False))
        return

    # Table format
    table = create_table(columns=["Key", "Value", "Default", "Description"])

    def _add_rows(prefix: str, rules_dict: dict):
        """Recursively add rows for all validation rules."""
        for key, rule in sorted(rules_dict.items()):
            current_value = config_manager.get(key)
            default_value = config_manager.get_default(key)
            description = rule.get("description", "")

            # Format values
            current_str = str(current_value) if current_value is not None else "[dim]not set[/dim]"
            default_str = str(default_value) if default_value is not None else "[dim]none[/dim]"

            # Highlight if different from default
            if current_value != default_value:
                current_str = f"[cyan]{current_str}[/cyan]"

            table.add_row(key, current_str, default_str, description)

    _add_rows("", VALIDATION_RULES)

    print_table(table)


@config_cmd.command()
@click.argument("key")
def get(key):
    """Get a specific configuration value.

    Examples:
        dot config get claude.active_profile
        dot config get backup.enabled
    """
    value = config_manager.get(key)
    default_value = config_manager.get_default(key)

    if value is None:
        print_warning(f"{key} is not set")
        if default_value is not None:
            console.print(f"[dim]Default: {default_value}[/dim]")
        return

    console.print(f"{key} = {value}")

    if value != default_value:
        console.print(f"[dim]Default: {default_value}[/dim]")
    else:
        console.print(f"[dim](using default value)[/dim]")


@config_cmd.command()
@click.argument("key")
@click.argument("value")
@click.option("--force", is_flag=True, help="Skip confirmation")
def set(key, value, force):
    """Set a configuration value.

    Examples:
        dot config set claude.active_profile bedrock
        dot config set backup.enabled true
        dot config set backup.retention_days 60
    """
    # Get rule for type conversion
    if key not in VALIDATION_RULES:
        print_error(f"Unknown configuration key: {key}")
        console.print("\nAvailable keys:")
        for k in sorted(VALIDATION_RULES.keys()):
            console.print(f"  • {k}")
        return

    rule = VALIDATION_RULES[key]
    expected_type = rule.get("type")

    # Convert value to the expected type
    try:
        if expected_type == bool:
            # Parse boolean values
            if value.lower() in ["true", "1", "yes", "on"]:
                typed_value = True
            elif value.lower() in ["false", "0", "no", "off"]:
                typed_value = False
            else:
                print_error(f"Invalid boolean value: {value}")
                return
        elif expected_type == int:
            typed_value = int(value)
        else:
            typed_value = value
    except ValueError as e:
        print_error(f"Invalid value type: {e}")
        return

    # Validate the value BEFORE prompting
    try:
        config_manager.validate_key_value(key, typed_value)
    except ConfigValidationError as e:
        print_error(f"Validation error: {e}")
        return

    # Get current value
    current_value = config_manager.get(key)

    # Show what will change
    if not force:
        console.print(f"\n[bold]Setting:[/bold] {key}")
        console.print(f"  Current: {current_value if current_value is not None else '[dim]not set[/dim]'}")
        console.print(f"  New:     [cyan]{typed_value}[/cyan]")
        console.print()

        if not questionary.confirm("Continue?", default=True).ask():
            print_warning("Cancelled")
            return

    # Set the value (validation already done, so this should succeed)
    try:
        config_manager.set(key, typed_value)
        print_success(f"Set {key} = {typed_value}")
    except ConfigValidationError as e:
        # This shouldn't happen since we already validated, but handle it just in case
        print_error(f"Unexpected validation error: {e}")


@config_cmd.command()
@click.argument("key", required=False)
@click.option("--force", is_flag=True, help="Skip confirmation")
def reset(key, force):
    """Reset configuration to defaults.

    Examples:
        dot config reset                      # Reset entire config
        dot config reset claude.active_profile  # Reset specific key
    """
    if key:
        # Reset specific key
        default_value = config_manager.get_default(key)
        current_value = config_manager.get(key)

        if not force:
            console.print(f"\n[bold]Resetting:[/bold] {key}")
            console.print(f"  Current: {current_value if current_value is not None else '[dim]not set[/dim]'}")
            console.print(f"  Default: {default_value if default_value is not None else '[dim]none[/dim]'}")
            console.print()

            if not questionary.confirm("Continue?", default=True).ask():
                print_warning("Cancelled")
                return

        config_manager.reset(key)
        print_success(f"Reset {key} to default value")
    else:
        # Reset entire config
        if not force:
            console.print("\n[bold yellow]Warning:[/bold yellow] This will reset ALL configuration to defaults")
            console.print()

            if not questionary.confirm("Continue?", default=False).ask():
                print_warning("Cancelled")
                return

        config_manager.reset()
        print_success("Reset all configuration to defaults")


@config_cmd.command()
def edit():
    """Open the configuration file in your default editor."""
    config_file = config_manager.user_config_file

    # Ensure config file exists with defaults
    if not config_file.exists():
        print_info("Creating config file with defaults...")
        config_manager._config = DEFAULT_CONFIG.copy()
        config_manager.save_config()

    # Get editor from environment
    editor = os.environ.get("EDITOR", "vim")

    # Open in editor
    try:
        subprocess.run([editor, str(config_file)], check=True)
        print_success("Configuration file saved")

        # Reload and validate
        try:
            config_manager._config = None  # Clear cache
            config_manager.load_user_config()
            print_success("Configuration is valid")
        except Exception as e:
            print_error(f"Configuration validation failed: {e}")
            console.print("\nYou can edit the file again or reset to defaults:")
            console.print(f"  • Edit: {editor} {config_file}")
            console.print("  • Reset: dot config reset --force")

    except subprocess.CalledProcessError:
        print_error("Editor exited with error")
    except FileNotFoundError:
        print_error(f"Editor not found: {editor}")
        console.print(f"\nSet your preferred editor with: export EDITOR=<editor-name>")


@config_cmd.command()
def path():
    """Show the configuration file path."""
    config_file = config_manager.user_config_file

    console.print(f"[bold]Config file:[/bold] {config_file}")

    if config_file.exists():
        stat = config_file.stat()
        console.print(f"  Status: [green]exists[/green]")
        console.print(f"  Size:   {stat.st_size} bytes")
        console.print(f"  Modified: {stat.st_mtime}")
    else:
        console.print(f"  Status: [yellow]does not exist[/yellow]")
        console.print(f"\nCreate with defaults:")
        console.print(f"  dot config set claude.active_profile bedrock")


@config_cmd.command()
@click.argument("profile", required=False, type=click.Choice(["bedrock", "personal"]))
@click.option("--apply", is_flag=True, help="Apply settings and generate shell commands")
def claude(profile, apply):
    """Manage Claude profile (bedrock or personal).

    Examples:
        dot config claude                 # Show current profile
        dot config claude bedrock        # Switch to bedrock
        dot config claude personal       # Switch to personal
        dot config claude bedrock --apply  # Switch and generate shell commands
    """
    current_profile = config_manager.get("claude.active_profile", "bedrock")

    # Show current profile if no profile specified
    if not profile:
        print_header("Claude Profile")
        console.print(f"Active profile: [cyan]{current_profile}[/cyan]")

        # Show profile details
        console.print()
        if current_profile == "bedrock":
            aws_profile = config_manager.get("claude.bedrock.aws_profile", "ClaudeCodeUnix")
            aws_region = config_manager.get("claude.bedrock.aws_region", "us-west-2")
            console.print(f"AWS Profile: {aws_profile}")
            console.print(f"AWS Region:  {aws_region}")
            console.print("Telemetry:   enabled")
        else:
            console.print("No AWS configuration")
            console.print("Telemetry:   disabled")

        # Show environment detection
        env_profile = get_current_profile_from_env()
        if env_profile and env_profile != current_profile:
            console.print()
            print_warning(f"Environment suggests profile: {env_profile}")
            console.print("Run with --apply to sync environment")

        return

    # Switch profile
    if profile == current_profile:
        print_info(f"Already using {profile} profile")
        if not apply:
            return

    # Verify settings file exists
    if not verify_settings_file(profile):
        settings_file = config_manager.get(f"claude.{profile}.settings_file")
        print_error(f"Settings file not found: {settings_file}")
        console.print("\nCreate the file or update the path:")
        console.print(f"  dot config set claude.{profile}.settings_file <path>")
        return

    # Update active profile
    try:
        config_manager.set("claude.active_profile", profile)
        print_success(f"Switched to {profile} profile")
    except ConfigValidationError as e:
        print_error(f"Failed to switch profile: {e}")
        return

    # Apply changes if requested
    if apply:
        # Backup and restore settings file
        backup_path = backup_settings_file()
        if backup_path:
            print_info(f"Backed up settings to: {backup_path.name}")

        if restore_settings_file(profile):
            print_success("Settings file updated")
        else:
            print_error("Failed to update settings file")
            return

        # Generate shell commands
        console.print()
        console.print("[bold]Shell commands to apply:[/bold]")
        console.print()
        commands = generate_shell_commands(profile)
        console.print(commands)
        console.print()
        console.print("[dim]# To apply in your current shell, run:[/dim]")
        console.print(f"[dim]# eval \"$(dot config claude {profile} --apply)\"[/dim]")
    else:
        console.print()
        console.print(f"Profile updated to [cyan]{profile}[/cyan]")
        console.print()
        console.print("To apply the changes:")
        console.print(f"  eval \"$(dot config claude {profile} --apply)\"")


@config_cmd.command()
@click.argument("profile", required=False, type=click.Choice(["bedrock", "personal"]))
def env(profile):
    """Print environment commands for a profile.

    This command outputs shell commands that can be evaluated
    to set/unset environment variables for the specified profile.

    Examples:
        eval "$(dot config claude env)"          # Use active profile
        eval "$(dot config claude env bedrock)"  # Force bedrock
        eval "$(dot config claude env personal)" # Force personal
    """
    # Use specified profile or get from config
    if not profile:
        profile = config_manager.get("claude.active_profile", "bedrock")

    # Generate and print shell commands
    commands = generate_shell_commands(profile)
    console.print(commands)


# Register the command group
config = config_cmd
