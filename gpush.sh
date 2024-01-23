#!/usr/bin/env bash
eval "$(ssh-agent -s)"
ssh-add alo
git add .
echo "Enter your commit message: "
read commit_message
git commit -m "$commit_message"
git push
