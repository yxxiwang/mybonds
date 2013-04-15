# .bash_profile

# Get the aliases and functions
if [ -f ~/.bashrc ]; then
	. ~/.bashrc
fi

# User specific environment and startup programs

alias sp='supervisorctl '
alias gitpull='git pull'
alias gitpush='git push origin master '
alias gitset='git remote set-url origin https://yxxiwang@github.com/yxxiwang/mybonds.git'
alias dstat='dstat -cdlmnpsy'
alias cli='redis-cli '
alias cli1='redis-cli -n 1 '
set -o vi

PATH=$PATH:$HOME/bin:/usr/bin

export PATH
