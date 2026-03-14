"""Rich console output utilities."""

from typing import List, Optional

from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.text import Text

# Global console instance
console = Console()


def print_success(message: str):
    """Print a success message in green."""
    console.print(f"[green]✓[/green] {message}")


def print_error(message: str):
    """Print an error message in red."""
    console.print(f"[red]✗[/red] {message}")


def print_warning(message: str):
    """Print a warning message in yellow."""
    console.print(f"[yellow]⚠[/yellow] {message}")


def print_info(message: str):
    """Print an info message in blue."""
    console.print(f"[blue]ℹ[/blue] {message}")


def print_header(title: str):
    """Print a section header."""
    console.print(f"\n[bold cyan]{title}[/bold cyan]")


def print_panel(title: str, content: str, style: str = "blue"):
    """Print content in a panel.

    Args:
        title: Panel title.
        content: Panel content.
        style: Panel border style/color.
    """
    panel = Panel(content, title=title, border_style=style)
    console.print(panel)


def create_table(
    title: Optional[str] = None, columns: Optional[List[str]] = None, show_header: bool = True
) -> Table:
    """Create a Rich table.

    Args:
        title: Optional table title.
        columns: List of column names.
        show_header: Whether to show the header row.

    Returns:
        Rich Table object.
    """
    table = Table(title=title, show_header=show_header)

    if columns:
        for col in columns:
            table.add_column(col)

    return table


def print_table(table: Table):
    """Print a Rich table.

    Args:
        table: Rich Table object to print.
    """
    console.print(table)


def print_status(message: str, status: str = "working"):
    """Print a status message with spinner.

    Args:
        message: Status message.
        status: Status type (working, success, error).
    """
    if status == "working":
        console.print(f"[cyan]⋯[/cyan] {message}")
    elif status == "success":
        print_success(message)
    elif status == "error":
        print_error(message)
    else:
        console.print(message)
