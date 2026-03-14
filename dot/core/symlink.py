"""Symlink operations for dotfiles."""

import os
from pathlib import Path
from typing import Optional

from dot.core.backup import BackupManager


class SymlinkManager:
    """Manages symlink creation and verification."""

    def __init__(self, backup_manager: Optional[BackupManager] = None):
        """Initialize symlink manager.

        Args:
            backup_manager: Optional backup manager for creating backups.
        """
        self.backup_manager = backup_manager or BackupManager()

    def create_symlink(
        self, src: Path, dest: Path, backup: bool = True, force: bool = False
    ) -> bool:
        """Create a symlink from dest to src.

        Args:
            src: Source file path (target of the symlink).
            dest: Destination path (where the symlink will be created).
            backup: Whether to backup existing files.
            force: Whether to overwrite existing files without backup.

        Returns:
            True if symlink was created, False otherwise.
        """
        # Ensure source exists
        if not src.exists():
            raise FileNotFoundError(f"Source file does not exist: {src}")

        # Check if destination already exists
        if dest.exists() or dest.is_symlink():
            # Check if it's already our symlink
            if self.is_our_symlink(dest, src):
                return False  # Already linked correctly

            # Backup or remove existing file
            if backup and not force:
                self.backup_manager.create_backup(dest)

            # Remove existing file/symlink
            if dest.is_symlink():
                dest.unlink()
            elif dest.is_file():
                dest.unlink()
            elif dest.is_dir():
                # Don't automatically remove directories
                raise IsADirectoryError(
                    f"Destination is a directory: {dest}. Remove manually if needed."
                )

        # Create parent directory if it doesn't exist
        dest.parent.mkdir(parents=True, exist_ok=True)

        # Create the symlink
        os.symlink(src, dest)
        return True

    def verify_symlink(self, dest: Path, expected_src: Path) -> bool:
        """Verify that a symlink points to the expected source.

        Args:
            dest: Path to the symlink.
            expected_src: Expected source path.

        Returns:
            True if the symlink is correct, False otherwise.
        """
        if not dest.is_symlink():
            return False

        try:
            actual_src = dest.resolve()
            expected_src = expected_src.resolve()
            return actual_src == expected_src
        except (OSError, RuntimeError):
            return False

    def is_our_symlink(self, dest: Path, src: Path) -> bool:
        """Check if a path is a symlink pointing to our source.

        Args:
            dest: Path to check.
            src: Expected source path.

        Returns:
            True if dest is a symlink to src, False otherwise.
        """
        return self.verify_symlink(dest, src)

    def get_symlink_target(self, link_path: Path) -> Optional[Path]:
        """Get the target of a symlink.

        Args:
            link_path: Path to the symlink.

        Returns:
            Path to the symlink target, or None if not a symlink.
        """
        if not link_path.is_symlink():
            return None

        try:
            return link_path.resolve()
        except (OSError, RuntimeError):
            return None
