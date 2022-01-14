import requests
import json
import datetime
from datetime import datetime as dates
import discord
import time
from discord.ext import tasks

#define all variables
ajd = str(datetime.date.today())
demain = datetime.date.today()+datetime.timedelta(days=1)
preconf = open('./config.json')
config = json.load(preconf)
homechanconf = int(config["homeworks"])
totimestamp = slice(10)

def hex_to_rgb(value):
    value = value.lstrip('#')
    lv = len(value)
    return tuple(int(value[i:i + lv // 3], 16) for i in range(0, lv, lv // 3))

def Login():

    # login
    urlogin = "http://127.0.0.1:21727/auth/login"
    payloadlogin = '{"url": "'+config["pronoteurl"]+'","username":"'+config["username"]+'","password":"'+config["password"]+'"}'
    headerslogin = {'content-type': "application/json"}
    tokenjson = json.loads(requests.request("POST", urlogin, data=payloadlogin, headers=headerslogin).text)

    token = tokenjson["token"]

    return token

def getTimetables():

    token = Login()

    # Pickup Infos
    urlquery = "http://127.0.0.1:21727/graphql"
    payloadquery = '{ "query": "query { timetable(from: \\"'+ajd+'\\") { teacher, room, from, to, color, subject } }"}'
    headersquery = {'content-type': "application/json",'token': token}
    timetables = requests.request("POST", urlquery, data=payloadquery, headers=headersquery).text

    return(timetables)

def getHomeworks():

    token = Login()

    # Pickup Infos
    urlquery = "http://127.0.0.1:21727/graphql"
    payloadquery = '{ "query": "query { homeworks(from: \\"'+ajd+'\\") { description, subject, color } }"}'
    headersquery = {'content-type': "application/json",'token': token}
    homeworks = requests.request("POST", urlquery, data=payloadquery, headers=headersquery).text
    
    return(homeworks)

global home
global timetab
home = json.loads(getHomeworks())
timetab = json.loads(getTimetables())

# init bot
bot = discord.Bot()

# on bot ready
@bot.event
async def on_ready():
    print(f"We have logged in as {bot.user}")
    hb.start()
    async for guild in bot.fetch_guilds():
        global guilds
        guilds = []
        guilds.append(guild.id)
    return guilds

@tasks.loop(hours=24)
async def hb():
    a = "a"

# on slash command "devoirs"
@bot.slash_command(guild_ids=[481828231763329024])
async def devoirs(ctx):
    await ctx.respond("Voici les devoirs de demain : ")
    for i in home["data"]["homeworks"]:
        col = hex_to_rgb(str(i["color"]))
        embedVar = discord.Embed(title="Pour demain en " + i["subject"], description=i["description"], color=discord.Color.from_rgb(col[0],col[1],col[2]))
        await ctx.send(embed=embedVar)

# on slash command "emplois du temps"
@bot.slash_command(guild_ids=[481828231763329024])
async def edt(ctx):
    await ctx.respond("Voici l'emplois du temps d'aujourd'hui : ")
    for i in timetab["data"]["timetable"]:
        col = hex_to_rgb(str(i["color"]))
        #verify if there is a teacher
        if i["teacher"]:
            embedVar = discord.Embed(title=i["subject"] , description="Salle : "+i["room"]+"\nAvec : "+i["teacher"]+"\nDe : <t:"+str(i["from"])[totimestamp]+":t>\nÀ : <t:"+str(i["to"])[totimestamp]+":t>", color=discord.Color.from_rgb(col[0],col[1],col[2]))
        else:
            embedVar = discord.Embed(title=i["subject"] , description="Salle : "+i["room"]+"\nAvec :\nDe : <t:"+str(i["from"])[totimestamp]+":t>\nÀ : <t:"+str(i["to"])[totimestamp]+":t>", color=discord.Color.from_rgb(col[0],col[1],col[2]))
        await ctx.send(embed=embedVar)

# run the bot with the token in config.json
bot.run(config["discordtoken"])