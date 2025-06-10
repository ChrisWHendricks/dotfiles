#!/bin/bash

# Chris W Hendricks's dotfiles installer

set -e

DOTFILES_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
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
link_file "$DOTFILES_DIR/.zshrc" "$HOME/.zshrc"
link_file "$DOTFILES_DIR/.bashrc" "$HOME/.bashrc"
link_file "$DOTFILES_DIR/.bash_profile" "$HOME/.bash_profile"
link_file "$DOTFILES_DIR/.gitconfig" "$HOME/.gitconfig"
link_file "$DOTFILES_DIR/.gitignore_global" "$HOME/.gitignore_global"
link_file "$DOTFILES_DIR/.tmux.conf" "$HOME/.tmux.conf"

# Create src directory if it doesn't exist
SRC_DIR="$HOME/src"
mkdir -p "$SRC_DIR"

# Link dotfiles to src directory for easy editing
echo "Creating links in ~/src for easy editing..."
link_file "$DOTFILES_DIR/.zshrc" "$SRC_DIR/.zshrc"
link_file "$DOTFILES_DIR/.bashrc" "$SRC_DIR/.bashrc"
link_file "$DOTFILES_DIR/.bash_profile" "$SRC_DIR/.bash_profile"
link_file "$DOTFILES_DIR/.gitconfig" "$SRC_DIR/.gitconfig"
link_file "$DOTFILES_DIR/.gitignore_global" "$SRC_DIR/.gitignore_global"
link_file "$DOTFILES_DIR/.tmux.conf" "$SRC_DIR/.tmux.conf"

# Link VS Code settings if VS Code is installed
VSCODE_DIR="$HOME/Library/Application Support/Code/User"
if [ -d "$VSCODE_DIR" ]; then
    echo "Linking VS Code settings"
    mkdir -p "$VSCODE_DIR"
    link_file "$DOTFILES_DIR/vscode/settings.json" "$VSCODE_DIR/settings.json"
fi

echo "Installing Dev Tools"
./install_tools.sh

echo "Dotfiles installation complete!"
