#!/bin/sh

sleep 10

rm -r config/
git checkout -- config/

git pull
rename 's/\.example$//' config/*

pip3 install -r requirements.txt

pidof python3 | python3 main.py
