
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
    
    "username": "YOUR_USERNAME",
    
    "password": "YOUR PASSWORD",
    
    "discordtoken": "YOUR_DISCORD_BOT_TOKEN",
    
    "homeworks": "DISCORD_CHANNEL_FOR_HOMEWORKS",
    
    "timetables": "DISCORD_CHANNEL_FOR_TIMETABLES",
    
    "guildid": [YOUR_GUILD_ID]
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
