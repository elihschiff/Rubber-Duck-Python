#!/bin/sh

# validate messages config
required_messages=$(grep -rPoh '\.messages\[".+?"\]' bot/ | sed -e 's/^\.messages\["/"/g' -e 's/"]$/"/g' | sort | uniq | xargs)
python3 utilities/validate_messages.py "config/messages.json" $required_messages || exit 1

nohup python3.6 main.py $(pidof python3.6) >/dev/null 2>/dev/null </dev/null &
