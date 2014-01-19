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
mkdir -p ~/.rvm/src
cd ~/.rvm/src
rm -rf ./rvm
git clone --depth 1 git://github.com/wayneeseguin/rvm.git
cd rvm
./install
cd ~/

source ~/.bash_profile # To reload the bash profile
source ~/.bashrc # To reload the bashrc

rvm install 1.9.2
rvm install 2.1.0
rvm --default 2.1.0

echo -e "${BLUE}Installing Ruby Gems{RESETCOLOR}"
gem install cocoapods rails sinatra

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

echo -e "${BLUE}Opening apps that need further setup${RESETCOLOR}"
open ~/Applications/Dropbox.app # To enter dropbox details

echo -e "${BLUE}Adding items to the dock${RESETCOLOR}"
# Google Chrome
defaults write com.apple.dock persistent-apps -array-add "<dict><key>tile-data</key><dict><key>file-data</key><dict><key>_CFURLString</key><string>~/Applications/Google Chrome.app</string><key>_CFURLStringType</key><integer>0</integer></dict></dict></dict>"
# Spotify
defaults write com.apple.dock persistent-apps -array-add "<dict><key>tile-data</key><dict><key>file-data</key><dict><key>_CFURLString</key><string>~/Applications/Spotify.app</string><key>_CFURLStringType</key><integer>0</integer></dict></dict></dict>"
# Sublime Text
defaults write com.apple.dock persistent-apps -array-add "<dict><key>tile-data</key><dict><key>file-data</key><dict><key>_CFURLString</key><string>~/Applications/Sublime Text 2.app</string><key>_CFURLStringType</key><integer>0</integer></dict></dict></dict>"
# Terminal
defaults write com.apple.dock persistent-apps -array-add "<dict><key>tile-data</key><dict><key>file-data</key><dict><key>_CFURLString</key><string>/Applications/Utilities/Terminal</string><key>_CFURLStringType</key><integer>0</integer></dict></dict></dict>"
# HipChat
defaults write com.apple.dock persistent-apps -array-add "<dict><key>tile-data</key><dict><key>file-data</key><dict><key>_CFURLString</key><string>~/Applications/HipChat.app</string><key>_CFURLStringType</key><integer>0</integer></dict></dict></dict>"
# 1Password
defaults write com.apple.dock persistent-apps -array-add "<dict><key>tile-data</key><dict><key>file-data</key><dict><key>_CFURLString</key><string>~/Applications/1Password.app</string><key>_CFURLStringType</key><integer>0</integer></dict></dict></dict>"
# Sequal Pro
defaults write com.apple.dock persistent-apps -array-add "<dict><key>tile-data</key><dict><key>file-data</key><dict><key>_CFURLString</key><string>~/Applications/Sequel Pro.app</string><key>_CFURLStringType</key><integer>0</integer></dict></dict></dict>"

killall Dock

echo -e "${GREEN}Script done${RESETCOLOR}"
