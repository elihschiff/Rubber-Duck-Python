#!/bin/sh

git pull

pip3 install -r requirements.txt

nohup python3 main.py $(pidof python3) &
