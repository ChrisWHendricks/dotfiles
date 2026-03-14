"""Check command for verifying dotfiles status."""

import sys
from pathlib import Path

import click

from dot.core.config import config
from dot.core.platform import detect_platform, is_vscode_installed
from dot.core.symlink import SymlinkManager
from dot.utils.output import (
    console,
    print_error,
    print_header,
    print_success,
    print_warning,
    create_table,
    print_table,
)
from dot.utils.shell import command_exists, get_command_version


@click.command()
def check():
    """Check dotfiles installation status and system configuration.

    Verifies:
    - Dotfiles repository location
    - Python version
    - Platform detection
    - Symlink status
    - Tool installation
    """
    print_header("Dotfiles Status Check")

    issues_found = 0
    symlink_mgr = SymlinkManager()

    # Check repository
    console.print()
    try:
        dotfiles_root = config.dotfiles_root
        if dotfiles_root.exists():
            print_success(f"Dotfiles repository: {dotfiles_root}")
        else:
            print_error(f"Dotfiles repository not found: {dotfiles_root}")
            issues_found += 1
    except Exception as e:
        print_error(f"Error locating dotfiles repository: {e}")
        issues_found += 1

    # Check Python version
    python_version = f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}"
    print_success(f"Python version: {python_version}")

    # Check platform
    platform = detect_platform()
    print_success(f"Platform: {platform.value}")

    # Check symlinks
    print_header("Symlinks")

    # Load dotfiles map if it exists
    dotfiles_map_path = config.dotfiles_root / "dot" / "data" / "dotfiles_map.yaml"
    if dotfiles_map_path.exists():
        try:
            dotfiles_map = config.load_data_file("dotfiles_map.yaml")
            dotfiles = dotfiles_map.get("dotfiles", [])

            for item in dotfiles:
                src_rel = item.get("source")
                dest_str = item.get("destination")
                platforms = item.get("platforms", [])

                # Skip if not for current platform
                if platforms and platform.value not in platforms:
                    continue

                # Check condition
                condition = item.get("condition")
                if condition == "vscode_installed" and not is_vscode_installed():
                    continue

                src = config.dotfiles_root / src_rel
                dest = Path(dest_str).expanduser()

                if symlink_mgr.is_our_symlink(dest, src):
                    print_success(f"{dest.name} → {src}")
                elif dest.exists():
                    if dest.is_symlink():
                        target = symlink_mgr.get_symlink_target(dest)
                        print_warning(f"{dest.name} (points to {target})")
                    else:
                        print_warning(f"{dest.name} (exists but not linked)")
                    issues_found += 1
                else:
                    print_error(f"{dest.name} (not linked)")
                    issues_found += 1

        except FileNotFoundError:
            print_warning("No dotfiles_map.yaml found - skipping symlink check")
        except Exception as e:
            print_error(f"Error checking symlinks: {e}")
            issues_found += 1
    else:
        print_warning("No dotfiles_map.yaml found - skipping symlink check")

    # Check tools
    print_header("Tools")

    essential_tools = [
        ("git", "Version control"),
        ("tmux", "Terminal multiplexer"),
        ("vim", "Text editor"),
    ]

    table = create_table(columns=["Tool", "Status", "Version"])

    for tool, description in essential_tools:
        if command_exists(tool):
            version = get_command_version(tool)
            version_str = version.split()[0] if version else "unknown"
            table.add_row(f"[green]{tool}[/green]", f"[green]✓ installed[/green]", version_str)
        else:
            table.add_row(f"[red]{tool}[/red]", f"[red]✗ not installed[/red]", "-")
            issues_found += 1

    print_table(table)

    # Summary
    console.print()
    if issues_found == 0:
        print_success("All checks passed!")
    else:
        print_warning(f"Status: {issues_found} issue(s) found")
        console.print(
            "\n[dim]Run 'dot install' to fix symlink issues or 'dot tools install' to install missing tools.[/dim]"
        )

    sys.exit(0 if issues_found == 0 else 1)
