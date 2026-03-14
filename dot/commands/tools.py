"""Tools command for managing development tools and applications."""

import subprocess
from typing import Dict, List, Optional

import click
import questionary

from dot.core.config import config
from dot.core.platform import detect_platform, get_package_manager, Platform
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
from dot.utils.shell import command_exists, run_command


class ToolManager:
    """Manages tool installation and updates."""

    def __init__(self):
        """Initialize tool manager."""
        self.platform = detect_platform()
        self.package_manager = get_package_manager()
        self.tools_data = self._load_tools_data()

    def _load_tools_data(self) -> Dict:
        """Load tools configuration for current platform."""
        if self.platform == Platform.MACOS:
            return config.load_data_file("tools_macos.yaml")
        elif self.platform == Platform.LINUX:
            return config.load_data_file("tools_linux.yaml")
        else:
            return {"categories": {}}

    def get_all_tools(self, category: Optional[str] = None) -> List[Dict]:
        """Get all tools, optionally filtered by category.

        Args:
            category: Optional category to filter by.

        Returns:
            List of tool dictionaries.
        """
        categories = self.tools_data.get("categories", {})

        if category:
            return categories.get(category, [])

        # Return all tools from all categories
        all_tools = []
        for cat_tools in categories.values():
            all_tools.extend(cat_tools)
        return all_tools

    def is_tool_installed(self, tool: Dict) -> bool:
        """Check if a tool is installed.

        Args:
            tool: Tool dictionary.

        Returns:
            True if installed, False otherwise.
        """
        name = tool.get("name", "").lower()

        # Check custom check command
        check_cmd = tool.get("check_command")
        if check_cmd:
            returncode, _, _ = run_command(check_cmd, check=False)
            return returncode == 0

        # Check for brew/apt package
        if self.platform == Platform.MACOS:
            brew_name = tool.get("brew") or tool.get("brew_cask")
            if brew_name:
                returncode, stdout, _ = run_command(f"brew list {brew_name}", check=False)
                return returncode == 0

        elif self.platform == Platform.LINUX:
            if self.package_manager in ["apt", "apt-get"]:
                apt_name = tool.get("apt")
                if apt_name:
                    returncode, stdout, _ = run_command(
                        f"dpkg -l {apt_name}", check=False
                    )
                    return returncode == 0

        # Fallback: check if command exists
        # Extract binary name from tool name
        binary_name = name.split()[0].lower()
        return command_exists(binary_name)

    def install_tool(self, tool: Dict, dry_run: bool = False) -> bool:
        """Install a tool.

        Args:
            tool: Tool dictionary.
            dry_run: If True, only show what would be done.

        Returns:
            True if installation was successful, False otherwise.
        """
        name = tool.get("name")

        # Check if already installed
        if self.is_tool_installed(tool):
            print_info(f"{name} is already installed")
            return True

        # Custom installation method
        install_method = tool.get("install_method")
        if install_method == "custom":
            install_cmd = tool.get("install_command")
            if not install_cmd:
                print_error(f"No install command for {name}")
                return False

            print_info(f"Installing {name}...")
            if dry_run:
                print_info(f"Would run: {install_cmd}")
                return True

            returncode, stdout, stderr = run_command(install_cmd, check=False)
            if returncode == 0:
                print_success(f"Installed {name}")
                return True
            else:
                print_error(f"Failed to install {name}: {stderr}")
                return False

        # Homebrew installation (macOS)
        if self.platform == Platform.MACOS and self.package_manager == "brew":
            # Check if tap is needed
            tap = tool.get("tap")
            if tap:
                print_info(f"Tapping {tap}...")
                if not dry_run:
                    run_command(f"brew tap {tap}", check=False)

            # Install with brew or brew cask
            brew_name = tool.get("brew")
            brew_cask = tool.get("brew_cask")

            if brew_cask:
                cmd = f"brew install --cask {brew_cask}"
            elif brew_name:
                cmd = f"brew install {brew_name}"
            else:
                print_error(f"No brew package name for {name}")
                return False

            print_info(f"Installing {name}...")
            if dry_run:
                print_info(f"Would run: {cmd}")
                return True

            returncode, stdout, stderr = run_command(cmd, check=False)
            if returncode == 0:
                print_success(f"Installed {name}")
                return True
            else:
                print_error(f"Failed to install {name}: {stderr}")
                return False

        # APT installation (Linux)
        elif self.platform == Platform.LINUX and self.package_manager in ["apt", "apt-get"]:
            apt_name = tool.get("apt")
            if not apt_name:
                print_error(f"No apt package name for {name}")
                return False

            cmd = f"sudo apt-get install -y {apt_name}"
            print_info(f"Installing {name}...")
            if dry_run:
                print_info(f"Would run: {cmd}")
                return True

            returncode, stdout, stderr = run_command(cmd, check=False)
            if returncode == 0:
                print_success(f"Installed {name}")
                return True
            else:
                print_error(f"Failed to install {name}: {stderr}")
                return False

        print_error(f"Don't know how to install {name} on this platform")
        return False


@click.group()
def tools():
    """Manage development tools and applications.

    Use 'dot tools <subcommand> --help' for more information.
    """
    pass


@tools.command()
@click.option("--installed", is_flag=True, help="Show only installed tools")
@click.option("--category", help="Filter by category")
def list(installed, category):
    """List available tools and their installation status."""
    print_header("Development Tools")

    manager = ToolManager()
    tools_list = manager.get_all_tools(category)

    if not tools_list:
        print_warning("No tools found")
        return

    # Group by category
    categories = manager.tools_data.get("categories", {})

    for cat_name, cat_tools in categories.items():
        if category and cat_name != category:
            continue

        console.print(f"\n[bold cyan]{cat_name.replace('_', ' ').title()}[/bold cyan]")

        table = create_table(columns=["Tool", "Status", "Description"])

        for tool in cat_tools:
            name = tool.get("name", "")
            desc = tool.get("description", "")
            is_installed = manager.is_tool_installed(tool)

            if installed and not is_installed:
                continue

            status = "[green]✓ installed[/green]" if is_installed else "[dim]not installed[/dim]"
            table.add_row(name, status, desc)

        print_table(table)


@tools.command()
@click.argument("tool_names", nargs=-1, required=False)
@click.option("--all", "install_all", is_flag=True, help="Install all tools")
@click.option("--category", help="Install all tools in a category")
@click.option("--dry-run", is_flag=True, help="Show what would be installed")
@click.option("--force", is_flag=True, help="Skip confirmation prompts")
def install(tool_names, install_all, category, dry_run, force):
    """Install development tools.

    Examples:
        dot tools install git tmux     # Install specific tools
        dot tools install --all        # Install all tools
        dot tools install --category essential  # Install essential tools
    """
    manager = ToolManager()

    # Check if package manager is available
    if not manager.package_manager:
        print_error(f"No package manager found for {manager.platform.value}")
        print_info("Please install Homebrew (macOS) or ensure apt/yum is available (Linux)")
        return

    # Determine which tools to install
    tools_to_install = []

    if install_all:
        tools_to_install = manager.get_all_tools()
    elif category:
        tools_to_install = manager.get_all_tools(category)
    elif tool_names:
        # Find tools by name
        all_tools = manager.get_all_tools()
        for name in tool_names:
            matching = [t for t in all_tools if t.get("name", "").lower() == name.lower()]
            if matching:
                tools_to_install.extend(matching)
            else:
                print_warning(f"Tool not found: {name}")
    else:
        print_error("Please specify tools to install or use --all")
        return

    if not tools_to_install:
        print_warning("No tools to install")
        return

    # Show what will be installed
    print_header(f"Installing {len(tools_to_install)} tool(s)")
    for tool in tools_to_install:
        name = tool.get("name")
        if manager.is_tool_installed(tool):
            print_info(f"{name} (already installed)")
        else:
            console.print(f"  • {name}")

    # Confirm
    if not force and not dry_run:
        console.print()
        if not questionary.confirm("Continue?", default=True).ask():
            print_warning("Installation cancelled")
            return

    # Install tools
    console.print()
    success_count = 0
    failed_count = 0

    for tool in tools_to_install:
        if manager.install_tool(tool, dry_run):
            success_count += 1
        else:
            failed_count += 1

    # Summary
    console.print()
    if dry_run:
        print_success("Dry run complete!")
    elif failed_count == 0:
        print_success(f"Successfully installed {success_count} tool(s)!")
    else:
        print_warning(f"Installed {success_count}, failed {failed_count}")


@tools.command()
def update():
    """Update all installed tools."""
    print_header("Updating Tools")

    manager = ToolManager()

    if not manager.package_manager:
        print_error(f"No package manager found for {manager.platform.value}")
        return

    # Update package manager
    if manager.platform == Platform.MACOS and manager.package_manager == "brew":
        print_info("Updating Homebrew...")
        run_command("brew update", check=False)
        print_info("Upgrading packages...")
        run_command("brew upgrade", check=False)
        print_success("Update complete!")

    elif manager.platform == Platform.LINUX and manager.package_manager in ["apt", "apt-get"]:
        print_info("Updating package lists...")
        run_command("sudo apt-get update", check=False)
        print_info("Upgrading packages...")
        run_command("sudo apt-get upgrade -y", check=False)
        print_success("Update complete!")
