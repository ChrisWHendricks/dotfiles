"""Platform detection and platform-specific utilities."""

import platform
import shutil
from enum import Enum
from pathlib import Path
from typing import Optional


class Platform(Enum):
    """Supported platforms."""

    MACOS = "macos"
    LINUX = "linux"
    WINDOWS = "windows"
    UNKNOWN = "unknown"


def detect_platform() -> Platform:
    """Detect the current operating system platform.

    Returns:
        Platform enum value representing the current OS.
    """
    system = platform.system().lower()

    if system == "darwin":
        return Platform.MACOS
    elif system == "linux":
        return Platform.LINUX
    elif system == "windows":
        return Platform.WINDOWS
    else:
        return Platform.UNKNOWN


def is_macos() -> bool:
    """Check if running on macOS."""
    return detect_platform() == Platform.MACOS


def is_linux() -> bool:
    """Check if running on Linux."""
    return detect_platform() == Platform.LINUX


def is_windows() -> bool:
    """Check if running on Windows."""
    return detect_platform() == Platform.WINDOWS


def get_package_manager() -> Optional[str]:
    """Detect the system package manager.

    Returns:
        Package manager name (e.g., 'brew', 'apt', 'yum') or None if not found.
    """
    current_platform = detect_platform()

    if current_platform == Platform.MACOS:
        if shutil.which("brew"):
            return "brew"
        return None

    elif current_platform == Platform.LINUX:
        # Check for various Linux package managers in order of preference
        if shutil.which("apt"):
            return "apt"
        elif shutil.which("apt-get"):
            return "apt-get"
        elif shutil.which("yum"):
            return "yum"
        elif shutil.which("dnf"):
            return "dnf"
        elif shutil.which("pacman"):
            return "pacman"
        elif shutil.which("zypper"):
            return "zypper"
        return None

    return None


def get_home_dir() -> Path:
    """Get the user's home directory.

    Returns:
        Path to the user's home directory.
    """
    return Path.home()


def get_config_dir() -> Path:
    """Get the user's config directory.

    Returns:
        Path to the user's config directory (~/.config on Linux/macOS).
    """
    current_platform = detect_platform()

    if current_platform == Platform.MACOS or current_platform == Platform.LINUX:
        config_dir = get_home_dir() / ".config"
        config_dir.mkdir(parents=True, exist_ok=True)
        return config_dir

    # Windows fallback
    config_dir = get_home_dir() / "AppData" / "Local"
    return config_dir


def get_vscode_user_dir() -> Optional[Path]:
    """Get the VS Code user configuration directory.

    Returns:
        Path to VS Code user directory if it exists, None otherwise.
    """
    current_platform = detect_platform()

    if current_platform == Platform.MACOS:
        vscode_dir = get_home_dir() / "Library" / "Application Support" / "Code" / "User"
    elif current_platform == Platform.LINUX:
        vscode_dir = get_config_dir() / "Code" / "User"
    elif current_platform == Platform.WINDOWS:
        vscode_dir = get_home_dir() / "AppData" / "Roaming" / "Code" / "User"
    else:
        return None

    return vscode_dir if vscode_dir.exists() else None


def is_vscode_installed() -> bool:
    """Check if VS Code is installed.

    Returns:
        True if VS Code is installed, False otherwise.
    """
    # Check if 'code' command is available
    if shutil.which("code"):
        return True

    # Check if VS Code user directory exists
    vscode_dir = get_vscode_user_dir()
    return vscode_dir is not None
