# Enable prompt substitution
setopt PROMPT_SUBST

# sourcre all scripts in the scripts directory
for script in $CWHZSH/scripts/*.zsh; do
  #echo "Sourcing $script"
  source $script
done

precmd() {

  # Update the prompt with the current working directory
  #PROMPT="$(cwh-prompt)"
  PROMPT=$'$LF%{%f%b%k%}$(cwh-prompt)%{%f%b%k%}$LF%F{119}$ %{%f%b%k%}'
 

}



# Define Aliases
alias rz="source ~/.zshrc" # Reload this file to update env vars, oh my zsh themes and what-not
alias c="clear"
alias cls=clear

# its annoying that python is python3 and not just python so I create at alias for my sanity. (Same for pip)
alias python="python3"
alias pip="pip3"

#  I use this a lot so I create an alias for it
alias botodocs='open https://boto3.amazonaws.com/v1/documentation/api/latest/index.html'

