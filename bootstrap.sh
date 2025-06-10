ghuser=$1
ghemail=$2

echo "Executing Bootstrap $1 - $2 " > ~/dotfiles-bootstrap.log

echo "Github Username is $GITHUB_AUTHOR_NAME" >> ~/dotfiles-bootstrap.log
echo "Github Email is $GITHUB_AUTHOR_EMAIL" >> ~/dotfiles-bootstrap.log
 ./script/bootstrap
