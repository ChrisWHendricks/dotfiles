"""Backup management for dotfiles."""

import shutil
from datetime import datetime
from pathlib import Path
from typing import List

from dot.core.config import config


class BackupManager:
    """Manages backup operations for dotfiles."""

    def __init__(self):
        """Initialize backup manager."""
        self.timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        self.backup_dir = config.backup_dir / self.timestamp
        self.backed_up_files: List[Path] = []

    def create_backup(self, file_path: Path) -> Path:
        """Create a backup of a file.

        Args:
            file_path: Path to the file to backup.

        Returns:
            Path to the backed up file.
        """
        if not file_path.exists():
            return None

        # Create backup directory if it doesn't exist
        self.backup_dir.mkdir(parents=True, exist_ok=True)

        # Preserve relative path structure in backup
        backup_path = self.backup_dir / file_path.name

        # Handle existing backup file
        if backup_path.exists():
            # Add a counter to avoid overwriting
            counter = 1
            while backup_path.exists():
                backup_path = self.backup_dir / f"{file_path.stem}_{counter}{file_path.suffix}"
                counter += 1

        # Copy the file (not move, so we preserve the original)
        if file_path.is_symlink():
            # For symlinks, save the link target
            link_target = file_path.resolve()
            with open(backup_path.with_suffix(".link_info"), "w") as f:
                f.write(f"Symlink to: {link_target}\n")
        else:
            shutil.copy2(file_path, backup_path)

        self.backed_up_files.append(file_path)
        return backup_path

    def has_backups(self) -> bool:
        """Check if any files were backed up.

        Returns:
            True if backups were created, False otherwise.
        """
        return len(self.backed_up_files) > 0

    def get_backup_location(self) -> Path:
        """Get the current backup directory path.

        Returns:
            Path to the backup directory.
        """
        return self.backup_dir
