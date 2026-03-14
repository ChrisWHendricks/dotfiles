"""Install command for creating dotfiles symlinks."""

import click
import questionary

from dot.core.installer import DotfileInstaller
from dot.utils.output import (
    console,
    print_error,
    print_header,
    print_info,
    print_success,
    print_warning,
)


@click.command()
@click.option("--dry-run", is_flag=True, help="Show what would be done without making changes")
@click.option("--force", is_flag=True, help="Skip confirmation prompts")
@click.option("--no-backup", is_flag=True, help="Skip backing up existing files")
@click.option(
    "--link-in-src",
    is_flag=True,
    help="Also create convenience links in ~/src for easy editing",
)
def install(dry_run, force, no_backup, link_in_src):
    """Install dotfiles by creating symlinks.

    This command creates symlinks from your home directory to the dotfiles
    in this repository. Existing files are backed up by default.

    Examples:
        dot install              # Interactive installation
        dot install --dry-run    # Preview changes
        dot install --force      # Skip prompts
        dot install --link-in-src  # Also link in ~/src
    """
    print_header("Installing Dotfiles")

    # Confirmation prompt unless force or dry-run
    if not force and not dry_run:
        console.print(
            "\nThis will create symlinks for your dotfiles. Existing files will be backed up."
        )
        if not questionary.confirm("Continue?", default=True).ask():
            print_warning("Installation cancelled")
            return

    # Create installer
    installer = DotfileInstaller(
        dry_run=dry_run, force=force, no_backup=no_backup, link_in_src=link_in_src
    )

    # Show backup location if backups will be created
    if not no_backup and not dry_run:
        backup_dir = installer.backup_manager.get_backup_location()
        print_info(f"Backups will be saved to: {backup_dir}")

    # Install dotfiles
    console.print()
    if dry_run:
        print_info("DRY RUN - No changes will be made\n")

    results = installer.install_all()

    # Display results
    console.print()
    print_header("Results")

    if results["created"]:
        console.print(f"\n[green]Created {len(results['created'])} symlink(s):[/green]")
        for path in results["created"]:
            print_success(f"{path.name} → {path}")

    if results["skipped"]:
        console.print(f"\n[yellow]Skipped {len(results['skipped'])} (already linked):[/yellow]")
        for path in results["skipped"]:
            print_info(f"{path.name}")

    if results["failed"]:
        console.print(f"\n[red]Failed {len(results['failed'])} symlink(s):[/red]")
        for path in results["failed"]:
            print_error(f"{path.name}")

    # Show backup location if backups were created
    backup_location = installer.get_backup_location()
    if backup_location and not dry_run:
        console.print()
        print_info(f"Backups saved to: {backup_location}")

    # Summary
    console.print()
    if not results["failed"]:
        if dry_run:
            print_success(
                "Dry run complete! Run without --dry-run to apply these changes."
            )
        else:
            print_success("Installation complete!")
            console.print("\n[dim]Run 'dot check' to verify the installation.[/dim]")
    else:
        print_warning("Installation completed with some errors")
        console.print("\n[dim]Check the errors above and try again.[/dim]")
