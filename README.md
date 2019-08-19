Rubber Duck
======
Rubber Duck is a fully-featured **Discord Bot** used to aid with the administration of the [RPI Academic Discord server](https://rpi.chat/).

Duck and Cover!! Rubber Duck is more than it's quacked up to be. Waddle we do without this quackingly great ducknology. Let Rubber Duck take you under his wing. Make yourself feel vinduckated and deploy this in producktion and get your semiconducktors quacking.

## Installation and set up
```bash
$ git clone https://gitlab.com/rpi-academic-discord/slithering-duck.git
$ cd slithering-duck
$ python3 utilities/gen_config_db.py database.db
$ python3 utilities/gen_logging_db.py logging.db
```
Next, generate `config/config.json`.  An example file is visible at `config/config.json.example`.
If you'd like to add courses, they can be loaded from a json file with the following command:
```bash
$ python3 utilities/gen_config_db.py database.db [JSON FILE]
```
An example json file can be found in `config/courses.json.example`.

## Running the bot
Create a `.env` in the root directory of the project (an example file is `.env-template`) with your bot token.  Then, run the following command:
```bash
$ python3 main.py
```
You may pass in PIDs of other processes to kill them once the bot is online (eg if you want to restart the bot without downtime, you can pass the PID of the bot to another instance of it).

## Running tests
To run tests, execute the following command:
```bash
$ python3 -m unittest bot.tests -v
```

## Features
- Dynamically generate channels for topics members want to discuss
- Welcome new members to the server
- [Rubber Duck Debugging](https://wikipedia.org/wiki/Rubber_duck_debugging)
- Only allow emoji to be sent in a channel or by a user
- Render LaTeX
- Keep server logs
- Much more!

## Main Contributors
* [Eli Schiff](https://github.com/elihschiff)
* [Ben Sherman](https://gitlab.com/benjaminrsherman)

## Other
A previous iteration of the bot, written in Javascript, is available here: [https://github.com/rpi-cs-discord/Rubber-Duck](https://github.com/rpi-cs-discord/Rubber-Duck).

Rubber Duck is dedicated to SIS Man (1998-2019)

![](https://imgur.com/oc2397H.gif "SISMan")
