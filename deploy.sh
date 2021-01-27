#!/bin/sh

cp config/quacks.txt.example config/quacks.txt
cp config/games.txt.example config/games.txt

python3.6 -m pip install -r requirements.txt

./restart.sh
