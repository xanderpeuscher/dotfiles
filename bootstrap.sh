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

echo -e "${BLUE}Installing Ruby with RVM${RESETCOLOR}"
\curl -sSL https://get.rvm.io | bash -s stable --ruby=1.9.3

echo -e "${BLUE}Installing Ruby Gems{RESETCOLOR}"
gem install cocoapods rails sinatra

echo -e "${BLUE}Installing homebrew${RESETCOLOR}"
ruby -e "$(curl -fsSL https://raw.github.com/Homebrew/homebrew/go/install)"

echo -e "${BLUE}Installing couple of base homebrew packages${RESETCOLOR}"
brew install wget
brew install git
brew install gcutil
brew tap josegonzalez/homebrew-php
brew tap homebrew/versions
brew install php55-intl
brew install josegonzalez/php/composer
brew install mcrypt php55-mcrypt

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
# Plugins/utilities
brew cask install silverlight
brew cask install prey
# For development
brew cask install crashlytics
brew cask install testflight
brew cask install sublime-text
brew cask install flow
brew cask install virtualbox
brew cask install vagrant
brew cask install sequel-pro
# For hardware
brew cask install logitech-control-center

# Google App Engine
brew cask install googleappenginelauncher

echo -e "${BLUE}Linking commands${RESETCOLOR}"
ln -sf ~/Applications/Sublime\ Text\ 2.app/ ~/bin/subl

echo -e "${GREEN}Script done${RESETCOLOR}"
