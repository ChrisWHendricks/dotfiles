#!/bin/bash
#
# Homebrew
#
# This installs some of the common dependencies needed (or at least desired)
# using Homebrew.

# Check for Homebrew
if test ! $(which brew)
then
  echo "  Installing Homebrew for you."

  # Install the correct homebrew for each OS type
  if test "$(uname)" = "Darwin"
  then
  # hide output of the install command
    export HOMEBREW_NO_AUTO_UPDATE=1
    /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)" > /dev/null
  elif test "$(expr substr $(uname -s) 1 5)" = "Linux"
  then
    # Handle the glibc warning by setting HOMEBREW_NO_AUTO_UPDATE
    export HOMEBREW_NO_AUTO_UPDATE=1
    /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)" > /dev/null
    
    # Add Homebrew to PATH for Linux
    test -d ~/.linuxbrew && eval "$(~/.linuxbrew/bin/brew shellenv)"
    test -d /home/linuxbrew/.linuxbrew && eval "$(/home/linuxbrew/.linuxbrew/bin/brew shellenv)"
    
    # Add to shell profile
    eval "$(/home/linuxbrew/.linuxbrew/bin/brew shellenv)"
    
    if [ -f ~/.zshrc ]; then
      echo 'eval "$(/home/linuxbrew/.linuxbrew/bin/brew shellenv)"' >> ~/.zshrc
    fi
    if [ -f ~/.bashrc ]; then
      echo 'eval "$(/home/linuxbrew/.linuxbrew/bin/brew shellenv)"' >> ~/.bashrc
    fi
  fi
fi

# Install from appropriate Brewfile based on OS
# if test "$(uname)" = "Darwin"
# then
#   echo "  Installing macOS dependencies from Brewfile"
#   brew bundle --file=$HOME/.dotfiles/macos/Brewfile
# elif test "$(expr substr $(uname -s) 1 5)" = "Linux"
# then
#   echo "  Installing Linux dependencies from Brewfile"
#   brew bundle --file=$HOME/.dotfiles/linux/Brewfile
# fi

exit 0