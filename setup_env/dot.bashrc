source /usr/local/etc/bash_completion.d/git-prompt.sh
source /usr/local/etc/bash_completion.d/git-completion.bash
GIT_PS1_SHOWDIRTYSTATE=true

export PS1='\[\033[36m\]\u@\h\[\033[00m\]:\[\033[01m\]\w\[\033[32m\]$(__git_ps1)\[\033[00m\]\\$ '

source ~/venv/py37/bin/activate
cd ~/Documents/GitHub