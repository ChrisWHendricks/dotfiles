# Terminal Setup with Nerd Fonts

## What are Nerd Fonts?

Nerd Fonts patch developer targeted fonts with a high number of glyphs (icons). Specifically to add a high number of extra glyphs from popular 'iconic fonts' such as Font Awesome, Devicons, Octicons, and others. They also include all Powerline symbols, which are special glyphs used by Powerline-compatible terminal themes to create beautiful status lines and prompts.

## Setting up iTerm2 with Nerd Fonts

1. After running the `install_tools.sh` script, you'll have several Nerd Fonts installed:
   - Hack Nerd Font
   - Fira Code Nerd Font
   - JetBrains Mono Nerd Font

2. Open iTerm2 preferences:
   - Go to `iTerm2 > Preferences > Profiles > Text`
   - Click on `Font` and select one of the installed Nerd Fonts (e.g., `JetBrainsMono Nerd Font`)
   - Adjust the font size to your preference

3. Test your font by typing special characters in your terminal:
   ```
   echo -e "\uf296 \ue74e \uf308"
   ```

## Using Nerd Fonts with VS Code

1. Open VS Code settings:
   - Press `Cmd+,` or go to `Code > Preferences > Settings`
   - Search for "font"
   - In "Font Family", add one of the Nerd Fonts at the beginning of the list:
     ```
     'JetBrainsMono Nerd Font', Menlo, Monaco, 'Courier New', monospace
     ```

2. For the integrated terminal:
   - Search for "terminal font" in settings
   - Set the "Terminal > Integrated: Font Family" to your preferred Nerd Font

## Popular Terminal Themes and Plugins that work well with Nerd Fonts

- Oh My Zsh with themes like Powerlevel10k, Agnoster, or Spaceship
- Starship prompt (cross-shell prompt)
- Tmux with custom status lines using Nerd Font icons

Enjoy your enhanced terminal experience with beautiful icons and ligatures!