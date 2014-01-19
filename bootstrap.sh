#!/usr/bin/env bash

TERM="xterm-color"
RED="\033[4;31m"
GREEN="\033[4;32m"
YELLOW="\033[4;33m"
BLUE="\033[4;34m"
RESETCOLOR="\033[0m" 

echo -e "${BLUE}Installing cocoapods${RESETCOLOR}"
sudo gem install cocoapods

echo -e "${BLUE}Installing homebrew${RESETCOLOR}"
ruby -e "$(curl -fsSL https://raw.github.com/Homebrew/homebrew/go/install)"

echo -e "${BLUE}Installing couple of base homebrew packages${RESETCOLOR}"
brew install wget
brew install git
brew install gcutil

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

echo -e "${BLUE}Linking commands${RESETCOLOR}"
ln -sf ~/Applications/Sublime\ Text\ 2.app/ ~/bin/subl

echo -e "${GREEN}Script done${RESETCOLOR}"

open ~/Applications/Dropbox.app # To enter dropbox details
