# This file is slightly necessary in my development environment
# As this program was created in termux on an android phone
eval "$(ssh-agent -s)"
ssh-add alo
git add .
echo "Enter your commit message: "
read commit_message
git commit -m "$commit_message"
git push
