if test ! "$(uname)" = "Linux"
  then
  exit 0
fi

# Logging functions to make messages pretty
info() {
    printf "\r  [ \033[00;34m..\033[0m ] $1\n"
    
}

user() {
    printf "\r  [ \033[0;33m??\033[0m ] $1\n"
   
}

success() {
    printf "\r\033[2K  [ \033[00;32mOK\033[0m ] $1\n"
   
}

fail() {
    printf "\r\033[2K  [\033[0;31mFAIL\033[0m] $1\n"
    echo ''
    exit
}

echo "Installing Linux Apps"
info "Installing applications from Brewfile..."
brew bundle --file=$HOME/.dotfiles/linux/Brewfile

