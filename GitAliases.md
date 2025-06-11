# Git Aliases

This document lists all the Git aliases available in this dotfiles repository.

## Basic Commands

| Alias | Description |
|-------|-------------|
| `git co` | Shorthand for `git checkout` |
| `git cob` | Shorthand for `git checkout -b` to create and checkout a branch |
| `git cm "message"` | Stage all changes and commit with the specified message |
| `git st` | Show short status (equivalent to `git status -s`) |
| `git amend` | Amend the last commit with all current changes |
| `git unstage` | Unstage a file (reset from HEAD) |
| `git discard` | Discard changes to a file (checkout --) |

## Branch Management

| Alias | Description |
|-------|-------------|
| `git branches` | List all branches including remote branches |
| `git default` | Show the default branch name (usually main or master) |
| `git delete` | Delete a branch (shorthand for `git branch -d`) |
| `git bclean-local` | Delete all branches that have been merged into the default branch |
| `git bclean` | Run GitHub CLI prune and clean local branches |
| `git bdone` | Switch to default branch, update it, and clean merged branches |
| `git gone` | List branches whose upstream has been removed |

## History and Logs

| Alias | Description |
|-------|-------------|
| `git ls` | Better formatted git log |
| `git hist` | Show graph-based commit history |
| `git history` | Show detailed graph-based commit history with dates |
| `git graph` | Show compact graph of recent commits |
| `git latest` | Show the commit message and files from the latest commit |
| `git lds` | Log with short date format |
| `git churn` | Show files with the most changes (highest churn) |

## Remote Operations

| Alias | Description |
|-------|-------------|
| `git open` | Open the repository URL in a browser (OS-aware) |
| `git pr` | Open the pull request creation page for the current branch |
| `git remotes` | Show all remotes with their URLs |
| `git up` | Pull with rebase, prune, and update submodules |
| `git sync` | Pull with rebase and then push |
| `git fp` | Force push current branch with lease (safer force push) |
| `git pushf` | Force push with lease and includes check |
| `git publish` | Push branch, delete draft, and open in browser |

## Rebase and Reset

| Alias | Description |
|-------|-------------|
| `git abort` | Abort an in-progress rebase |
| `git rba` | Abort an in-progress rebase (shorthand) |
| `git rbc` | Stage all changes and continue rebase |
| `git re` | Fetch and rebase on top of the default branch |
| `git ri` | Interactive rebase on top of the default branch |
| `git undo` | Undo the last commit but keep changes |

## Stashing and Saving

| Alias | Description |
|-------|-------------|
| `git save` | Create a savepoint commit with all changes |
| `git wip` | Create a "Work in Progress" commit with all changes |
| `git stashes` | List all stashes |
| `git restore` | Create a savepoint and reset to specified commit |
| `git wipe` | Create a savepoint and wipe all changes |

## Utility

| Alias | Description |
|-------|-------------|
| `git aliases` | List all git aliases |
| `git cleanup` | Clean working directory but keep specific files |
| `git conflicts` | Show files with merge conflicts |
| `git files [commit]` | List files changed in specified commit (or HEAD) |
| `git find "pattern"` | Search for files matching pattern in the repository |
| `git grep "pattern"` | Search for pattern in tracked files (case insensitive) |
| `git ec` | Edit global git config |
| `git new` | Initialize a new git repo with main as default branch |

## Configuration

| Alias | Description |
|-------|-------------|
| `git set-origin` | Set the origin remote URL |
| `git set-upstream` | Set the upstream remote URL |