if [ "Darwin" = 'Darwin' ]; then
    alias ls='ls -G'
else
    eval `dircolors ~/.colorrc`
    alias ls='ls --color=auto'
fi

alias la='ls -a'
alias ll='ls -l'
alias tree='tree -C'
alias cp='cp -i'
alias mv='mv -i'
alias rm='rm -i'

# $ pip3 install jupyter
alias jn='jupyter notebook'
