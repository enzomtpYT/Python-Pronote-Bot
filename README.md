
# Python-Pronote-Bot

  

Python-Pronote-Bot is a discord bot that fetch Pronote infos (like homeworks and timetables)

  

## Installation

You will need a local [Pronote Api Server](https://github.com/enzomtpYT/pronote-api) to use the bot

Using git :

  

```bash

git clone https://github.com/enzomtpYT/Python-Pronote-Bot.git

```

  

## Usage



### Configure the bot


  In config.json

```json

{

"pronoteurl": "Insert Your Pronote URL",

"username": "Your pronote username",

"password": "Your pronote password",

"discordtoken": "Your Discord Bot Token",

"homeworks": "Channel for the homeworks"

}

```

### Start the bot

  In the bot folder open a terminal and do :
  
  On windows :
```batch
py Client.py
```

On linux :
```batch
python3 Client.py
```

### Use the bot
Commands :

 - [x] Timetables ( With cancelled classes )
 - [x] Homeworks
 
 Auto messages (DM or Channel) :
 
 - [x] Timetables ( With cancelled classes ) every morning
 - [x] Homeworks every afternoon

## License

[MIT](https://choosealicense.com/licenses/mit/)