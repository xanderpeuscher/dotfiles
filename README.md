dotfiles
========

To get started bootstrapping your mac execute the following commands.

```
mkdir -p ~/Development/dotfiles  && \
curl -sS https://github.com/tscheepers/dotfiles/archive/master.zip > ~/Development/dotfiles.zip && \
unzip ~/Development/dotfiles.zip -d dotfiles && cd ~/Development/dotfiles && \
chmod u+x bootstrap.sh && ./bootstrap.sh
```
