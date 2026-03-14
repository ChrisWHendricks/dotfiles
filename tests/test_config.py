"""Tests for configuration management."""

import json
import os
import tempfile
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest
import yaml

from dot.core.config import (
    Config,
    ConfigValidationError,
    DEFAULT_CONFIG,
    VALIDATION_RULES,
)


@pytest.fixture
def temp_config_dir(tmp_path):
    """Create a temporary config directory."""
    config_dir = tmp_path / "dotfiles"
    config_dir.mkdir(parents=True, exist_ok=True)
    return config_dir


@pytest.fixture
def config_instance(temp_config_dir):
    """Create a Config instance with temporary paths."""
    config = Config()
    # Create a test config file path
    test_config_file = temp_config_dir / "config.yaml"

    # Store the original property method
    original_property = Config.user_config_file

    # Create a custom instance that uses the temp file
    class TestConfig(Config):
        @property
        def user_config_file(self):
            return test_config_file

    test_config = TestConfig()
    test_config._config = None  # Clear cache
    return test_config


class TestConfig:
    """Tests for the Config class."""

    def test_default_config_structure(self):
        """Test that DEFAULT_CONFIG has the expected structure."""
        assert "claude" in DEFAULT_CONFIG
        assert "backup" in DEFAULT_CONFIG
        assert "symlink" in DEFAULT_CONFIG
        assert "tools" in DEFAULT_CONFIG

        assert "active_profile" in DEFAULT_CONFIG["claude"]
        assert "bedrock" in DEFAULT_CONFIG["claude"]
        assert "personal" in DEFAULT_CONFIG["claude"]

    def test_validation_rules_completeness(self):
        """Test that all leaf keys in DEFAULT_CONFIG have validation rules."""
        def check_rules(prefix, config_dict):
            for key, value in config_dict.items():
                full_key = f"{prefix}.{key}" if prefix else key
                if isinstance(value, dict):
                    check_rules(full_key, value)
                else:
                    # Leaf key should have a validation rule
                    assert full_key in VALIDATION_RULES, f"Missing validation rule for {full_key}"

        check_rules("", DEFAULT_CONFIG)

    def test_get_default(self, config_instance):
        """Test getting default values."""
        assert config_instance.get_default("claude.active_profile") == "bedrock"
        assert config_instance.get_default("backup.enabled") is True
        assert config_instance.get_default("backup.retention_days") == 30
        assert config_instance.get_default("nonexistent.key") is None

    def test_get_with_no_config_file(self, config_instance):
        """Test get() returns defaults when no config file exists."""
        assert config_instance.get("claude.active_profile") == "bedrock"
        assert config_instance.get("backup.enabled") is True
        assert config_instance.get("nonexistent.key") is None
        assert config_instance.get("nonexistent.key", "default") == "default"

    def test_set_and_get(self, config_instance):
        """Test setting and getting configuration values."""
        # Set a value
        config_instance.set("claude.active_profile", "personal")
        assert config_instance.get("claude.active_profile") == "personal"

        # Set another value
        config_instance.set("backup.retention_days", 60)
        assert config_instance.get("backup.retention_days") == 60

    def test_set_creates_nested_structure(self, config_instance):
        """Test that set() creates nested dictionary structure."""
        config_instance.set("backup.enabled", False)
        config = config_instance.load_user_config()
        assert "backup" in config
        assert "enabled" in config["backup"]
        assert config["backup"]["enabled"] is False

    def test_save_and_load_config(self, config_instance):
        """Test saving and loading configuration from file."""
        # Set some values
        config_instance.set("claude.active_profile", "personal")
        config_instance.set("backup.retention_days", 45)

        # Clear cache and reload
        config_instance._config = None
        reloaded = config_instance.load_user_config()

        assert reloaded["claude"]["active_profile"] == "personal"
        assert reloaded["backup"]["retention_days"] == 45

    def test_config_file_permissions(self, config_instance):
        """Test that config file is created with correct permissions."""
        config_instance.set("backup.enabled", True)

        # Check file exists and has 0o600 permissions
        config_file = config_instance.user_config_file
        assert config_file.exists()
        # Check only the permission bits (mask with 0o777)
        assert (config_file.stat().st_mode & 0o777) == 0o600

    def test_validate_key_value_valid(self, config_instance):
        """Test validation with valid values."""
        # Should not raise
        config_instance.validate_key_value("claude.active_profile", "bedrock")
        config_instance.validate_key_value("claude.active_profile", "personal")
        config_instance.validate_key_value("backup.enabled", True)
        config_instance.validate_key_value("backup.retention_days", 30)
        config_instance.validate_key_value("backup.retention_days", 365)

    def test_validate_unknown_key(self, config_instance):
        """Test validation with unknown key."""
        with pytest.raises(ConfigValidationError, match="Unknown configuration key"):
            config_instance.validate_key_value("unknown.key", "value")

    def test_validate_invalid_type(self, config_instance):
        """Test validation with wrong type."""
        with pytest.raises(ConfigValidationError, match="Invalid type"):
            config_instance.validate_key_value("backup.enabled", "not a boolean")

        with pytest.raises(ConfigValidationError, match="Invalid type"):
            config_instance.validate_key_value("backup.retention_days", "not an int")

    def test_validate_invalid_enum_value(self, config_instance):
        """Test validation with invalid enum value."""
        with pytest.raises(ConfigValidationError, match="must be one of"):
            config_instance.validate_key_value("claude.active_profile", "invalid")

    def test_validate_out_of_range(self, config_instance):
        """Test validation with out-of-range integer."""
        with pytest.raises(ConfigValidationError, match="must be >= 1"):
            config_instance.validate_key_value("backup.retention_days", 0)

        with pytest.raises(ConfigValidationError, match="must be <= 365"):
            config_instance.validate_key_value("backup.retention_days", 500)

    def test_validate_pattern(self, config_instance):
        """Test validation with regex pattern."""
        # Valid AWS regions
        config_instance.validate_key_value("claude.bedrock.aws_region", "us-west-2")
        config_instance.validate_key_value("claude.bedrock.aws_region", "eu-central-1")

        # Invalid region format
        with pytest.raises(ConfigValidationError, match="must match pattern"):
            config_instance.validate_key_value("claude.bedrock.aws_region", "invalid")

    def test_reset_specific_key(self, config_instance):
        """Test resetting a specific key to default."""
        # Set a custom value
        config_instance.set("backup.retention_days", 60)
        assert config_instance.get("backup.retention_days") == 60

        # Reset to default
        config_instance.reset("backup.retention_days")
        assert config_instance.get("backup.retention_days") == 30

    def test_reset_all_config(self, config_instance):
        """Test resetting entire configuration."""
        # Set multiple values
        config_instance.set("claude.active_profile", "personal")
        config_instance.set("backup.retention_days", 60)

        # Reset all
        config_instance.reset()

        # Should return to defaults
        assert config_instance.get("claude.active_profile") == "bedrock"
        assert config_instance.get("backup.retention_days") == 30

        # Config file should be deleted
        assert not config_instance.user_config_file.exists()

    def test_atomic_save(self, config_instance):
        """Test that config save is atomic (uses temp file and rename)."""
        config_instance.set("backup.enabled", True)

        # Check that temp file doesn't exist after save
        temp_file = config_instance.user_config_file.with_suffix(".yaml.tmp")
        assert not temp_file.exists()

        # Config file should exist
        assert config_instance.user_config_file.exists()


class TestClaudeUtils:
    """Tests for Claude profile management utilities."""

    @pytest.fixture
    def mock_claude_dir(self, tmp_path):
        """Create a mock Claude directory with settings files."""
        claude_dir = tmp_path / ".claude"
        claude_dir.mkdir()

        # Create mock settings files
        bedrock_settings = {
            "awsAuthRefresh": "/path/to/credential-process",
            "env": {
                "AWS_PROFILE": "ClaudeCodeUnix",
                "AWS_REGION": "us-west-2",
                "CLAUDE_CODE_USE_BEDROCK": "1",
            },
        }

        personal_settings = {
            "enabledPlugins": {
                "feature-dev@claude-code-plugins": True,
            },
        }

        with open(claude_dir / "settings.bedrock.json", "w") as f:
            json.dump(bedrock_settings, f)

        with open(claude_dir / "settings.pro.json", "w") as f:
            json.dump(personal_settings, f)

        with open(claude_dir / "settings.json", "w") as f:
            json.dump(bedrock_settings, f)

        return claude_dir

    def test_get_profile_env_vars_bedrock(self):
        """Test getting environment variables for bedrock profile."""
        from dot.utils.claude import get_profile_env_vars

        env_vars = get_profile_env_vars("bedrock")

        assert env_vars["AWS_PROFILE"] == "ClaudeCodeUnix"
        assert env_vars["AWS_REGION"] == "us-west-2"
        assert env_vars["CLAUDE_CODE_USE_BEDROCK"] == "1"
        assert env_vars["CLAUDE_CODE_ENABLE_TELEMETRY"] == "1"
        assert "OTEL_EXPORTER_OTLP_ENDPOINT" in env_vars

    def test_get_profile_env_vars_personal(self):
        """Test getting environment variables for personal profile."""
        from dot.utils.claude import get_profile_env_vars

        env_vars = get_profile_env_vars("personal")

        # All should be None (unset)
        assert env_vars["AWS_PROFILE"] is None
        assert env_vars["AWS_REGION"] is None
        assert env_vars["CLAUDE_CODE_USE_BEDROCK"] is None
        assert env_vars["CLAUDE_CODE_ENABLE_TELEMETRY"] is None
        assert env_vars["OTEL_EXPORTER_OTLP_ENDPOINT"] is None

    def test_generate_shell_commands_bedrock(self):
        """Test generating shell commands for bedrock profile."""
        from dot.utils.claude import generate_shell_commands

        commands = generate_shell_commands("bedrock")

        assert 'export AWS_PROFILE="ClaudeCodeUnix"' in commands
        assert 'export AWS_REGION="us-west-2"' in commands
        assert 'export CLAUDE_CODE_USE_BEDROCK="1"' in commands

    def test_generate_shell_commands_personal(self):
        """Test generating shell commands for personal profile."""
        from dot.utils.claude import generate_shell_commands

        commands = generate_shell_commands("personal")

        assert "unset AWS_PROFILE" in commands
        assert "unset AWS_REGION" in commands
        assert "unset CLAUDE_CODE_USE_BEDROCK" in commands
        assert "export" not in commands

    def test_verify_settings_file(self, mock_claude_dir):
        """Test verifying settings file existence."""
        from dot.utils.claude import verify_settings_file

        with patch("dot.utils.claude.config_manager") as mock_config:
            mock_config.get.side_effect = lambda key: {
                "claude.bedrock.settings_file": str(mock_claude_dir / "settings.bedrock.json"),
                "claude.personal.settings_file": str(mock_claude_dir / "settings.pro.json"),
                "claude.missing.settings_file": str(mock_claude_dir / "missing.json"),
            }.get(key)

            assert verify_settings_file("bedrock") is True
            assert verify_settings_file("personal") is True
            assert verify_settings_file("missing") is False


class TestConfigCommand:
    """Integration tests for the config CLI command."""

    def test_config_list_command(self):
        """Test the config list command."""
        from click.testing import CliRunner
        from dot.commands.config import config

        runner = CliRunner()
        result = runner.invoke(config, ["list"])

        assert result.exit_code == 0
        assert "Configuration Settings" in result.output
        # Keys may be truncated in table output, just check for "claude"
        assert "claude" in result.output
        assert "backup" in result.output
        assert "Active Claude" in result.output
        assert "AWS CLI profile" in result.output

    def test_config_get_command(self):
        """Test the config get command."""
        from click.testing import CliRunner
        from dot.commands.config import config

        runner = CliRunner()
        result = runner.invoke(config, ["get", "claude.active_profile"])

        assert result.exit_code == 0
        assert "bedrock" in result.output.lower()

    def test_config_set_command(self):
        """Test the config set command."""
        from click.testing import CliRunner
        from dot.commands.config import config

        runner = CliRunner()
        result = runner.invoke(
            config, ["set", "backup.retention_days", "45", "--force"]
        )

        assert result.exit_code == 0
        assert "Set backup.retention_days = 45" in result.output

    def test_config_set_invalid_value(self):
        """Test config set with invalid value."""
        from click.testing import CliRunner
        from dot.commands.config import config

        runner = CliRunner()
        result = runner.invoke(
            config, ["set", "claude.active_profile", "invalid", "--force"]
        )

        assert result.exit_code == 0
        assert "Validation error" in result.output

    def test_config_claude_show_profile(self):
        """Test showing current Claude profile."""
        from click.testing import CliRunner
        from dot.commands.config import config

        runner = CliRunner()
        result = runner.invoke(config, ["claude"])

        assert result.exit_code == 0
        assert "Claude Profile" in result.output
        assert "Active profile" in result.output

    def test_config_env_command(self):
        """Test the env command."""
        from click.testing import CliRunner
        from dot.commands.config import config

        runner = CliRunner()
        result = runner.invoke(config, ["env", "bedrock"])

        assert result.exit_code == 0
        assert "export AWS_PROFILE" in result.output
        assert "export CLAUDE_CODE_USE_BEDROCK" in result.output

        result = runner.invoke(config, ["env", "personal"])

        assert result.exit_code == 0
        assert "unset AWS_PROFILE" in result.output
        assert "unset CLAUDE_CODE_USE_BEDROCK" in result.output


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
