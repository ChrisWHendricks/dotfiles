"""Shell command execution utilities."""

import subprocess
from typing import Optional, Tuple


def run_command(
    command: str,
    shell: bool = True,
    capture_output: bool = True,
    check: bool = False,
    cwd: Optional[str] = None,
) -> Tuple[int, str, str]:
    """Run a shell command and return the result.

    Args:
        command: Command to execute.
        shell: Whether to run through shell.
        capture_output: Whether to capture stdout/stderr.
        check: Whether to raise exception on non-zero exit.
        cwd: Working directory for the command.

    Returns:
        Tuple of (return_code, stdout, stderr).
    """
    try:
        result = subprocess.run(
            command,
            shell=shell,
            capture_output=capture_output,
            text=True,
            check=check,
            cwd=cwd,
        )
        return result.returncode, result.stdout, result.stderr
    except subprocess.CalledProcessError as e:
        return e.returncode, e.stdout, e.stderr


def command_exists(command: str) -> bool:
    """Check if a command exists in PATH.

    Args:
        command: Command name to check.

    Returns:
        True if command exists, False otherwise.
    """
    returncode, _, _ = run_command(f"command -v {command}", check=False)
    return returncode == 0


def get_command_version(command: str, version_flag: str = "--version") -> Optional[str]:
    """Get the version of a command.

    Args:
        command: Command name.
        version_flag: Flag to get version (default: --version).

    Returns:
        Version string or None if command not found.
    """
    if not command_exists(command):
        return None

    returncode, stdout, stderr = run_command(f"{command} {version_flag}", check=False)

    if returncode == 0:
        # Return first line of output (usually contains version)
        output = stdout.strip() or stderr.strip()
        return output.split("\n")[0] if output else None

    return None
