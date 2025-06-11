# Enable prompt substitution
setopt PROMPT_SUBST

SEP1=$'\ue0b1'
PROMPT_FG=${FG[033]}
RC=${FX[reset]}
LF=$'\n'
GITHUB=$''

cwh-prompt() {
    echo "$(dir_prompt)$(git_prompt)"
}

dir_prompt() {
    local fg="%F{51}"
    local newPathSep="%F{magenta}  $fg"
    local_dir=$PWD
    local_dir=${local_dir/#$HOME/\~}

    echo -n "${fg}${local_dir}"
}

python_version_prompt() {
    echo -n "🐍 "
}

git_prompt(){
        # If in git repo
    if ! $(git rev-parse --is-inside-work-tree >/dev/null 2>&1); then
        return
    fi
    # Get local and remote branch names
    local_branch=$(git rev-parse --abbrev-ref HEAD)
    remote_branch=$(git config --get branch.$local_branch.remote)
    remote_branch_name=$(git config --get branch.$local_branch.merge | cut -d/ -f3)

    gitStatusMsg=$(git_prompt_status)


    echo -e -n " |%F{42} $GITHUB  $local_branch ($remote_branch) $gitStatusMsg%f$LF"

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

    echo "$STATUS $RC"

}

precmd() {
    
 user=`whoami`
  PROMPT=$'$LF%F{165}($USER) %{%f%b%k%}$(cwh-prompt)%{%f%b%k%}$LF%F{119}$ %{%f%b%k%}'

}