#!/bin/sh

cp config/quacks.txt.example config/quacks.txt
cp config/games.txt.example config/games.txt

pip3 install -r requirements.txt

./restart.sh
