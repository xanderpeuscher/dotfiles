#!/usr/bin/env bash

TERM="xterm-color"
RED="\033[4;31m"
GREEN="\033[4;32m"
YELLOW="\033[4;33m"
BLUE="\033[4;34m"
RESETCOLOR="\033[0m" 

echo "Do you wish to execute the bootstrap script and install a whole lot of things? (You should have changed the current directory to the directory of this file)"
select yn in "Yes" "No"; do
    case $yn in
        Yes ) break;;
        No ) exit;;
    esac
done

echo -e "${BLUE}Setting up Bash and Git Config${RESETCOLOR}"

cp .bash_profile ~/.bash_profile
cp .bashrc ~/.bashrc
cp .gitconfig ~/.gitconfig
cp .vimrc ~/.vimrc

#echo -e "${BLUE}Installing Ruby with RVM${RESETCOLOR}"
#\curl -sSL https://get.rvm.io | bash -s stable --ruby=1.9.3

#echo -e "${BLUE}Installing Ruby Gems${RESETCOLOR}"
#gem install cocoapods rails sinatra jekyll jekyll-sass no-document 

echo -e "${BLUE}Installing homebrew${RESETCOLOR}"
ruby -e "$(curl -fsSL https://raw.github.com/Homebrew/homebrew/go/install)"

echo -e "${BLUE}Installing couple of base homebrew packages${RESETCOLOR}"
brew install wget git gcutil ctags python mysql
brew tap josegonzalez/homebrew-php
brew tap homebrew/dupes
brew tap homebrew/versions
brew install php55-intl
brew install josegonzalez/php/composer
brew install mcrypt php55-mcrypt
brew install composer phpunit

#echo -e "Installing PIP (Python)"
#sudo easy_install pip
#pip install --user git+git://github.com/Lokaltog/powerline #powerline for vim

#echo -e "Setting up VIM"
#brew install vim --with-python --with-ruby
#git clone https://github.com/gmarik/Vundle.vim.git ~/.vim/bundle/Vundle.vim
#vim +PluginInstall +qall

echo -e "${BLUE}Installing homebrew cask${RESETCOLOR}"
brew tap phinze/cask
brew install brew-cask

echo -e "${BLUE}Installing basic applications${RESETCOLOR}"
brew cask install google-chrome
brew cask install firefox
brew cask install spotify
brew cask install dropbox
brew cask install onepassword
brew cask install vlc
brew cask install hipchat
brew cask install adobe-creative-cloud
# Plugins/utilities
brew cask install silverlight
brew cask install prey
brew cask install the-unarchiver
# For development
brew cask install phpstorm
brew cask install crashlytics
brew cask install testflight
brew cask install sublime-text
brew cask install flow
brew cask install cyberduck
brew cask install virtualbox
brew cask install vagrant
brew cask install sequel-pro
brew cask install googleappenginelauncher
brew cask install dash
# For hardware
brew cask install logitech-control-center

echo -e "${BLUE}Downloading some files{RESETCOLOR}"
wget -O ~/Downloads/Inconsolata.otf http://levien.com/type/myfonts/Inconsolata.otf
wget -O ~/Downloads/Inconsolata%20for%20Powerline.otf https://github.com/Lokaltog/powerline-fonts/raw/master/Inconsolata/Inconsolata%20for%20Powerline.otf

mkdir -p ~/Library/Developer/Xcode/UserData/FontAndColorThemes
wget -O ~/Library/Developer/Xcode/UserData/FontAndColorThemes/halflife.dvtcolortheme https://raw.githubusercontent.com/daylerees/colour-schemes/master/xcode/halflife.dvtcolortheme

echo -e "${BLUE}Setting up sublime${RESETCOLOR}"
ln -sf ~/Applications/Sublime\ Text\ 2.app/ ~/bin/subl
wget -O  ~/Library/Application\ Support/Sublime\ Text\ 2/Packages/User/Preferences.sublime-settings https://raw.githubusercontent.com/tscheepers/dotfiles/master/sublime/Preferences.sublime-settings
git clone https://github.com/daylerees/colour-schemes.git ~/Library/Application\ Support/Sublime\ Text\ 2/Packages/daylerees\ -\ themes

echo -e "${BLUE}Setting up Git tab completion${RESETCOLOR}"
curl https://raw.githubusercontent.com/git/git/master/contrib/completion/git-completion.bash -o ~/.git-completion.bash

echo -e "${GREEN}Script done${RESETCOLOR}"
