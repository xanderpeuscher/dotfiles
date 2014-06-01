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

echo -e "${BLUE}Installing Ruby with RVM${RESETCOLOR}"
\curl -sSL https://get.rvm.io | bash -s stable --ruby=1.9.3

echo -e "${BLUE}Installing Ruby Gems{RESETCOLOR}"
gem install cocoapods rails sinatra

echo -e "${BLUE}Installing homebrew${RESETCOLOR}"
ruby -e "$(curl -fsSL https://raw.github.com/Homebrew/homebrew/go/install)"

echo -e "${BLUE}Installing couple of base homebrew packages${RESETCOLOR}"
brew install wget git gcutil ctags python
brew tap josegonzalez/homebrew-php
brew tap homebrew/dupes
brew tap homebrew/versions
brew install php55-intl
brew install josegonzalez/php/composer
brew install mcrypt php55-mcrypt

echo -e "Installing PIP (Python)"
easy_install pip
pip install --user git+git://github.com/Lokaltog/powerline #powerline for vim

echo -e "Setting up VIM"
brew install vim --with-python --with-ruby
mkdir -p ~/.vim/autoload ~/.vim/bundle
curl -so ~/.vim/autoload/pathogen.vim https://raw.githubusercontent.com/tpope/vim-pathogen/HEAD/autoload/pathogen.vim
git clone https://github.com/scrooloose/nerdtree.git ~/.vim/bundle/nerdtree #nerdtree for vim
git clone https://github.com/kien/ctrlp.vim.git ~/.vim/bundle/ctrlp #ctrlp for vim

# add vimrc :"python from powerline.ext.vim import source_plugin; source_plugin()"


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
# For hardware
brew cask install logitech-control-center

echo -e "${BLUE}Downloading some files{RESETCOLOR}"
wget -O ~/Downloads/Inconsolata.otf http://levien.com/type/myfonts/Inconsolata.otf

mkdir -p ~/Library/Developer/Xcode/UserData/FontAndColorThemes
wget -O ~/Library/Developer/Xcode/UserData/FontAndColorThemes/halflife.dvtcolortheme https://raw.githubusercontent.com/daylerees/colour-schemes/master/xcode/halflife.dvtcolortheme

echo -e "${BLUE}Setting up sublime${RESETCOLOR}"
ln -sf ~/Applications/Sublime\ Text\ 2.app/ ~/bin/subl
wget -O  ~/Library/Application\ Support/Sublime\ Text\ 2/Packages/User/Preferences.sublime-settings https://raw.githubusercontent.com/tscheepers/dotfiles/master/sublime/Preferences.sublime-settings
git clone https://github.com/daylerees/colour-schemes.git ~/Library/Application\ Support/Sublime\ Text\ 2/Packages/daylerees\ -\ themes

echo -e "${GREEN}Script done${RESETCOLOR}"
