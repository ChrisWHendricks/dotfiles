# Chris W Hendricks's .zshrc

# Path to your oh-my-zsh installation.
export ZSH="$HOME/.oh-my-zsh"

# Theme
ZSH_THEME="chw-detailed" # Default theme

# Plugins
plugins=()

# plugins=(
#   git
#   macos
#   docker
#   npm
#   node
#   vscode
# )

source $ZSH/oh-my-zsh.sh

# User configuration
export PATH="$HOME/bin:/usr/local/bin:$PATH"

# Dotfiles CLI (Python) - ensure new dot command takes precedence
export PATH="$HOME/src/dotfiles/venv/bin:$PATH"

# Preferred editor for local and remote sessions
export EDITOR='nano'

# Load aliases
[[ -f ~/.zsh_aliases ]] && source ~/.zsh_aliases

# Custom functions
function mkcd() {
  mkdir -p "$@" && cd "$_"
}

# Load local config if it exists
[[ -f ~/.zshrc.local ]] && source ~/.zshrc.local