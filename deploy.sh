#!/bin/sh

rm -r config/
git checkout -- config/

git pull
rename 's/\.example$//' config/*

cp ~/bot_token .

pip3 install -r requirements.txt

pidof python3 | python3 main.py &
