#!/bin/sh

nohup python3 main.py $(pidof python3) > /dev/null 2> /dev/null < /dev/null &
