#!/bin/sh
#
# Homebrew
#
# This installs some of the common dependencies needed (or at least desired)
# using Homebrew.

install_apps=$1 

  if [[ x"$OS" == x"Windows" ]]; then
    echo "Windows not currently supported, because I don't use windows very often.  Linux > Mac > Windows. (a.k.a Windows Sucks)"
    exit 0
  fi

# Check for Homebrew
if test ! $(which brew)
then
  echo "  Installing Homebrew for you."

  # Install the correct homebrew for each OS type
  if test "$(uname)" = "Darwin"
  then
    ruby -e "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/master/install)"
  elif test "$(expr substr $(uname -s) 1 5)" = "Linux"
  then
    ruby -e "$(curl -fsSL https://raw.githubusercontent.com/Linuxbrew/install/master/install)"
  fi
fi

function install() {
  app=$1
  cask=${2:-}

cat << EOF

-> Installing ${app}...
EOF

  if [[ x"$OS" == x"Windows" ]]; then
    scoop install ${app}
  else
    if [[ ! "$cask" ]]; then
      brew list ${app} >/dev/null || brew install ${app}
    else
      brew list ${app} --cask >/dev/null || brew install ${app} --cask
    fi
  fi

cat << EOF

-> ${app} installed
EOF
}

# Always Install Nerd Fonts
info "Installing Nerd Fonts..."
brew install --cask font-hack-nerd-font font-fira-code-nerd-font font-jetbrains-mono-nerd-font


# if not install-apps then exit
if [[ x"$install_apps" != x"yes" ]]; then
  echo "install-apps is not set to yes, skipping..."
  exit 0
fi

info "Installing Homebrew apps..."
install gh
install go
install iterm2 yes
install zsh
install ngrok yes
install visual-studio-code yes
#install slack yes
install google-chrome yes
install github-desktop yes
install OneDrive yes
install powershell yes
install google-drive yes
install postman yes
install nvm
install openssl
install readline
install sqlite3 
install zlib
install ruby-install
install rbenv
install xz
install rectangle yes
install alfred yes

# Install Rust
# Not using Rust right now so not installing
# if test ! $(which rustup)
# then
#   curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh
# fi

# You may need to run these commands for ruby-installer to work.
# export PATH="/opt/homebrew/opt/openssl@1.1/bin:$PATH"
# export PKG_CONFIG_PATH="/opt/homebrew/opt/openssl@1.1/lib/pkgconfig"
# export LDFLAGS="-L/opt/homebrew/opt/openssl@1.1/lib"
# export CPPFLAGS="-I/opt/homebrew/opt/openssl@1.1/include"

# Not using truby right now so not installing it
# ruby-install ruby 3.1.3
# gem install jekyll --user-install

# Dont think I need this right now
#curl https://pyenv.run | bash

brew cleanup
rm -f -r /Library/Caches/Homebrew/*

exit 0