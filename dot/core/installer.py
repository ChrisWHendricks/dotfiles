"""Installation logic for dotfiles."""

from pathlib import Path
from typing import Dict, List, Optional

from dot.core.backup import BackupManager
from dot.core.config import config
from dot.core.platform import detect_platform, is_vscode_installed
from dot.core.symlink import SymlinkManager


class DotfileInstaller:
    """Handles installation of dotfiles."""

    def __init__(
        self,
        dry_run: bool = False,
        force: bool = False,
        no_backup: bool = False,
        link_in_src: bool = False,
    ):
        """Initialize the installer.

        Args:
            dry_run: If True, only show what would be done.
            force: If True, skip confirmation prompts.
            no_backup: If True, skip backing up existing files.
            link_in_src: If True, also create convenience links in ~/src.
        """
        self.dry_run = dry_run
        self.force = force
        self.no_backup = no_backup
        self.link_in_src = link_in_src
        self.backup_manager = BackupManager()
        self.symlink_manager = SymlinkManager(self.backup_manager)
        self.results: Dict[str, List[Path]] = {
            "created": [],
            "skipped": [],
            "failed": [],
        }

    def load_dotfiles_map(self) -> List[Dict]:
        """Load the dotfiles mapping configuration.

        Returns:
            List of dotfile configurations.
        """
        try:
            dotfiles_data = config.load_data_file("dotfiles_map.yaml")
            return dotfiles_data.get("dotfiles", [])
        except FileNotFoundError:
            return []

    def should_install(self, item: Dict) -> bool:
        """Check if a dotfile should be installed based on platform and conditions.

        Args:
            item: Dotfile configuration dictionary.

        Returns:
            True if the dotfile should be installed, False otherwise.
        """
        # Check platform
        platforms = item.get("platforms", [])
        current_platform = detect_platform()
        if platforms and current_platform.value not in platforms:
            return False

        # Check conditions
        condition = item.get("condition")
        if condition == "vscode_installed":
            return is_vscode_installed()

        return True

    def install_dotfile(self, item: Dict) -> bool:
        """Install a single dotfile.

        Args:
            item: Dotfile configuration dictionary.

        Returns:
            True if installation was successful, False otherwise.
        """
        src_rel = item.get("source")
        dest_str = item.get("destination")

        if not src_rel or not dest_str:
            return False

        src = config.dotfiles_root / src_rel
        dest = Path(dest_str).expanduser()

        # Check if source exists
        if not src.exists():
            self.results["failed"].append(dest)
            return False

        # Check if already linked correctly
        if self.symlink_manager.is_our_symlink(dest, src):
            self.results["skipped"].append(dest)
            return True

        # Dry run mode
        if self.dry_run:
            self.results["created"].append(dest)
            return True

        # Create the symlink
        try:
            created = self.symlink_manager.create_symlink(
                src, dest, backup=not self.no_backup, force=self.force
            )
            if created:
                self.results["created"].append(dest)
            else:
                self.results["skipped"].append(dest)
            return True
        except Exception as e:
            self.results["failed"].append(dest)
            return False

    def install_src_links(self) -> int:
        """Create convenience links in ~/src for easy editing.

        Returns:
            Number of links created.
        """
        if not self.link_in_src:
            return 0

        src_dir = Path.home() / "src"
        src_dir.mkdir(parents=True, exist_ok=True)

        dotfiles_map = self.load_dotfiles_map()
        links_created = 0

        for item in dotfiles_map:
            if not self.should_install(item):
                continue

            src_rel = item.get("source")
            src = config.dotfiles_root / src_rel
            dest = src_dir / src.name

            if not src.exists():
                continue

            # Skip if already linked
            if self.symlink_manager.is_our_symlink(dest, src):
                continue

            if self.dry_run:
                links_created += 1
                continue

            try:
                self.symlink_manager.create_symlink(
                    src, dest, backup=not self.no_backup, force=self.force
                )
                links_created += 1
            except Exception:
                pass

        return links_created

    def install_all(self) -> Dict[str, List[Path]]:
        """Install all dotfiles.

        Returns:
            Dictionary with lists of created, skipped, and failed paths.
        """
        dotfiles_map = self.load_dotfiles_map()

        for item in dotfiles_map:
            if not self.should_install(item):
                continue

            self.install_dotfile(item)

        # Create src links if requested
        if self.link_in_src:
            self.install_src_links()

        return self.results

    def get_backup_location(self) -> Optional[Path]:
        """Get the backup directory location if backups were created.

        Returns:
            Path to backup directory, or None if no backups were created.
        """
        if self.backup_manager.has_backups():
            return self.backup_manager.get_backup_location()
        return None
