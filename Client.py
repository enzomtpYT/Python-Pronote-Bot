#ver 0.1.6
from cmath import exp
import requests, json, os, datetime, discord, time, sys, asyncio
from ast import Try
from datetime import datetime as dates
from discord.ext import tasks

#define all variables
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
    ajd = str(datetime.date.today())

    try:
        token = Login()
    except:
        print("Server not running or don't have internet")

    # Pickup Infos
    urlquery = "http://127.0.0.1:21727/graphql"
    payloadquery = '{ "query": "query { timetable(from: \\"'+ajd+'\\") { teacher, room, from, to, color, subject, isCancelled } }"}'
    headersquery = {'content-type': "application/json",'token': token}
    timetables = requests.request("POST", urlquery, data=payloadquery, headers=headersquery).text

    return(timetables)

def getHomeworks():
    ajd = str(datetime.date.today())

    try:
        token = Login()
    except:
        print("Server not running or don't have internet")

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
    h24homeworks.start()
    h24timetables.start()
    async for guild in bot.fetch_guilds():
        global guilds
        guilds = []
        guilds.append(guild.id)
        return guilds



@tasks.loop(time=datetime.time(hour=7, minute=5))
async def h24timetables():
    print("Executing daily timetables")
    global timechan
    weekend = datetime.date.today()


    #Send timetables in the channel defined in config.json
    timechan = bot.get_channel(int(config["timetables"]))
    if weekend.weekday() <= 4:
        await timechan.send("Voici l'emplois du temps d'aujourd'hui : ")
        for i in timetab["data"]["timetable"]:
            col = hex_to_rgb(str(i["color"]))
            #verify if there is a teacher
            if i["teacher"]:
                if i["isCancelled"]==True:
                    embedVar = discord.Embed(title=str(i["subject"]) , description="Salle : "+str(i["room"])+"\nAvec : "+i["teacher"]+"\nEst annulé : Oui. \nDe : <t:"+str(i["from"])[totimestamp]+":t>\nÀ : <t:"+str(i["to"])[totimestamp]+":t>", color=discord.Color.from_rgb(col[0],col[1],col[2]))
                else:
                    embedVar = discord.Embed(title=str(i["subject"]) , description="Salle : "+str(i["room"])+"\nAvec : "+i["teacher"]+"\nEst annulé : Non. \nDe : <t:"+str(i["from"])[totimestamp]+":t>\nÀ : <t:"+str(i["to"])[totimestamp]+":t>", color=discord.Color.from_rgb(col[0],col[1],col[2]))
            else:
                if i["isCancelled"]==True:
                    embedVar = discord.Embed(title=str(i["subject"]) , description="Salle : "+str(i["room"])+"\nAvec :\nEst annulé : Oui. \nDe : <t:"+str(i["from"])[totimestamp]+":t>\nÀ : <t:"+str(i["to"])[totimestamp]+":t>", color=discord.Color.from_rgb(col[0],col[1],col[2]))
                else:
                    embedVar = discord.Embed(title=str(i["subject"]) , description="Salle : "+str(i["room"])+"\nAvec :\nEst annulé : Non. \nDe : <t:"+str(i["from"])[totimestamp]+":t>\nÀ : <t:"+str(i["to"])[totimestamp]+":t>", color=discord.Color.from_rgb(col[0],col[1],col[2]))
            await timechan.send(embed=embedVar)
    else:
        await timechan.send("Weekend !")


    #Send timetables to everyone who is in the list
    print("Sending daily Timetables to : ")
    for usr in data["UsersTimetables"]:
        try:
            user = await bot.fetch_user(usr)
            print(user)
            if weekend.weekday() <= 4:
                await user.send("Voici l'emplois du temps d'aujourd'hui : ")
                for i in timetab["data"]["timetable"]:
                    col = hex_to_rgb(str(i["color"]))
                    #verify if there is a teacher
                    if i["teacher"]:
                        if i["isCancelled"]==True:
                            embedVar = discord.Embed(title=str(i["subject"]) , description="Salle : "+str(i["room"])+"\nAvec : "+i["teacher"]+"\nEst annulé : Oui. \nDe : <t:"+str(i["from"])[totimestamp]+":t>\nÀ : <t:"+str(i["to"])[totimestamp]+":t>", color=discord.Color.from_rgb(col[0],col[1],col[2]))
                        else:
                            embedVar = discord.Embed(title=str(i["subject"]) , description="Salle : "+str(i["room"])+"\nAvec : "+i["teacher"]+"\nEst annulé : Non. \nDe : <t:"+str(i["from"])[totimestamp]+":t>\nÀ : <t:"+str(i["to"])[totimestamp]+":t>", color=discord.Color.from_rgb(col[0],col[1],col[2]))
                    else:
                        if i["isCancelled"]==True:
                            embedVar = discord.Embed(title=str(i["subject"]) , description="Salle : "+str(i["room"])+"\nAvec :\nEst annulé : Oui. \nDe : <t:"+str(i["from"])[totimestamp]+":t>\nÀ : <t:"+str(i["to"])[totimestamp]+":t>", color=discord.Color.from_rgb(col[0],col[1],col[2]))
                        else:
                            embedVar = discord.Embed(title=str(i["subject"]) , description="Salle : "+str(i["room"])+"\nAvec :\nEst annulé : Non. \nDe : <t:"+str(i["from"])[totimestamp]+":t>\nÀ : <t:"+str(i["to"])[totimestamp]+":t>", color=discord.Color.from_rgb(col[0],col[1],col[2]))
                    await user.send(embed=embedVar)
        except Exception as err:
            print("An error occured while sending dm to a user : {0}".format(err))


@tasks.loop(time=datetime.time(hour=15, minute=30))
async def h24homeworks():
    print("Executing daily homeworks")
    global homechan
    weekend = datetime.date.today()


    #Send homeworks in the channel defined in config.json
    weekendhome = datetime.date.today()+datetime.timedelta(days=1)
    homechan = bot.get_channel(int(config["homeworks"]))
    if weekendhome.weekday() <= 4:
        await homechan.send("Voici les devoirs de demain : ")
        for i in home["data"]["homeworks"]:
            col = hex_to_rgb(str(i["color"]))
            embedVar = discord.Embed(title="Pour demain en " + str(i["subject"]), description=i["description"], color=discord.Color.from_rgb(col[0],col[1],col[2]))
            await homechan.send(embed=embedVar)
    else:
        await homechan.send("Weekend !")


    # Send homeworks to every users who is in the list
    print("Sending daily Homeworks to : ")
    for usr in data["UsersHomeworks"]:
        try:
            user = await bot.fetch_user(usr)
            print(user)
            if weekend.weekday() <= 4:
                await user.send("Voici les devoirs de demain : ")
                for i in home["data"]["homeworks"]:
                    col = hex_to_rgb(str(i["color"]))
                    embedVar = discord.Embed(title="Pour demain en " + str(i["subject"]), description=i["description"], color=discord.Color.from_rgb(col[0],col[1],col[2]))
                    await user.send(embed=embedVar)
        except Exception as err:
            print("An error occured while sending dm to a user : {0}".format(err))



# on slash command "devoirs"
@bot.slash_command(guild_ids=config["guildid"])
async def devoirs(ctx):
    print(str(ctx.author) + " Executed \"devoirs\"")
    await ctx.respond("Voici les devoirs de demain : ")
    for i in home["data"]["homeworks"]:
        col = hex_to_rgb(str(i["color"]))
        embedVar = discord.Embed(title="Pour demain en " + str(i["subject"]), description=i["description"], color=discord.Color.from_rgb(col[0],col[1],col[2]))
        await ctx.send(embed=embedVar)

# on slash command "emplois du temps"
@bot.slash_command(guild_ids=config["guildid"])
async def edt(ctx):
    print(str(ctx.author) + " Executed \"edt\"")
    await ctx.respond("Voici l'emplois du temps d'aujourd'hui : ")
    for i in timetab["data"]["timetable"]:
        col = hex_to_rgb(str(i["color"]))
        #verify if there is a teacher
        if i["teacher"]:
            if i["isCancelled"]==True:
                embedVar = discord.Embed(title=str(i["subject"]) , description="Salle : "+str(i["room"])+"\nAvec : "+i["teacher"]+"\nEst annulé : Oui. \nDe : <t:"+str(i["from"])[totimestamp]+":t>\nÀ : <t:"+str(i["to"])[totimestamp]+":t>", color=discord.Color.from_rgb(col[0],col[1],col[2]))
            else:
                embedVar = discord.Embed(title=str(i["subject"]) , description="Salle : "+str(i["room"])+"\nAvec : "+i["teacher"]+"\nEst annulé : Non. \nDe : <t:"+str(i["from"])[totimestamp]+":t>\nÀ : <t:"+str(i["to"])[totimestamp]+":t>", color=discord.Color.from_rgb(col[0],col[1],col[2]))
        else:
            if i["isCancelled"]==True:
                embedVar = discord.Embed(title=str(i["subject"]) , description="Salle : "+str(i["room"])+"\nAvec :\nEst annulé : Oui. \nDe : <t:"+str(i["from"])[totimestamp]+":t>\nÀ : <t:"+str(i["to"])[totimestamp]+":t>", color=discord.Color.from_rgb(col[0],col[1],col[2]))
            else:
                embedVar = discord.Embed(title=str(i["subject"]) , description="Salle : "+str(i["room"])+"\nAvec :\nEst annulé : Non. \nDe : <t:"+str(i["from"])[totimestamp]+":t>\nÀ : <t:"+str(i["to"])[totimestamp]+":t>", color=discord.Color.from_rgb(col[0],col[1],col[2]))
        await ctx.send(embed=embedVar)

# Add you to the list of daily Timetables
@bot.slash_command(guild_ids=config["guildid"])
async def edtdm(ctx):
    print(str(ctx.author) + " Executed \"edtdm\"")
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
    print(str(ctx.author) + " Executed \"edtdmremove\"")
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
    print(str(ctx.author) + " Executed \"devoirsdm\"")
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
    print(str(ctx.author) + " Executed \"devoirsdmremove\"")
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
try:
    bot.run(config["discordtoken"])
except:
    print("Bot a planté")

# bot.run(config["discordtoken"])