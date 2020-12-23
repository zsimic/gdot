Synopsis:

```
get started with one of:
    gdot attach github:...
    gdot attach https://github.com/.../dotfiles
    gdot detach

    gdot symlink attach ~/Dropbox/roaming
    gdot symlink detach

gdot status
gdot diff
gdot list
gdot add .bashrc
gdot add ~/.config/htop/
gdot pull -y -a
gdot push -m "changed foo..."
gdot rm -f .profile
gdot reset                      # same as pull -y
gdot sync                       # same as pull + push
gdot sync -m "changed foo..."

gdot git ...

gdot neofetch

~/.config/gdot-git-store
    .git -> remote https://github.com/.../dotfiles
    .gitignore
    local-only
        symlink: ~/Dropbox/roaming
    symlink-only?:
        ~/foo
    tracked:
        ~/bin/
        ~/.bashrc
        ~/.config/htop/
        sublime-text

special:
    sublime-text:
        linux: ~/.config/sublime-text-3/Packages/User/
        mac: ~/Library/Application Support/Sublime Text 3/Packages/User/
        windows: %APPDATA%/Sublime Text 3/Packages/User/
    iterm2:
        mode: seed-only
        mac: ~/Library/Preferences/com.googlecode.iterm2.plist
    keybinding:
        mode: copy
        mac: ~/Library/KeyBindings/DefaultKeyBinding.dict
```
