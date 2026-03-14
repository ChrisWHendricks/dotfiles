"""Filesystem utility functions."""

from pathlib import Path
from typing import List


def ensure_dir(path: Path) -> Path:
    """Ensure a directory exists, creating it if necessary.

    Args:
        path: Path to the directory.

    Returns:
        The path (for chaining).
    """
    path.mkdir(parents=True, exist_ok=True)
    return path


def expand_path(path_str: str) -> Path:
    """Expand a path string, handling ~ and environment variables.

    Args:
        path_str: Path string to expand.

    Returns:
        Expanded Path object.
    """
    return Path(path_str).expanduser().resolve()


def is_safe_to_remove(path: Path) -> bool:
    """Check if a path is safe to remove.

    This prevents accidental removal of important directories.

    Args:
        path: Path to check.

    Returns:
        True if safe to remove, False otherwise.
    """
    # List of paths that should never be removed
    dangerous_paths = [
        Path.home(),
        Path("/"),
        Path("/usr"),
        Path("/bin"),
        Path("/sbin"),
        Path("/etc"),
        Path("/var"),
        Path("/home"),
        Path("/root"),
    ]

    resolved_path = path.resolve()

    for dangerous in dangerous_paths:
        if resolved_path == dangerous.resolve():
            return False

    return True


def find_files(directory: Path, pattern: str = "*", recursive: bool = True) -> List[Path]:
    """Find files matching a pattern in a directory.

    Args:
        directory: Directory to search.
        pattern: Glob pattern to match.
        recursive: Whether to search recursively.

    Returns:
        List of matching file paths.
    """
    if not directory.exists():
        return []

    if recursive:
        return sorted(directory.rglob(pattern))
    else:
        return sorted(directory.glob(pattern))
