#!/bin/sh

git fetch --all
git reset --hard origin/master

cp config/messages.json.example config/messages.json
cp config/quacks.txt.example config/quacks.txt
cp config/games.txt.example config/games.txt

pip3 install -r requirements.txt

./restart.sh
