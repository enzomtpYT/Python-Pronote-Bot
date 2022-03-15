# Ver 0.2.0
# Credits to enzomtp
from cmath import exp
import requests, json, os, datetime, discord
from ast import Try
from discord.ext import tasks

print("Python Pronote Bot  V0.2.0 by enzomtp")

# Define all variables
preconf = open('./config.json')
config = json.load(preconf)
totimestamp = slice(10)



# Verify, Create, Read the data.json
if os.path.isfile("./data.json"):
    data = json.load(open('./data.json'))
    print(data)
else:
    f = open("data.json", "x")
    data = {
        "UsersHomeworks1":[],
        "UsersTimetables1":[],
        "UsersHomeworks2":[],
        "UsersTimetables2":[]
    }
    with open('data.json', 'w') as f:
        json.dump(data, f, ensure_ascii=False)
    print("created file")
    data = json.load(open('./data.json'))
    print(data)




# A hex to rgb function
def hex_to_rgb(value):
    value = value.lstrip('#')
    lv = len(value)
    return tuple(int(value[i:i + lv // 3], 16) for i in range(0, lv, lv // 3))




# Login in the api
def Login(grp):
    print("Logging in as group "+grp)

    # Login
    urlogin = "http://127.0.0.1:21727/auth/login"
    payloadlogin = '{"url": "'+config["pronoteurl"]+'","username":"'+config["group"][str(grp)]["username"]+'","password":"'+config["group"][str(grp)]["password"]+'"}'
    headerslogin = {'content-type': "application/json"}
    tokenjson = json.loads(requests.request("POST", urlogin, data=payloadlogin, headers=headerslogin).text)

    token = tokenjson["token"]

    return token




# Get Timetables from the api
def getTimetables(grp):
    ajd = str(datetime.date.today())
    print("Getting Timetables as "+grp)

    try:
        token = Login(grp)
    except:
        print("Server not running or don't have internet")

    # Pickup Infos
    urlquery = "http://127.0.0.1:21727/graphql"
    payloadquery = '{ "query": "query { timetable(from: \\"'+ajd+'\\") { teacher, room, from, to, color, subject, isCancelled } }"}'
    headersquery = {'content-type': "application/json",'token': token}
    timetables = requests.request("POST", urlquery, data=payloadquery, headers=headersquery).text
    print("Parsed json for Timetables : \n"+str(timetables))

    return(timetables)




# Get Homeworks from the api
def getHomeworks(grp):
    ajd = str(datetime.date.today())
    print("Getting Homeworks as "+grp)

    try:
        token = Login(grp)
    except:
        print("Server not running or don't have internet")

    # Pickup Infos
    urlquery = "http://127.0.0.1:21727/graphql"
    payloadquery = '{ "query": "query { homeworks(from: \\"'+ajd+'\\") { description, subject, color } }"}'
    headersquery = {'content-type': "application/json",'token': token}
    homeworks = requests.request("POST", urlquery, data=payloadquery, headers=headersquery).text
    print("Parsed json for homeworks : \n"+str(homeworks))
    
    return(homeworks)




global home
global timetab

# Init bot
bot = discord.Bot()

# On bot ready
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




# Schedule the daily Timetables task
@tasks.loop(time=datetime.time(hour=7, minute=5))
async def h24timetables():
    for a in range(1,3):
        timetab = json.loads(getTimetables(str(a)))
        print("Executing daily timetables")
        global timechan
        weekend = datetime.date.today()


        #Send timetables in the channel defined in config.json
        timechan = bot.get_channel(int(config["group"][str(a)]["timetables"]))
        if weekend.weekday() <= 4:
            await timechan.send("Voici l'emplois du temps d'aujourd'hui : ")
            for i in timetab["data"]["timetable"]:
                col = hex_to_rgb(str(i["color"]))
                # Verify if there is a teacher
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


        # Send timetables to everyone who is in the list
        print("Sending daily Timetables to : ")
        for usr in data["UsersTimetables"+str(a)]:
            try:
                user = await bot.fetch_user(usr)
                print(user)
                if weekend.weekday() <= 4:
                    await user.send("Voici l'emplois du temps d'aujourd'hui : ")
                    for i in timetab["data"]["timetable"]:
                        col = hex_to_rgb(str(i["color"]))
                        # Verify if there is a teacher
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




# Schedule the daily Homeworks task
@tasks.loop(time=datetime.time(hour=15, minute=30))
async def h24homeworks():
    for a in range(1,3):
        home = json.loads(getHomeworks(a))
        print("Executing daily homeworks")
        global homechan
        weekend = datetime.date.today()


        #Send homeworks in the channel defined in config.json
        weekendhome = datetime.date.today()+datetime.timedelta(days=1)
        homechan = bot.get_channel(int(config["group"][a]["homeworks"]))
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
        for usr in data["UsersHomeworks"+str(a)]:
            try:
                user = await bot.fetch_user(usr)
                print(user)
                if weekendhome.weekday() <= 4:
                    await user.send("Voici les devoirs de demain : ")
                    for i in home["data"]["homeworks"]:
                        col = hex_to_rgb(str(i["color"]))
                        embedVar = discord.Embed(title="Pour demain en " + str(i["subject"]), description=i["description"], color=discord.Color.from_rgb(col[0],col[1],col[2]))
                        await user.send(embed=embedVar)
            except Exception as err:
                print("An error occured while sending dm to a user : {0}".format(err))




# On slash command "devoirs"
@bot.slash_command(guild_ids=config["discord"]["guildid"])
async def devoirs(
    ctx, 
    group: discord.Option(int, "Enter your group", min_value=1, max_value=2, default=1)
    ):
    home = json.loads(getHomeworks(group))
    print(str(ctx.author) + " Executed \"devoirs\"")
    await ctx.respond("Voici les devoirs de demain : ")
    for i in home["data"]["homeworks"]:
        col = hex_to_rgb(str(i["color"]))
        embedVar = discord.Embed(title="Pour demain en " + str(i["subject"]), description=i["description"], color=discord.Color.from_rgb(col[0],col[1],col[2]))
        await ctx.send(embed=embedVar)




# On slash command "emplois du temps"
@bot.slash_command(guild_ids=config["discord"]["guildid"])
async def edt(
    ctx, 
    group: discord.Option(int, "Enter your group", min_value=1, max_value=2, default=1)
    ):
    timetab = json.loads(getTimetables(str(group)))
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
@bot.slash_command(guild_ids=config["discord"]["guildid"])
async def edtdm(
    ctx, 
    group: discord.Option(int, "Enter your group", min_value=1, max_value=2, default=1)
    ):
    print(str(ctx.author) + " Executed \"edtdm\"")
    verf = 0
    for d in data["UsersTimetables"+str(group)]:
        if d==ctx.author.id :
            verf += 1
    if not verf==1 :
        successful = False
        try:
            data["UsersTimetables"+str(group)].append(ctx.author.id)
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
@bot.slash_command(guild_ids=config["discord"]["guildid"])
async def edtdmremove(
    ctx, 
    group: discord.Option(int, "Enter your group", min_value=1, max_value=2, default=1)
    ):
    print(str(ctx.author) + " Executed \"edtdmremove\"")
    successful = False  
    try:
        for i in data["UsersTimetables"+str(group)]:
            remcount = -1
            if ctx.author.id == i:
                remcount += 1
                break
            else:
                remcount += 1
        data["UsersTimetables"+str(group)].pop(remcount)
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
@bot.slash_command(guild_ids=config["discord"]["guildid"])
async def devoirsdm(
    ctx, 
    group: discord.Option(int, "Enter your group", min_value=1, max_value=2, default=1)
    ):
    print(str(ctx.author) + " Executed \"devoirsdm\"")
    verf = 0
    for d in data["UsersHomeworks"+str(group)]:
        if d==ctx.author.id :
            verf += 1
    if not verf==1 :
        successful = False
        try:
            data["UsersHomeworks"+str(group)].append(ctx.author.id)
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
@bot.slash_command(guild_ids=config["discord"]["guildid"])
async def devoirsdmremove(
    ctx, 
    group: discord.Option(int, "Enter your group", min_value=1, max_value=2, default=1)
    ):
    print(str(ctx.author) + " Executed \"devoirsdmremove\"")
    successful = False  
    try:
        for i in data["UsersHomeworks"+str(group)]:
            remcount = -1
            if ctx.author.id == i:
                remcount += 1
                break
            else:
                remcount += 1
        data["UsersHomeworks"+str(group)].pop(remcount)
        with open('data.json', 'w') as f:
            json.dump(data, f, ensure_ascii=False)
        print(data)
        successful = True
    except Exception as err:
        await ctx.respond("Foirré")
        await ctx.channel.send("Erreur : \n{0}".format(err))
    if successful:
        await ctx.respond("Sucessfully Removed.")




# Run the bot with the token in config.json
bot.run(config["discord"]["discordtoken"])