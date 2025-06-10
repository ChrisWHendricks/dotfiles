echo "Executing Bootstrap" > ~/dotfiles-bootstrap.log

echo "Github Username is $GITHUB_AUTHOR_NAME" >> ~/dotfiles-bootstrap.log
echo "Github Email is $GITHUB_AUTHOR_EMAIL" >> ~/dotfiles-bootstrap.log
 ./script/bootstrap
