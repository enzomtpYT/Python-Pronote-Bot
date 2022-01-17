#ver 0.1.2
import requests, json, os, datetime, discord, time, sys
from ast import Try
from datetime import datetime as dates
from discord.ext import tasks

alt= datetime.date.today()
print(alt.weekday())

#define all variables
ajd = str(datetime.date.today())
demain = datetime.date.today()+datetime.timedelta(days=1)
preconf = open('./config.json')
config = json.load(preconf)
totimestamp = slice(10)

if os.path.isfile("./data.json"):
    data = json.load(open('./data.json'))
    print(data)
else:
    f = open("data.json", "x")
    data = {
        "UsersHomeworks":[],
        "UsersTimetables":[]
    }
    with open('data.json', 'w') as f:
        json.dump(data, f, ensure_ascii=False)
    print("created file")
    data = json.load(open('./data.json'))
    print(data)

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
    payloadquery = '{ "query": "query { timetable(from: \\"'+ajd+'\\") { teacher, room, from, to, color, subject, isCancelled } }"}'
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
    h24.start()
    async for guild in bot.fetch_guilds():
        global guilds
        guilds = []
        guilds.append(guild.id)
    return guilds

@tasks.loop(hours=24)
async def h24():
    global homechan
    global timechan
    weekend = datetime.date.today()


    timechan = bot.get_channel(int(config["timetables"]))
    if weekend.weekday() <= 4:
        await timechan.send("Voici l'emplois du temps d'aujourd'hui : ")
        for i in timetab["data"]["timetable"]:
            col = hex_to_rgb(str(i["color"]))
            #verify if there is a teacher
            if i["teacher"]:
                embedVar = discord.Embed(title=i["subject"] , description="Salle : "+i["room"]+"\nAvec : "+i["teacher"]+"\nDe : <t:"+str(i["from"])[totimestamp]+":t>\nÀ : <t:"+str(i["to"])[totimestamp]+":t>", color=discord.Color.from_rgb(col[0],col[1],col[2]))
            else:
                embedVar = discord.Embed(title=i["subject"] , description="Salle : "+i["room"]+"\nAvec :\nDe : <t:"+str(i["from"])[totimestamp]+":t>\nÀ : <t:"+str(i["to"])[totimestamp]+":t>", color=discord.Color.from_rgb(col[0],col[1],col[2]))
            await timechan.send(embed=embedVar)
    else:
        await timechan.send("Weekend !")
    

    weekendhome = datetime.date.today()+datetime.timedelta(days=1)
    homechan = bot.get_channel(int(config["homeworks"]))
    if weekendhome.weekday() <= 4:
        await homechan.send("Voici les devoirs de demain : ")
        for i in home["data"]["homeworks"]:
            col = hex_to_rgb(str(i["color"]))
            embedVar = discord.Embed(title="Pour demain en " + i["subject"], description=i["description"], color=discord.Color.from_rgb(col[0],col[1],col[2]))
            await homechan.send(embed=embedVar)
    else:
        await homechan.send("Weekend !")



    for usr in data["UsersTimetables"]:
        try:
            user = await bot.fetch_user(usr)
            if weekend.weekday() <= 4:
                await user.send("Voici l'emplois du temps d'aujourd'hui : ")
                for i in timetab["data"]["timetable"]:
                    col = hex_to_rgb(str(i["color"]))
                    #verify if there is a teacher
                    if i["teacher"]:
                        embedVar = discord.Embed(title=i["subject"] , description="Salle : "+i["room"]+"\nAvec : "+i["teacher"]+"\nDe : <t:"+str(i["from"])[totimestamp]+":t>\nÀ : <t:"+str(i["to"])[totimestamp]+":t>", color=discord.Color.from_rgb(col[0],col[1],col[2]))
                    else:
                        embedVar = discord.Embed(title=i["subject"] , description="Salle : "+i["room"]+"\nAvec :\nDe : <t:"+str(i["from"])[totimestamp]+":t>\nÀ : <t:"+str(i["to"])[totimestamp]+":t>", color=discord.Color.from_rgb(col[0],col[1],col[2]))
                    await user.send(embed=embedVar)
        except Exception as err:
            print("An error occured while sending dm to a user : {0}".format(err))
    
    for usr in data["UsersHomeworks"]:
        try:
            user = await bot.fetch_user(usr)
            if weekend.weekday() <= 4:
                await user.send("Voici les devoirs de demain : ")
                for i in home["data"]["homeworks"]:
                    col = hex_to_rgb(str(i["color"]))
                    embedVar = discord.Embed(title="Pour demain en " + i["subject"], description=i["description"], color=discord.Color.from_rgb(col[0],col[1],col[2]))
                    await user.send(embed=embedVar)
        except Exception as err:
            print("An error occured while sending dm to a user : {0}".format(err))

# on slash command "devoirs"
@bot.slash_command(guild_ids=config["guildid"])
async def devoirs(ctx):
    await ctx.respond("Voici les devoirs de demain : ")
    for i in home["data"]["homeworks"]:
        col = hex_to_rgb(str(i["color"]))
        embedVar = discord.Embed(title="Pour demain en " + i["subject"], description=i["description"], color=discord.Color.from_rgb(col[0],col[1],col[2]))
        await ctx.send(embed=embedVar)

# on slash command "emplois du temps"
@bot.slash_command(guild_ids=config["guildid"])
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
    for i in data:
        print(i)

# Add you to the list of daily Timetables
@bot.slash_command(guild_ids=config["guildid"])
async def edtdm(ctx):
    verf = 0
    for d in data["UsersTimetables"]:
        if d==ctx.author.id :
            verf += 1
    if not verf==1 :
        successful = False
        try:
            data["UsersTimetables"].append(ctx.author.id)
            with open('data.json', 'w') as f:
                json.dump(data, f, ensure_ascii=False)
            print(data)
            successful = True
        except Exception as err:
            await ctx.respond("Foirré")
            await ctx.channel.send("Erreur : \n{0}".format(err))
        if successful:
            await ctx.respond("Sucessfully added.")
    else:
        await ctx.respond("Tu est déja dans la liste !")

# Remove you from the list of daily Timetables
@bot.slash_command(guild_ids=config["guildid"])
async def edtdmremove(ctx):
    successful = False  
    try:
        for i in data["UsersTimetables"]:
            remcount = -1
            if ctx.author.id == i:
                remcount += 1
                break
            else:
                remcount += 1
        data["UsersTimetables"].pop(remcount)
        with open('data.json', 'w') as f:
            json.dump(data, f, ensure_ascii=False)
        print(data)
        successful = True
    except Exception as err:
        await ctx.respond("Foirré")
        await ctx.channel.send("Erreur : \n{0}".format(err))
    if successful:
        await ctx.respond("Sucessfully Removed.")


# Add you to the list of daily homeworks
@bot.slash_command(guild_ids=config["guildid"])
async def devoirsdm(ctx):
    verf = 0
    for d in data["UsersHomeworks"]:
        if d==ctx.author.id :
            verf += 1
    if not verf==1 :
        successful = False
        try:
            data["UsersHomeworks"].append(ctx.author.id)
            with open('data.json', 'w') as f:
                json.dump(data, f, ensure_ascii=False)
            print(data)
            successful = True
        except Exception as err:
            await ctx.respond("Foirré")
            await ctx.channel.send("Erreur : \n{0}".format(err))
        if successful:
            await ctx.respond("Sucessfully added.")
    else:
        await ctx.respond("Tu est déja dans la liste !")

# Remove you from the list of daily homeworks
@bot.slash_command(guild_ids=config["guildid"])
async def devoirsdmremove(ctx):
    successful = False  
    try:
        for i in data["UsersHomeworks"]:
            remcount = -1
            if ctx.author.id == i:
                remcount += 1
                break
            else:
                remcount += 1
        data["UsersHomeworks"].pop(remcount)
        with open('data.json', 'w') as f:
            json.dump(data, f, ensure_ascii=False)
        print(data)
        successful = True
    except Exception as err:
        await ctx.respond("Foirré")
        await ctx.channel.send("Erreur : \n{0}".format(err))
    if successful:
        await ctx.respond("Sucessfully Removed.")


# run the bot with the token in config.json
bot.run(config["discordtoken"])