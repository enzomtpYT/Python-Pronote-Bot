
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
    "pronoteurl": "YOUR_PRONOTE_URL",
    "discord": {
        "discordtoken": "YOUR_DISCORD_TOKEN",
        "guildid": [YOUR_GUILD_ID],
        "sendmenu": true,
        "menuchannel": "CHANNEL_TO_SEND_MENU"
    },
    "group": {
        "1": {
            "username": "USERNAME_FOR_GROUP1",
            "password": "PASSWORD_FOR_GROUP1",
            "homeworks": "CHANNEL_TO_SEND_HOMEWORKS_FOR_GROUP1",
            "timetables": "CHANNEL_TO_SEND_TIMETABLES_FOR_GROUP1"
        },
        "2": {
            "username": "USERNAME_FOR_GROUP2",
            "password": "PASSWORD_FOR_GROUP2",
            "homeworks": "CHANNEL_TO_SEND_HOMEWORKS_FOR_GROUP2",
            "timetables": "CHANNEL_TO_SEND_TIMETABLES_FOR_GROUP2"
        }
    }
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

[MIT](https://pastebin.com/raw/21JuM9kU)
