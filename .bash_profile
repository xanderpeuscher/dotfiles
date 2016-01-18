# adding ~/bin to the path
export PATH="$(brew --prefix php70)/bin:$PATH"
export PATH=${PATH}:$HOME/bin

# adding RVM
if [[ -s $HOME/.rvm/scripts/rvm ]]; then
  source $HOME/.rvm/scripts/rvm;
fi

# GIT tab completion
if [ -f ~/.git-completion.bash ]; then
  . ~/.git-completion.bash
fi

# setting the default editor
export EDITOR='subl -w'

# aliases
alias behat='./vendor/bin/behat'
alias phpunit='./vendor/bin/phpunit'
alias art='php artisan'
alias rb='php artisan --env=testing migrate && php artisan --env=testing db:seed && grunt && vendor/bin/behat --verbose --stop-on-failure'
alias sb='php artisan serve --host=behat.localhost'
alias rbs='
	php artisan --env=testing migrate &&
	php artisan --env=testing db:seed &&
	grunt &&
	vendor/bin/behat --verbose --stop-on-failure'
	# Add the path to the project folder, like "/Users/Xander/Development/"$1"/app/tests/acceptance/"$2".feature"

alias showHidden='defaults write com.apple.finder AppleShowAllFiles YES'
alias hideHidden='defaults write com.apple.finder AppleShowAllFiles NO'
alias openBash='subl ~/.bash_profile'
alias apache='sudo apachectl'

# setting colors
# http://stackoverflow.com/questions/1550288/mac-os-x-terminal-colors
export TERM="xterm-color"

RED="\[\e[0;31m\]"
GREEN="\[\e[0;32m\]"
YELLOW="\[\e[0;33m\]"
BLUE="\[\e[0;34m\]"
RESETCOLOR="\[\e[0m\]" 

export CLICOLOR=1
export LSCOLORS=GxFxCxDxBxegedabagaced

# setting the PS1
function parse_git_dirty() {
        [[ $(git status 2> /dev/null | tail -n1) != *"working directory clean"* ]] && echo "*"
}

function parse_git_branch() {
        git branch --no-color 2> /dev/null | sed -e '/^[^*]/d' -e "s/* \(.*\)/\1$(parse_git_dirty)/"
}

export PS1="\n    ${BLUE}\w\$([[ -n \$(git branch 2> /dev/null) ]] && echo \"  ${YELLOW}\")\$(parse_git_branch)\n${RESETCOLOR}→ "

source ~/.profile

