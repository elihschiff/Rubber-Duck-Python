#!/bin/sh

git pull

pip3 install -r requirements.txt

nohup python3 main.py $(pidof python3) > /dev/null 2> /dev/null < /dev/null &
