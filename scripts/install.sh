#!/bin/bash

# Chris W Hendricks's dotfiles installer
# DEPRECATED: This script is deprecated. Please use the new 'dot' CLI instead.
# See README.md for installation instructions.

echo "⚠️  WARNING: This script is deprecated!"
echo "   Please use the new 'dot' CLI instead:"
echo ""
echo "   pip install -e ."
echo "   dot install"
echo ""
echo "   See README.md for more information."
echo ""
read -p "Continue with legacy installer anyway? (y/N) " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    exit 0
fi

set -e

DOTFILES_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)/.."
BACKUP_DIR="$HOME/.dotfiles_backup/$(date +%Y%m%d%H%M%S)"

# Create backup directory
mkdir -p "$BACKUP_DIR"

# Function to backup and link files
link_file() {
    local src="$1"
    local dest="$2"
    
    # Backup existing file if it exists and is not a symlink to our dotfiles
    if [ -e "$dest" ] && [ ! -L "$dest" -o "$(readlink "$dest")" != "$src" ]; then
        echo "Backing up $dest to $BACKUP_DIR/$(basename "$dest")"
        mv "$dest" "$BACKUP_DIR/$(basename "$dest")"
    fi
    
    # Create symlink
    if [ ! -e "$dest" ]; then
        echo "Linking $src to $dest"
        ln -sf "$src" "$dest"
    else
        echo "$dest already linked correctly"
    fi
}

# Link dotfiles to home directory
link_file "$DOTFILES_DIR/config/shell/.zshrc" "$HOME/.zshrc"
link_file "$DOTFILES_DIR/config/shell/.bashrc" "$HOME/.bashrc"
link_file "$DOTFILES_DIR/config/shell/.bash_profile" "$HOME/.bash_profile"
link_file "$DOTFILES_DIR/config/git/.gitconfig" "$HOME/.gitconfig"
link_file "$DOTFILES_DIR/config/git/.gitignore_global" "$HOME/.gitignore_global"
link_file "$DOTFILES_DIR/config/tmux/.tmux.conf" "$HOME/.tmux.conf"

# Create src directory if it doesn't exist
SRC_DIR="$HOME/src"
mkdir -p "$SRC_DIR"

# Link dotfiles to src directory for easy editing
echo "Creating links in ~/src for easy editing..."
link_file "$DOTFILES_DIR/config/shell/.zshrc" "$SRC_DIR/.zshrc"
link_file "$DOTFILES_DIR/config/shell/.bashrc" "$SRC_DIR/.bashrc"
link_file "$DOTFILES_DIR/config/shell/.bash_profile" "$SRC_DIR/.bash_profile"
link_file "$DOTFILES_DIR/config/git/.gitconfig" "$SRC_DIR/.gitconfig"
link_file "$DOTFILES_DIR/config/git/.gitignore_global" "$SRC_DIR/.gitignore_global"
link_file "$DOTFILES_DIR/config/tmux/.tmux.conf" "$SRC_DIR/.tmux.conf"

# Link VS Code settings if VS Code is installed
VSCODE_DIR="$HOME/Library/Application Support/Code/User"
if [ -d "$VSCODE_DIR" ]; then
    echo "Linking VS Code settings"
    mkdir -p "$VSCODE_DIR"
    link_file "$DOTFILES_DIR/config/vscode/settings.json" "$VSCODE_DIR/settings.json"
fi

echo "Dotfiles installation complete!"
echo "If you want to install additional tools, run: ./install_tools.sh"