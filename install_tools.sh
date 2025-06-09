#!/bin/bash

# Chris W Hendricks's tools installer

set -e

echo "Installing essential tools for macOS development environment..."

# Check if Homebrew is installed
if ! command -v brew &> /dev/null; then
    echo "Installing Homebrew..."
    /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
else
    echo "Homebrew already installed, updating..."
    brew update
fi

# Install command line tools
echo "Installing command line tools..."
brew install \
    git \
    tmux \
    wget \
    curl \
    jq \
    htop \
    tree \
    ripgrep \
    fd \
    bat \
    fzf

# Install Oh My Zsh if not already installed
if [ ! -d "$HOME/.oh-my-zsh" ]; then
    echo "Installing Oh My Zsh..."
    sh -c "$(curl -fsSL https://raw.githubusercontent.com/ohmyzsh/ohmyzsh/master/tools/install.sh)" "" --unattended
else
    echo "Oh My Zsh already installed"
fi

# Install applications with Homebrew Cask
echo "Installing applications..."
brew install --cask \
    visual-studio-code \
    iterm2 \
    rectangle \
    alfred

# Install Nerd Fonts
echo "Installing Nerd Fonts..."
brew tap homebrew/cask-fonts
brew install --cask font-hack-nerd-font font-fira-code-nerd-font font-jetbrains-mono-nerd-font

echo "Tools installation complete!"