"""Configuration management for dotfiles."""

import os
import re
from pathlib import Path
from typing import Any, Dict, Optional, Union

import yaml

from dot.core.platform import get_config_dir, get_home_dir


# Default configuration schema
DEFAULT_CONFIG = {
    "claude": {
        "active_profile": "bedrock",
        "bedrock": {
            "aws_profile": "ClaudeCodeUnix",
            "aws_region": "us-west-2",
            "settings_file": "~/.claude/settings.bedrock.json",
        },
        "personal": {
            "settings_file": "~/.claude/settings.pro.json",
        },
    },
    "backup": {
        "enabled": True,
        "retention_days": 30,
    },
    "symlink": {
        "create_in_src": False,
    },
    "tools": {
        "auto_update": False,
    },
}


# Validation rules for configuration keys
VALIDATION_RULES = {
    "claude.active_profile": {
        "type": str,
        "allowed_values": ["bedrock", "personal"],
        "description": "Active Claude profile",
    },
    "claude.bedrock.aws_profile": {
        "type": str,
        "description": "AWS CLI profile for Bedrock",
    },
    "claude.bedrock.aws_region": {
        "type": str,
        "pattern": r"^[a-z]{2}-[a-z]+-\d+$",
        "description": "AWS region for Bedrock",
    },
    "claude.bedrock.settings_file": {
        "type": str,
        "description": "Path to Bedrock settings file",
    },
    "claude.personal.settings_file": {
        "type": str,
        "description": "Path to personal settings file",
    },
    "backup.enabled": {
        "type": bool,
        "description": "Enable automatic backups",
    },
    "backup.retention_days": {
        "type": int,
        "min": 1,
        "max": 365,
        "description": "Days to retain backups",
    },
    "symlink.create_in_src": {
        "type": bool,
        "description": "Create convenience symlinks in ~/src",
    },
    "tools.auto_update": {
        "type": bool,
        "description": "Automatically update tools",
    },
}


class ConfigValidationError(Exception):
    """Raised when configuration validation fails."""

    pass


class Config:
    """Configuration manager for dotfiles."""

    def __init__(self):
        """Initialize configuration manager."""
        self._config: Optional[Dict[str, Any]] = None
        self._dotfiles_root: Optional[Path] = None

    @property
    def dotfiles_root(self) -> Path:
        """Get the dotfiles repository root directory.

        Returns:
            Path to the dotfiles repository.
        """
        if self._dotfiles_root is None:
            # Try environment variable first
            env_root = os.environ.get("DOTFILES_ROOT")
            if env_root:
                self._dotfiles_root = Path(env_root).resolve()
            else:
                # Default to the directory containing the dot package
                # This assumes the package is installed from the dotfiles repo
                package_dir = Path(__file__).parent.parent
                self._dotfiles_root = package_dir.parent.resolve()

        return self._dotfiles_root

    @property
    def backup_dir(self) -> Path:
        """Get the backup directory for dotfiles.

        Returns:
            Path to the backup directory.
        """
        backup_root = get_home_dir() / ".dotfiles_backup"
        backup_root.mkdir(parents=True, exist_ok=True)
        return backup_root

    @property
    def user_config_file(self) -> Path:
        """Get the user's custom configuration file path.

        Returns:
            Path to the user's config.yaml file.
        """
        config_dir = get_config_dir() / "dotfiles"
        config_dir.mkdir(parents=True, exist_ok=True)
        return config_dir / "config.yaml"

    def load_user_config(self) -> Dict[str, Any]:
        """Load user configuration from config.yaml.

        Returns:
            Dictionary containing user configuration, or empty dict if not found.
        """
        if self._config is None:
            if self.user_config_file.exists():
                with open(self.user_config_file, "r") as f:
                    self._config = yaml.safe_load(f) or {}
            else:
                self._config = {}

        return self._config

    def get(self, key: str, default: Any = None) -> Any:
        """Get a configuration value.

        Args:
            key: Configuration key (supports dot notation, e.g., 'backup.enabled').
            default: Default value if key is not found.

        Returns:
            Configuration value or default.
        """
        config = self.load_user_config()

        # Support dot notation (e.g., 'backup.enabled')
        keys = key.split(".")
        value = config
        for k in keys:
            if isinstance(value, dict):
                value = value.get(k)
            else:
                break

        # If value is not in user config, fall back to defaults
        if value is None:
            value = self.get_default(key)

        # If still None, use provided default
        return value if value is not None else default

    def get_default(self, key: str) -> Any:
        """Get the default value for a configuration key.

        Args:
            key: Configuration key (supports dot notation).

        Returns:
            Default value or None if key doesn't exist in defaults.
        """
        keys = key.split(".")
        value = DEFAULT_CONFIG
        for k in keys:
            if isinstance(value, dict):
                value = value.get(k)
            else:
                return None

        return value

    def set(self, key: str, value: Any) -> None:
        """Set a configuration value.

        Args:
            key: Configuration key (supports dot notation).
            value: Value to set.

        Raises:
            ConfigValidationError: If key or value is invalid.
        """
        # Validate the key and value
        self.validate_key_value(key, value)

        # Load current config
        config = self.load_user_config()

        # Navigate to the parent dict and set the value
        keys = key.split(".")
        current = config

        # Create nested dicts as needed
        for k in keys[:-1]:
            if k not in current:
                current[k] = {}
            elif not isinstance(current[k], dict):
                raise ConfigValidationError(f"Cannot set {key}: parent path is not a dictionary")
            current = current[k]

        # Set the final value
        current[keys[-1]] = value

        # Clear cache and save
        self._config = config
        self.save_config()

    def validate_key_value(self, key: str, value: Any) -> None:
        """Validate a configuration key and value.

        Args:
            key: Configuration key.
            value: Value to validate.

        Raises:
            ConfigValidationError: If validation fails.
        """
        if key not in VALIDATION_RULES:
            raise ConfigValidationError(f"Unknown configuration key: {key}")

        rule = VALIDATION_RULES[key]

        # Type validation
        expected_type = rule.get("type")
        if expected_type and not isinstance(value, expected_type):
            raise ConfigValidationError(
                f"Invalid type for {key}: expected {expected_type.__name__}, got {type(value).__name__}"
            )

        # Allowed values validation
        allowed_values = rule.get("allowed_values")
        if allowed_values and value not in allowed_values:
            raise ConfigValidationError(
                f"Invalid value for {key}: must be one of {allowed_values}"
            )

        # Pattern validation for strings
        pattern = rule.get("pattern")
        if pattern and isinstance(value, str):
            if not re.match(pattern, value):
                raise ConfigValidationError(
                    f"Invalid format for {key}: must match pattern {pattern}"
                )

        # Range validation for integers
        if isinstance(value, int):
            min_val = rule.get("min")
            max_val = rule.get("max")
            if min_val is not None and value < min_val:
                raise ConfigValidationError(f"Value for {key} must be >= {min_val}")
            if max_val is not None and value > max_val:
                raise ConfigValidationError(f"Value for {key} must be <= {max_val}")

    def save_config(self) -> None:
        """Save the current configuration to disk.

        The config file is created with 0o600 permissions (owner read/write only).
        """
        config = self._config or {}

        # Ensure config directory exists
        self.user_config_file.parent.mkdir(parents=True, exist_ok=True)

        # Write to a temporary file first, then rename (atomic operation)
        temp_file = self.user_config_file.with_suffix(".yaml.tmp")
        try:
            with open(temp_file, "w") as f:
                yaml.safe_dump(config, f, default_flow_style=False, sort_keys=False)

            # Set permissions to 0o600
            temp_file.chmod(0o600)

            # Atomic rename
            temp_file.rename(self.user_config_file)
        except Exception:
            # Clean up temp file if something went wrong
            if temp_file.exists():
                temp_file.unlink()
            raise

    def reset(self, key: Optional[str] = None) -> None:
        """Reset configuration to defaults.

        Args:
            key: Specific key to reset, or None to reset entire config.
        """
        if key is None:
            # Reset entire config
            self._config = {}
            if self.user_config_file.exists():
                self.user_config_file.unlink()
        else:
            # Reset specific key to default value
            default_value = self.get_default(key)
            if default_value is not None:
                self.set(key, default_value)
            else:
                # If no default exists, remove the key
                config = self.load_user_config()
                keys = key.split(".")
                current = config

                # Navigate to parent
                for k in keys[:-1]:
                    if k not in current or not isinstance(current[k], dict):
                        return  # Key doesn't exist, nothing to reset
                    current = current[k]

                # Remove the key
                if keys[-1] in current:
                    del current[keys[-1]]
                    self._config = config
                    self.save_config()

    def load_data_file(self, filename: str) -> Dict[str, Any]:
        """Load a YAML file from the data directory.

        Args:
            filename: Name of the YAML file to load.

        Returns:
            Dictionary containing the file contents.

        Raises:
            FileNotFoundError: If the file doesn't exist.
        """
        data_dir = self.dotfiles_root / "dot" / "data"
        file_path = data_dir / filename

        if not file_path.exists():
            raise FileNotFoundError(f"Data file not found: {file_path}")

        with open(file_path, "r") as f:
            return yaml.safe_load(f) or {}


# Global config instance
config = Config()
