#!/bin/sh

git fetch --all
git reset --hard origin/master

./deploy.sh
