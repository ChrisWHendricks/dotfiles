#!/bin/bash

# Chris W Hendricks's dotfiles unlinker

set -e

DOTFILES_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Function to unlink a file
unlink_file() {
    local dest="$1"
    
    if [ -L "$dest" ]; then
        echo "Unlinking $dest"
        rm "$dest"
        echo "✓ Removed symlink: $dest"
    elif [ -e "$dest" ]; then
        echo "✗ $dest exists but is not a symlink"
    else
        echo "! $dest does not exist"
    fi
}

# Unlink dotfiles from home directory
unlink_file "$HOME/.zshrc"
unlink_file "$HOME/.bashrc"
unlink_file "$HOME/.bash_profile"
unlink_file "$HOME/.gitconfig"
unlink_file "$HOME/.gitignore_global"
unlink_file "$HOME/.tmux.conf"

# Unlink dotfiles from src directory
unlink_file "$HOME/src/.zshrc"
unlink_file "$HOME/src/.bashrc"
unlink_file "$HOME/src/.bash_profile"
unlink_file "$HOME/src/.gitconfig"
unlink_file "$HOME/src/.gitignore_global"
unlink_file "$HOME/src/.tmux.conf"

# Unlink VS Code settings if VS Code is installed
VSCODE_DIR="$HOME/Library/Application Support/Code/User"
if [ -d "$VSCODE_DIR" ]; then
    unlink_file "$VSCODE_DIR/settings.json"
fi

echo "Dotfiles unlink complete!"