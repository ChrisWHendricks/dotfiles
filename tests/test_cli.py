"""Tests for CLI commands."""

from click.testing import CliRunner
import pytest

from dot.cli import cli


@pytest.fixture
def runner():
    """Create a CLI runner for testing."""
    return CliRunner()


def test_cli_version(runner):
    """Test --version flag."""
    result = runner.invoke(cli, ["--version"])
    assert result.exit_code == 0
    assert "version" in result.output.lower()


def test_cli_help(runner):
    """Test --help flag."""
    result = runner.invoke(cli, ["--help"])
    assert result.exit_code == 0
    assert "Modern CLI tool" in result.output
    assert "check" in result.output
    assert "install" in result.output
    assert "tools" in result.output


def test_check_command(runner):
    """Test check command runs."""
    result = runner.invoke(cli, ["check"])
    # May exit with 0 or 1 depending on system state
    assert result.exit_code in [0, 1]
    assert "Dotfiles Status Check" in result.output


def test_install_dry_run(runner):
    """Test install command with dry-run."""
    result = runner.invoke(cli, ["install", "--dry-run"])
    assert result.exit_code == 0
    assert "DRY RUN" in result.output


def test_tools_list(runner):
    """Test tools list command."""
    result = runner.invoke(cli, ["tools", "list", "--category", "essential"])
    assert result.exit_code == 0
    assert "Development Tools" in result.output
