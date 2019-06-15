#! /bin/sh

# setup GitHub account
## setup user account
echo -n "GitHub user name >"
read INPUT
git config --global user.name "$INPUT"
echo -n "GitHub email >"
read INPUT
git config --global user.email "$INPUT"
ssh-keygen

echo "copy ./ssh/id_rsd.pub to SSH Public Keys in GitHub"
echo "top right icon -> Settings -> SSH and GPG keys -> New SSH key"
echo "Title: any"
echo "Key: copy below"
cat ~/.ssh/id_rsa.pub
echo "press Enter after setup finished"
read INPUT
