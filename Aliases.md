# Shell Aliases

This document lists all the shell aliases and functions available in this dotfiles repository.

## ZSH Aliases

| Alias | Description |
|-------|-------------|
| `zshconfig` | Edit ~/.zshrc in your default editor |
| `ohmyzsh` | Edit ~/.oh-my-zsh in your default editor |
| `codehome` | Open home directory in VS Code |
| `codesrc` | Open ~/src directory in VS Code |
| `rz` | Reload the shell (equivalent to `exec zsh`) |
| `c` | Clear the terminal screen |
| `cls` | Clear the terminal screen (Windows habit alternative) |
| `botodocs` | Open AWS Boto3 documentation in browser (OS-aware) |

## Custom Functions

| Function | Description |
|----------|-------------|
| `edit [file]` | Edit a file with VS Code with wait flag |
| `mkcd [directory]` | Create a directory and change into it |

## Environment Variables

| Variable | Description |
|----------|-------------|
| `EDITOR` | Set to "code" for basic editor operations |
| `VISUAL` | Set to "code --wait" for visual editor operations |
| `PATH` | Includes ~/.dotfiles/bin, ~/bin, and /usr/local/bin |

## Local Customization

You can add your own custom aliases and functions by creating a `~/.zshrc.local` file, which will be automatically sourced if it exists.