#!/bin/bash
#
# Bootstrap script for Chris W Hendricks's dotfiles
#
# This script sets up a brand new machine with all prerequisites needed
# to run the 'dot' CLI tool. It handles:
# - Python 3.9+ installation
# - Homebrew installation (macOS) or apt updates (Linux)
# - Git installation
# - Virtual environment setup
# - CLI installation
#

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Helper functions
print_success() {
    echo -e "${GREEN}✓${NC} $1"
}

print_error() {
    echo -e "${RED}✗${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}⚠${NC} $1"
}

print_info() {
    echo -e "${BLUE}ℹ${NC} $1"
}

print_header() {
    echo ""
    echo -e "${BLUE}========================================${NC}"
    echo -e "${BLUE}$1${NC}"
    echo -e "${BLUE}========================================${NC}"
    echo ""
}

# Detect OS
detect_os() {
    if [[ "$OSTYPE" == "darwin"* ]]; then
        OS="macos"
    elif [[ "$OSTYPE" == "linux-gnu"* ]]; then
        OS="linux"
    else
        print_error "Unsupported operating system: $OSTYPE"
        exit 1
    fi
    print_info "Detected OS: $OS"
}

# Check if command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Install Homebrew on macOS
install_homebrew() {
    if ! command_exists brew; then
        print_info "Installing Homebrew..."
        /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

        # Add Homebrew to PATH for Apple Silicon Macs
        if [[ $(uname -m) == "arm64" ]]; then
            echo 'eval "$(/opt/homebrew/bin/brew shellenv)"' >> ~/.zprofile
            eval "$(/opt/homebrew/bin/brew shellenv)"
        fi

        print_success "Homebrew installed"
    else
        print_success "Homebrew already installed"
    fi
}

# Update package manager on Linux
update_apt() {
    print_info "Updating apt package lists..."
    sudo apt-get update -qq
    print_success "Package lists updated"
}

# Install Git
install_git() {
    if ! command_exists git; then
        print_info "Installing Git..."
        if [[ "$OS" == "macos" ]]; then
            brew install git
        else
            sudo apt-get install -y git
        fi
        print_success "Git installed"
    else
        print_success "Git already installed ($(git --version))"
    fi
}

# Install Python 3
install_python() {
    local python_cmd=""
    local python_version=""

    # Check for python3 command
    if command_exists python3; then
        python_version=$(python3 --version 2>&1 | awk '{print $2}')
        major=$(echo "$python_version" | cut -d. -f1)
        minor=$(echo "$python_version" | cut -d. -f2)

        # Check if version is 3.9 or higher
        if [[ "$major" -ge 3 ]] && [[ "$minor" -ge 9 ]]; then
            print_success "Python $python_version already installed"
            return 0
        else
            print_warning "Python $python_version is installed but version 3.9+ is required"
        fi
    fi

    # Install Python
    print_info "Installing Python 3..."
    if [[ "$OS" == "macos" ]]; then
        brew install python@3
        print_success "Python installed via Homebrew"
    else
        sudo apt-get install -y python3 python3-pip python3-venv
        print_success "Python installed via apt"
    fi

    # Verify installation
    if command_exists python3; then
        python_version=$(python3 --version 2>&1)
        print_success "Python installed: $python_version"
    else
        print_error "Python installation failed"
        exit 1
    fi
}

# Setup virtual environment
setup_venv() {
    local dotfiles_dir="$1"
    local venv_dir="$dotfiles_dir/venv"

    if [[ -d "$venv_dir" ]]; then
        print_success "Virtual environment already exists"
    else
        print_info "Creating virtual environment..."
        python3 -m venv "$venv_dir"
        print_success "Virtual environment created"
    fi

    # Activate and upgrade pip
    print_info "Activating virtual environment and upgrading pip..."
    source "$venv_dir/bin/activate"
    pip install --upgrade pip setuptools wheel -q
    print_success "Virtual environment ready"
}

# Install Python dependencies
install_dependencies() {
    local dotfiles_dir="$1"

    print_info "Installing Python dependencies..."
    source "$dotfiles_dir/venv/bin/activate"
    pip install -e "$dotfiles_dir" -q
    print_success "Dependencies installed"
}

# Add venv to PATH
update_shell_config() {
    local dotfiles_dir="$1"
    local shell_config=""

    # Determine shell config file
    if [[ -n "$ZSH_VERSION" ]] || [[ "$SHELL" == *"zsh"* ]]; then
        shell_config="$HOME/.zshrc"
    elif [[ -n "$BASH_VERSION" ]] || [[ "$SHELL" == *"bash"* ]]; then
        shell_config="$HOME/.bashrc"
    else
        print_warning "Unknown shell, skipping PATH update"
        return
    fi

    # Check if PATH already includes venv
    local venv_path="$dotfiles_dir/venv/bin"
    if grep -q "$venv_path" "$shell_config" 2>/dev/null; then
        print_success "Shell config already includes dotfiles venv in PATH"
    else
        print_info "Adding dotfiles venv to PATH in $shell_config..."
        echo "" >> "$shell_config"
        echo "# Dotfiles CLI" >> "$shell_config"
        echo "export PATH=\"$venv_path:\$PATH\"" >> "$shell_config"
        print_success "PATH updated (restart shell or run: source $shell_config)"
    fi
}

# Main installation flow
main() {
    print_header "Dotfiles Bootstrap"

    # Get dotfiles directory
    DOTFILES_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
    print_info "Dotfiles directory: $DOTFILES_DIR"

    # Detect OS
    detect_os

    # Install prerequisites
    print_header "Installing Prerequisites"

    if [[ "$OS" == "macos" ]]; then
        install_homebrew
    else
        update_apt
    fi

    install_git
    install_python

    # Setup Python environment
    print_header "Setting Up Python Environment"
    setup_venv "$DOTFILES_DIR"
    install_dependencies "$DOTFILES_DIR"

    # Update shell config
    print_header "Configuring Shell"
    update_shell_config "$DOTFILES_DIR"

    # Final message
    print_header "Bootstrap Complete!"
    print_success "All prerequisites installed"
    print_info "To install dotfiles, run:"
    echo ""
    echo "    source $DOTFILES_DIR/venv/bin/activate"
    echo "    dot install"
    echo ""
    print_info "To check installation status, run:"
    echo ""
    echo "    dot check"
    echo ""
    print_info "For help, run:"
    echo ""
    echo "    dot --help"
    echo ""
    print_warning "Note: You may need to restart your shell or run:"
    echo ""
    echo "    source ~/.zshrc"
    echo ""
    echo "to use the 'dot' command without activating the venv manually."
}

# Run main function
main
