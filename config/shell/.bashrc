# Chris W Hendricks's .bashrc

# Aliases
alias ls='ls -G'
alias ll='ls -la'
alias la='ls -A'
alias l='ls -CF'
alias g='git'
alias gs='git status'
alias gc='git commit'
alias gp='git push'

# Functions
mkcd() {
  mkdir -p "$@" && cd "$_"
}

# Load local config if it exists
[[ -f ~/.bashrc.local ]] && source ~/.bashrc.local