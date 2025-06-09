# Chris W Hendricks's .bash_profile

# Load .bashrc if it exists
[[ -f ~/.bashrc ]] && source ~/.bashrc

# Set PATH
export PATH="$HOME/bin:/usr/local/bin:$PATH"

# Set default editor
export EDITOR='nano'

# History control
export HISTCONTROL=ignoreboth:erasedups
export HISTSIZE=10000
export HISTFILESIZE=10000

# Prompt
export PS1="\[\033[36m\]\u\[\033[m\]@\[\033[32m\]\h:\[\033[33;1m\]\w\[\033[m\]\$ "

# Load local config if it exists
[[ -f ~/.bash_profile.local ]] && source ~/.bash_profile.local