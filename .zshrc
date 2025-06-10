# Chris W Hendricks's .zshrc

# Path to your oh-my-zsh installation.
export ZSH="$HOME/.oh-my-zsh"

# Theme
ZSH_THEME="robbyrussell"

# Plugins
plugins=(
  git
  macos
  docker
  npm
  node
  vscode
)

source $ZSH/oh-my-zsh.sh

# User configuration
export PATH="$HOME/bin:/usr/local/bin:$PATH"

# Preferred editor for local and remote sessions
export EDITOR='nano'

# Aliases
alias zshconfig="$EDITOR ~/.zshrc"
alias ohmyzsh="$EDITOR ~/.oh-my-zsh"
alias ls="ls -G"
alias ll="ls -la"
alias g="git"
alias gs="git status"
alias gc="git commit"
alias gp="git push"
alias codehome="code ~"
alias codesrc="code ~/src"
alias rz="source ~/.zshrc"

export DOTFILES_REPO="https://github.com/ChrisWHendricks/dotfiles"
export DOTFILES_BRANCH="dev"


# Custom functions
function mkcd() {
  mkdir -p "$@" && cd "$_"
}

# Load local config if it exists
[[ -f ~/.zshrc.local ]] && source ~/.zshrc.local