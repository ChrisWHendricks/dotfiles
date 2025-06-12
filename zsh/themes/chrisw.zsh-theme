# Enable prompt substitution
setopt PROMPT_SUBST

SEP1=" 󰇝 "
VENV_ICON="󰆧"
PROMPT_FG=${FG[033]}
PROMPT_BG=${BG[234]}
RC=${FX[reset]}
LF=$'\n'
GITHUB=$''

function set_color() {
    local fg_code=$1
    local bg_code=$2
    local text=$3

    # if 4t argument this is FX code
    local fx_code=$4

    local colored_text="${FX[$fx_code]}${FG[${fg_code}]}${BG[${bg_code}]}${text}${FX[reset]}"
    echo -e "$colored_text"
}

sep(){
    set_color 119 "" "$SEP1"
}

username_prompt()
{
    local username=$(whoami)

    echo -n -e "$username"

}

cwh-prompt-right() {
    shell=$(basename $SHELL)
    echo "⟨ ${PROMPT_BG}$(username_prompt)$(sep)$(prompt_python)${PROMPT_BG}$(sep)$shell 〉${FX[reset]}"
}

cwh-prompt-left(){


    local gap="          "

    prompt=""
    prompt+="$(git_prompt) | $(dir_prompt)"
    #echo "${PROMPT_BG}$(dir_prompt)${FX[reset]}"
    echo -e -n $prompt
}

dir_prompt() {
    local fg="${FG[119]}"
    local bg="%K{51}"
    
    icon="󰆧"
    if [ -n "$VIRTUAL_ENV" ]; then
        
       icon="%F{201}$VENV_ICON"
    else
       icon="󰉖"
    fi
    local_dir=$PWD
    local_dir=${local_dir/#$HOME/\~}

    echo -n -e "${fg}$icon ${local_dir}${fg} 󰅂 "
}



function prompt_python() {

    local python_version=$(python3 --version 2>&1 | awk '{print $2}')
    if [ -n "$VIRTUAL_ENV" ]; then
        python_env=$(basename "$VIRTUAL_ENV")
        fg="%F{201}"
        bg=$PROMPT_BG
        echo -n "${fg}${bg} $python_version ($python_env)%F{015}"
    else
        fg="%F{015}"
         bg=$PROMPT_BG
        echo -n "${fg}${bg} $python_version %F{015}"
    fi
}

git_prompt() {
    # If in git repo
    if ! $(git rev-parse --is-inside-work-tree >/dev/null 2>&1); then
        return
    fi
    # Get local and remote branch names
    local_branch=$(git rev-parse --abbrev-ref HEAD)
    remote_branch=$(git config --get branch.$local_branch.remote)
    remote_branch_name=$(git config --get branch.$local_branch.merge | cut -d/ -f3)

    gitStatusMsg=$(git_prompt_status)
    #trim whitespace
    gitStatusMsg=$(echo $gitStatusMsg | xargs)

    echo -e -n "$PROMPT_BG%F{42}$GITHUB $local_branch ($remote_branch) ${gitStatusMsg}" 
}

git_prompt_status() {
    # Git status indicators with modern symbols
    ZSH_THEME_GIT_PROMPT_CLEAN="%F{82}\uf058%f"
    ZSH_THEME_GIT_PROMPT_ADDED="%F{#26a641}%f"
    ZSH_THEME_GIT_PROMPT_MODIFIED="%F{blue}%f"
    ZSH_THEME_GIT_PROMPT_DELETED="%F{#f85149}󰮈%f"
    ZSH_THEME_GIT_PROMPT_RENAMED="%F{#2188ff}󰑕%f"
    ZSH_THEME_GIT_PROMPT_UNMERGED="%F{#bf5af2}%f"
    ZSH_THEME_GIT_PROMPT_UNTRACKED="%F{196}\ue275"
    ZSH_THEME_GIT_PROMPT_STASHED="%F{#87ceeb}%f"
    ZSH_THEME_GIT_PROMPT_BEHIND="%F{#ff5555}%f"
    ZSH_THEME_GIT_PROMPT_AHEAD="%F{#50fa7b}%f"
    ZSH_THEME_GIT_PROMPT_UNSTAGED="%F{red}\uf06a%f"

    local INDEX=$(command git status --porcelain -b 2>/dev/null)
    local STATUS=""

    # ADDED
    if $(echo "$INDEX" | grep '^A ' &>/dev/null); then
        if $(echo "$INDEX" | grep '^A ' &>/dev/null); then
            STATUS="$ZSH_THEME_GIT_PROMPT_ADDED $STATUS"
        fi
    fi

    # MODIFIED
    if $(echo "$INDEX" | grep '^M\s' &>/dev/null) || $(echo "$INDEX" | grep '^\sM' &>/dev/null); then
        STATUS="$ZSH_THEME_GIT_PROMPT_MODIFIED $STATUS"
    fi

    # DELETED
    if $(echo "$INDEX" | grep '^D ' &>/dev/null); then
        STATUS="$ZSH_THEME_GIT_PROMPT_DELETEDn$STATUS"
    fi

    # RENAMED
    if $(echo "$INDEX" | grep '^R ' &>/dev/null); then
        STATUS="$ZSH_THEME_GIT_PROMPT_RENAMED $STATUS"
    fi

    # UNMERGED
    if $(echo "$INDEX" | grep '^U ' &>/dev/null); then
        STATUS="$ZSH_THEME_GIT_PROMPT_UNMERGED $STATUS"
    fi

    # STAGED
    if $(echo "$INDEX" | grep '^[MADRC]M ' &>/dev/null); then
        STATUS="$ZSH_THEME_GIT_PROMPT_STAGED $STATUS"
    fi

    if $(echo "$INDEX" | grep -E 'behind' &>/dev/null); then
        STATUS="$ZSH_THEME_GIT_PROMPT_BEHIND $STATUS"
    fi

    if $(echo "$INDEX" | grep -E 'ahead' &>/dev/null); then
        STATUS="$ZSH_THEME_GIT_PROMPT_AHEAD $STATUS"
    fi

    # If no status is found, set to clean
    if [ -z "$STATUS" ]; then
        STATUS="$ZSH_THEME_GIT_PROMPT_CLEAN"
    fi

    untracked_count=$(git status --porcelain | awk '/^\?\?/ {count++} END {print count}')

    #check if untracked_count is empty
    if [ -z "$untracked_count" ]; then
        untracked_count=0
    fi
    if [ $untracked_count -gt 0 ]; then
        STATUS="$STATUS $ZSH_THEME_GIT_PROMPT_UNTRACKED "
    fi

    # remove extra spaces fron Status
    STATUS=$(echo $STATUS | xargs)
    echo -e -n "$STATUS$RC"

}

precmd() {

    unset RPROMPT
    PROMPT=$'$LF%{%f%b%k%}$(cwh-prompt-left)%{%f%b%k%}%F{119}%{%f%b%k%}'
    #RPROMPT=" $(prompt_python) $(git_prompt)"

    # shell=$(basename $SHELL)
    # RPROMPT="${FG[082]}$shell${FX[reset]}"
    # RPROMPT="$PROMPT_BG| Current Theme: ${ZSH_THEME} ${FX[reset]}"
    #RPROMPT=$'%{%f%b%k%}$(cwh-prompt-right)%{%f%b%k%}'

}
