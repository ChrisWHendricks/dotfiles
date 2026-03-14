# Chris W Hendricks's Dotfiles

Modern CLI tool for managing personal dotfiles and development environment on macOS and Linux.

## Quick Start

### Brand New Machine (Bootstrap)

If you're setting up a brand new machine without Python or other prerequisites:

```bash
# Clone the repository
git clone https://github.com/ChrisWHendricks/dotfiles.git ~/src/dotfiles
cd ~/src/dotfiles

# Run bootstrap script (installs Homebrew, Python, Git, sets up venv)
./bootstrap.sh

# Install dotfiles
dot install

# Verify installation
dot check
```

The bootstrap script will automatically:
- Install Homebrew (macOS) or update apt (Linux)
- Install Git if not present
- Install Python 3.9+ if not present or too old
- Create and configure a virtual environment
- Install the `dot` CLI tool
- Add the CLI to your PATH

### Existing Machine (Manual Setup)

If you already have Python 3.9+ installed:

```bash
# Clone the repository
git clone https://github.com/ChrisWHendricks/dotfiles.git ~/src/dotfiles
cd ~/src/dotfiles

# Install Python dependencies and the CLI tool
python3 -m venv venv
source venv/bin/activate
pip install -e .

# Install dotfiles
dot install

# Verify installation
dot check
```

## Features

- **Modern CLI**: Built with Python and Click framework
- **Smart Symlinks**: Automatic backup and linking of dotfiles
- **Tool Management**: Install and update development tools
- **Cross-Platform**: macOS primary, Linux secondary support
- **Safe Operations**: Dry-run mode and automatic backups

## Commands

### `dot install`
Install dotfiles by creating symlinks to your home directory.

```bash
dot install                    # Interactive installation
dot install --dry-run          # Preview changes
dot install --force            # Skip prompts
dot install --no-backup        # Skip backups (not recommended)
dot install --link-in-src      # Also create links in ~/src
```

### `dot check`
Verify dotfiles installation and system configuration.

```bash
dot check                      # Check everything
```

Shows:
- Dotfiles repository location
- Python version and platform
- Symlink status
- Installed tools

### `dot tools`
Manage development tools and applications.

```bash
dot tools list                 # List all available tools
dot tools list --installed     # Show only installed tools
dot tools list --category cli_tools  # Filter by category

dot tools install git tmux     # Install specific tools
dot tools install --all        # Install all recommended tools
dot tools install --category essential  # Install by category
dot tools install --dry-run    # Preview installations

dot tools update               # Update all installed tools
```

Available categories:
- `essential` - Core development tools
- `cli_tools` - Command-line utilities
- `shell` - Shell enhancements
- `applications` - GUI applications
- `fonts` - Developer fonts

## What's Included

### Shell Configuration
- Zsh configuration (`.zshrc`)
- Bash configuration (`.bashrc`, `.bash_profile`)
- Shell aliases and functions

### Development Tools
- Git configuration (`.gitconfig`)
- Tmux configuration (`.tmux.conf`)
- VS Code settings

### Recommended Tools
- **Essential**: git, tmux, wget, curl
- **CLI Tools**: fzf, ripgrep, bat, jq, htop, tree
- **Applications**: VS Code, iTerm2, Rectangle, Alfred
- **Fonts**: Hack, Fira Code, JetBrains Mono Nerd Fonts

## Directory Structure

```
dotfiles/
├── dot/                      # Python package
│   ├── commands/            # CLI commands
│   ├── core/                # Core functionality
│   ├── utils/               # Utilities
│   └── data/                # Configuration files
├── config/                   # Dotfiles organized by type
│   ├── shell/               # Shell configurations
│   ├── git/                 # Git configurations
│   ├── tmux/                # Tmux configuration
│   └── vscode/              # VS Code settings
├── scripts/                  # Legacy install scripts
└── tests/                    # Test suite
```

## Development

```bash
# Install in development mode
pip install -e ".[dev]"

# Run tests
pytest

# Format code
black dot/

# Lint code
flake8 dot/
```

## Migration from Legacy Scripts

If you were using the old `install.sh` and `install_tools.sh` scripts, they are still available in the `scripts/` directory but are deprecated. The new `dot` CLI provides a better experience:

| Old Command | New Command |
|-------------|-------------|
| `./install.sh` | `dot install` |
| `./install_tools.sh` | `dot tools install --all` |
| Manual symlink verification | `dot check` |

## Backup

All existing files are automatically backed up before being replaced with symlinks. Backups are stored in `~/.dotfiles_backup/YYYYMMDDHHMMSS/`.

## Platform Support

- **macOS** (primary): Full support with Homebrew
- **Linux** (secondary): Support for apt-based distributions
- **Windows**: Not currently supported

## Requirements

- Python 3.9+
- macOS 10.15+ or Linux
- Homebrew (macOS) or apt (Linux)

## License

MIT