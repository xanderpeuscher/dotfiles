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

echo -e "${BLUE}Installing Caskroom{RESETCOLOR}"
ruby -e "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/master/install)" < /dev/null 2> /dev/null ; brew install caskroom/cask/brew-cask 2> /dev/null

echo -e "${BLUE}Installing couple of base homebrew packages${RESETCOLOR}"
brew install wget git gcutil ctags python mysql
brew install homebrew/php/composer
brew install php70
brew install php71
brew install php70-mcrypt
brew install php71-mcrypt
brew install --HEAD homebrew/php/php70-memcached
brew install memcached
brew install php70-timecop
brew install php70-intl
brew install php70-gmp
brew install php71-timecop
brew install php71-intl
brew install php71-gmp

echo -e "${BLUE}Installing some handy tools ${RESETCOLOR}"
brew install brew-php-switcher

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
brew cask install slack
brew cask install adobe-creative-cloud
# Plugins/utilities
brew cask install the-unarchiver
# For development
brew cask install phpstorm
brew cask install crashlytics
brew cask install sublime-text
brew cask install flow
brew cask install virtualbox
brew cask install vagrant
brew cask install sequel-pro
brew cask install filezilla
# For hardware
brew cask install logitech-control-center
brew cask install logitech-unifying
brew cask install logitech-options

echo -e "${BLUE}Setting up sublime${RESETCOLOR}"
ln -sf ~/Applications/Sublime\ Text\ 2.app/ ~/bin/subl
wget -O  ~/Library/Application\ Support/Sublime\ Text\ 2/Packages/User/Preferences.sublime-settings https://raw.githubusercontent.com/xanderpeuscher/dotfiles/master/sublime/Preferences.sublime-settings
git clone https://github.com/daylerees/colour-schemes.git ~/Library/Application\ Support/Sublime\ Text\ 2/Packages/daylerees\ -\ themes

echo -e "${BLUE}Setting up Git tab completion${RESETCOLOR}"
curl https://raw.githubusercontent.com/git/git/master/contrib/completion/git-completion.bash -o ~/.git-completion.bash

echo -e "${GREEN}Script done${RESETCOLOR}"
