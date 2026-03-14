"""Tests for platform detection utilities."""

import pytest

from dot.core.platform import (
    Platform,
    detect_platform,
    get_package_manager,
    is_macos,
    is_linux,
    get_home_dir,
)


def test_detect_platform():
    """Test platform detection returns a valid Platform enum."""
    platform = detect_platform()
    assert isinstance(platform, Platform)
    assert platform in [Platform.MACOS, Platform.LINUX, Platform.WINDOWS, Platform.UNKNOWN]


def test_platform_helpers():
    """Test platform helper functions are consistent."""
    # At least one should be True (or none for unknown platforms)
    platform_checks = [is_macos(), is_linux()]
    # Exactly one should be True on supported platforms
    detected = detect_platform()
    if detected == Platform.MACOS:
        assert is_macos() is True
        assert is_linux() is False
    elif detected == Platform.LINUX:
        assert is_macos() is False
        assert is_linux() is True


def test_get_package_manager():
    """Test package manager detection."""
    pm = get_package_manager()
    # Should return a string or None
    assert pm is None or isinstance(pm, str)

    # On macOS, should typically be 'brew'
    if is_macos():
        # May be None if Homebrew not installed
        assert pm in [None, "brew"]


def test_get_home_dir():
    """Test home directory detection."""
    home = get_home_dir()
    assert home.exists()
    assert home.is_dir()
    # Home directory should be absolute
    assert home.is_absolute()
