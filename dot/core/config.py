"""Configuration management for dotfiles."""

import os
from pathlib import Path
from typing import Any, Dict, Optional

import yaml

from dot.core.platform import get_config_dir, get_home_dir


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
                return default

        return value if value is not None else default

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
