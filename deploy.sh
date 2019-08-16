#!/bin/sh

git fetch --all
git reset --hard origin/master

cp config/messages.json.example config/messages.json
cp config/quacks.txt.example config/quacks.txt

pip3 install -r requirements.txt

nohup python3 main.py $(pidof python3) > /dev/null 2> /dev/null < /dev/null &
