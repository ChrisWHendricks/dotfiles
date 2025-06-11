# Chris W Hendricks's dotfiles

My personal dotfiles for macOS and Linux development environments.

## Table of Contents
- [Installation](#installation)
- [Usage](#usage)
  - [Managing dotfiles](#managing-dotfiles)
  - [Dotfiles CLI](#dotfiles-can-also-be-used-as-a-command-line)
  - [Local customization](#local-customization)
- [What's included](#whats-included)
- [Features](#features)
- [Additional Documentation](#additional-documentation)
- [License](#license)

## Installation

```bash
git clone https://github.com/ChrisWHendricks/dotfiles.git ~/.dotfiles
cd ~/.dotfiles
./install.sh
```

## Usage

### Managing dotfiles

- **Install**: Run `./install.sh` to create symlinks for all dotfiles
- **Unlink**: Run `./unlink.sh` to remove all symlinks created by the installer
- **Edit**: Modify files directly in the `~/.dotfiles` directory, changes will be reflected in your home directory

### Dotfiles can also be used as a command line
After the initial install is completed, you can use dotfiles as a cli

```bash
$ dot -h
dot -- dotfiles management

Usage: dot [options]

Options:
  --bootstrap     Run the bootstrap script to set up dotfiles
  --homebrew      Install or update Homebrew
  --set-defaults  Set OS specific defaults
  --apps          Install/Update applications
  -e, --edit      Open dotfiles directory for editing
  -h, --help      Show this help message and exit

If no options are provided, usage information is displayed.
```

### Local customization

- Create `~/.zshrc.local` for machine-specific Zsh settings
- Create `~/.gitconfig.local` for personal Git configuration

## What's included

- Zsh configuration (.zshrc)
- Git configuration with useful aliases
- VS Code settings
- macOS preferences and Homebrew setup
- Cross-platform compatibility (macOS and Linux)
- Automatic backup of existing dotfiles
- [Terminal Setup Guide](./terminal_setup.md)

## Features

- Symlinks dotfiles into your home directory
- Creates local git configuration with your personal details
- Installs Homebrew and common development tools
- Sets up macOS-specific preferences when on macOS

## Additional Documentation
- [Shell Aliases](./Aliases.md)
- [Git Aliases](./GitAliases.md)

## License

MIT