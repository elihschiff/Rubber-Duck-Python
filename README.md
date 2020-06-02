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
Next, generate all the different config JSON files.  Example files are visible in the config folder with the name `config/FILE_NAME.json.example`.
```bash
$ cp config/config.json.example config/config.json
$ cp config/messages.json.example config/messages.json
$ cp config/quacks.txt.example config/quacks.txt
$ cp config/courses.json.example config/courses.json
$ cp config/games.txt.example config/games.txt
$ cp config/roles.txt.example config/roles.txt
```
While most of the json files should work out of the box, `config.json` must be filled out or the bot may crash while running.

If you'd like to add courses, they can be loaded from a json file with the following command:
```bash
$ python3 utilities/gen_config_db.py database.db [JSON FILE]
```
An example JSON file can be found in `config/courses.json`.

The last step is to install all the pip dependencies
```bash
$ sudo pip3 install -r requirements.txt
```

## Running the bot
Create a `.env` in the root directory of the project (an example file is `.env.example`)
```bash
$ cp .env.example .env
```
 Add your bot token to the .env file. To learn how to create a bot token see the **Discord Server and Bot Setup** section

 To start the bot run:
```bash
$ python3 main.py
```
You may also pass in PIDs of other processes to kill them once the bot is online (eg if you want to restart the bot without downtime, you can pass the PID of the bot to another instance of it).

## Running tests
To run tests, execute the following command:
```bash
$ python3 -m unittest bot.tests -v
```

All the code is also formatted using the [Python Black Code Formatter](https://pypi.org/project/black/). Please make sure to format your code before making a pull request.

## Discord Server and Bot Setup

### Making a Discord bot
To make a new discord bot go to the [Discord Applications](https://discordapp.com/developers/applications/) page and click `New Application`

Give your new bot a name, for example `Rubber Duck`. Then click `create`

Click `Bot` on the left sidebar and then `Add Bot` followed by `Yes, do it!`

You will now see a `Copy` button under the `Token` section. Click `Copy` and add that token to your .env file

### Making a Discord Server

At the very bottom of the left sidebar in Discord click the `+` button followed by `Create a server`

Give your server a name and then click `Create`

Now that you have your server you are ready to fill out your config.json file. This will require you to make a few roles, channels, and categories. When you right click on anything in Discord you should see a `Copy ID` button. If you dont go to `User Settings>Appearance>Developer Mode` and make sure the switch is on.

### Inviting your bot to a Discord server

Open your bot's page found withing the [Discord Applications](https://discordapp.com/developers/applications/) page

On the left sidebar of your bot click `OAuth2`

Then click the `Bot` checkbox and scroll down to click the `Administrator` checkbox.

Finally go to the url on the page and add the bot to the correct server.


## Features
- Dynamically generate channels for topics members want to discuss
- Welcome new members to the server
- [Rubber Duck Debugging](https://wikipedia.org/wiki/Rubber_duck_debugging)
- Only allow emoji to be sent in a channel or by a user
- Render LaTeX
- Keep server logs
- Search Linux man pages
- Search Wikipedia
- Much more!

## Main Contributors
* [Eli Schiff](https://github.com/elihschiff)
* [Ben Sherman](https://gitlab.com/benjaminrsherman)

## Other
A previous iteration of the bot, written in Javascript, is available here: [https://github.com/rpi-cs-discord/Rubber-Duck](https://github.com/rpi-cs-discord/Rubber-Duck).

Rubber Duck is dedicated to SIS Man (1998-2019)

![](https://imgur.com/oc2397H.gif "SISMan")
