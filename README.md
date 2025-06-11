# Chris W Hendricks's dotfiles

My personal dotfiles for macOS and Linux development environments.

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

## Features

- Symlinks dotfiles into your home directory
- Creates local git configuration with your personal details
- Installs Homebrew and common development tools
- Sets up macOS-specific preferences when on macOS

## License

MIT