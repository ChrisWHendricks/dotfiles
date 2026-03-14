"""Main CLI application using Click framework."""

import click
from dot import __version__
from dot.commands import check, install, tools


@click.group()
@click.version_option(version=__version__, prog_name="dot")
@click.pass_context
def cli(ctx):
    """Modern CLI tool for managing dotfiles configuration.

    Use 'dot <command> --help' for more information on a specific command.
    """
    ctx.ensure_object(dict)


# Register commands
cli.add_command(check.check)
cli.add_command(install.install)
cli.add_command(tools.tools)


if __name__ == "__main__":
    cli()
