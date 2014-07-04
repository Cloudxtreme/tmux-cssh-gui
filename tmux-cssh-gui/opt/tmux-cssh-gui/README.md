# TMUX-CSSH-GUI
_A simple, useful GUI on top of tmux-cssh._

## On top of TMUX-CSSH

_tmxu-cssh-gui_ is completely set on top of _tmux-cssh_. So that means, that all configurations made within _tmux_cssh-gui_ will be read from and saved to _tmux-cssh_'s home configuration file _~/.tmux-cssh. That means also, that you can use _tmux-cssh_ in reverse to call configurations made with _tmux-cssh-gui_

```
$ tmux-cssh -cs [configuration name from gui-list]
```

## Screenhots

![Screenshot 1](https://raw.githubusercontent.com/dennishafemann/tmux-cssh-gui/master/screenshots/1.png)
![Screenshot 2](https://raw.githubusercontent.com/dennishafemann/tmux-cssh-gui/master/screenshots/2.png)
![Screenshot 3](https://raw.githubusercontent.com/dennishafemann/tmux-cssh-gui/master/screenshots/3.png)

## Python requirements / libraries

Following python-libs are required, used and imported:

* argparse
* ConfigParser
* gtk, gtk.glade
* os
* re
* shlex
* subprocess

## Deb-Packages

Take a look at the deb-packages available:

<a href="https://github.com/dennishafemann/tmux-cssh-gui/tree/deb-package/deb-packages">branch: deb-packages</a>

## TMUX-CSSH

<a href="https://github.com/dennishafemann/tmux-cssh">tmux-cssh @ github.com</a>
