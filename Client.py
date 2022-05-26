# Ver 0.2.8
# Credits to enzomtp
import requests, json, os, datetime, discord, pytz
from discord.ext import tasks

print("Python Pronote Bot V0.2.8 by enzomtp")

# Define all variables
preconf = open('./config.json')
config = json.load(preconf)
totimestamp = slice(10)
utc = pytz.utc
now=datetime.datetime.now()
FRTZ = pytz.timezone('Europe/Paris')

def ToUtcHour(h):
    return int(FRTZ.localize(datetime.datetime(int(now.strftime('%Y')), int(now.strftime('%m')), int(now.strftime('%d')), h, 12, 0)).astimezone(utc).strftime('%H'))
def ToUtcMin(m):
    return int(FRTZ.localize(datetime.datetime(int(now.strftime('%Y')), int(now.strftime('%m')), int(now.strftime('%d')), 12, m, 0)).astimezone(utc).strftime('%M'))


# Verify, Create and Read the data.json
if os.path.isfile("./data.json"):
    data = json.load(open('./data.json'))
    print(data)
else:
    f = open("data.json", "x")
    data = {
        "UsersHomeworks1":[],
        "UsersTimetables1":[],
        "UsersHomeworks2":[],
        "UsersTimetables2":[],
        "Menu":[]
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
    print("Logging in as group "+config["group"][str(grp)]["username"])

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
    print("Getting Timetables as group "+config["group"][str(grp)]["username"])

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
    print("Getting Homeworks as group "+config["group"][str(grp)]["username"])

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

# Get Menu from the api
def getMenu():
    ajdm = str(datetime.date.today()-datetime.timedelta(days=1))
    print("Getting Menu as "+config["group"]["2"]["username"])

    try:
        token = Login("2")
    except:
        print("Server not running or don't have internet")

    # Pickup Infos
    urlquery = "http://127.0.0.1:21727/graphql"
    payloadquery = '{ "query": "query { menu(from: \\"'+ajdm+'\\") { meals { name } } }"}'
    headersquery = {'content-type': "application/json",'token': token}
    timetables = requests.request("POST", urlquery, data=payloadquery, headers=headersquery).text
    print("Parsed json for Menu : \n"+str(timetables))

    return(timetables)



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
    h24menu.start()
    async for guild in bot.fetch_guilds():
        global guilds
        guilds = []
        guilds.append(guild.id)
        return guilds




# Schedule the daily Timetables task
@tasks.loop(time=datetime.time(hour=ToUtcHour(7), minute=ToUtcMin(55)))
async def h24timetables():
    for a in range(1,3):
        print("Executing daily timetables")
        global timechan
        weekend = datetime.date.today()

        timetab = json.loads(getTimetables(str(a)))
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
        print("Sending daily Timetables for group "+str(a)+" : ")
        for usr in data["UsersTimetables"+str(a)]:
            try:
                user = await bot.fetch_user(usr)
                print(user)
                if weekend.weekday() <= 4:
                    await user.send("Voici l'emplois du temps d'aujourd'hui pour le **groupe "+str(a)+"** : ")
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
@tasks.loop(time=datetime.time(hour=ToUtcHour(15), minute=ToUtcMin(55)))
async def h24homeworks():
    for a in range(1,3):
        print("Executing daily homeworks")
        global homechan

        home = json.loads(getHomeworks(str(a)))
        #Send homeworks in the channel defined in config.json
        weekendhome = datetime.date.today()+datetime.timedelta(days=1)
        homechan = bot.get_channel(int(config["group"][str(a)]["homeworks"]))
        if weekendhome.weekday() <= 4:
            await homechan.send("Voici les devoirs de demain : ")
            for i in home["data"]["homeworks"]:
                col = hex_to_rgb(str(i["color"]))
                embedVar = discord.Embed(title="Pour demain en " + str(i["subject"]), description=i["description"], color=discord.Color.from_rgb(col[0],col[1],col[2]))
                await homechan.send(embed=embedVar)
        else:
            await homechan.send("Weekend !")


        # Send homeworks to every users who is in the list
        print("Sending daily Homeworks for group "+str(a)+" : ")
        for usr in data["UsersHomeworks"+str(a)]:
            try:
                user = await bot.fetch_user(usr)
                print(user)
                if weekendhome.weekday() <= 4:
                    await user.send("Voici les devoirs de demain pour le **groupe "+str(a)+"** : ")
                    for i in home["data"]["homeworks"]:
                        col = hex_to_rgb(str(i["color"]))
                        embedVar = discord.Embed(title="Pour demain en " + str(i["subject"]), description=i["description"], color=discord.Color.from_rgb(col[0],col[1],col[2]))
                        await user.send(embed=embedVar)
            except Exception as err:
                print("An error occured while sending dm to a user : {0}".format(err))




# Schedule the daily Menu task
@tasks.loop(time=datetime.time(hour=ToUtcHour(7), minute=ToUtcMin(55)))
async def h24menu():
    menu = json.loads(str(getMenu()))
    print("Executing daily menu")
    global menuchan
    weekend = datetime.date.today()
    #Send menu in the channel defined in config.json
    if config["discord"]["sendmenu"] == True:
        menuchan = bot.get_channel(int(config["discord"]["menuchannel"]))
        if weekend.weekday() <= 4:
                await menuchan.send("Voici le menu d'aujourd'hui : ")
                menuindex = 0
                entree = ""
                viandes = ""
                acomp = ""
                laits = ""
                desserts = ""
                for i in menu["data"]["menu"][0]["meals"][0]:
                    for a in i:
                        if menuindex == 0:
                            entree = entree + a["name"]+"\n"
                        elif menuindex == 1:
                            viandes = viandes + a["name"]+"\n"
                        elif menuindex == 2:
                            acomp = acomp + a["name"]+"\n"
                        elif menuindex == 3:
                            laits = laits + a["name"]+"\n"
                        elif menuindex == 4:
                            desserts = desserts + a["name"]+"\n"
                    menuindex += 1
                embedVar = discord.Embed(title="Le menu d'ajourd'hui est composé de :", description=" ", color=0xff3950)
                embedVar.insert_field_at(index=0, name="Entrée", value=entree, inline=False)
                embedVar.insert_field_at(index=1, name="Viandes", value=viandes, inline=False)
                embedVar.insert_field_at(index=2, name="Acompagnements", value=acomp, inline=False)
                embedVar.insert_field_at(index=3, name="Laitages", value=laits, inline=False)
                embedVar.insert_field_at(index=4, name="Desserts", value=desserts, inline=False)
                await menuchan.send(embed=embedVar)
        else:
            await timechan.send("Weekend !")


    # Send menu to everyone who is in the list
    print("Sending daily Menu to : ")
    for usr in data["Menu"]:
        try:
            user = await bot.fetch_user(usr)
            print(user)
            if weekend.weekday() <= 4:
                await user.send("Voici le menu d'aujourd'hui : ")
                menuindex = 0
                entree = ""
                viandes = ""
                acomp = ""
                laits = ""
                desserts = ""
                for i in menu["data"]["menu"][0]["meals"][0]:
                    for a in i:
                        if menuindex == 0:
                            entree = entree + a["name"]+"\n"
                        elif menuindex == 1:
                            viandes = viandes + a["name"]+"\n"
                        elif menuindex == 2:
                            acomp = acomp + a["name"]+"\n"
                        elif menuindex == 3:
                            laits = laits + a["name"]+"\n"
                        elif menuindex == 4:
                            desserts = desserts + a["name"]+"\n"
                    menuindex += 1
                embedVar = discord.Embed(title="Le menu d'ajourd'hui est composé de :", description=" ", color=0xff3950)
                embedVar.insert_field_at(index=0, name="Entrée", value=entree, inline=False)
                embedVar.insert_field_at(index=1, name="Viandes", value=viandes, inline=False)
                embedVar.insert_field_at(index=2, name="Acompagnements", value=acomp, inline=False)
                embedVar.insert_field_at(index=3, name="Laitages", value=laits, inline=False)
                embedVar.insert_field_at(index=4, name="Desserts", value=desserts, inline=False)
                await user.send(embed=embedVar)
        except Exception as err:
            print("An error occured while sending dm to a user : {0}".format(err))




# On slash command "menu"
@bot.slash_command(guild_ids=config["discord"]["guildid"], description="Envoye le menu dans ce channel")
async def menu(ctx):
    menu = json.loads(getMenu())
    print(str(ctx.author) + " Executed \"menu\"")
    try:
        await ctx.respond("Voici le menu d'aujourd'hui : ")
    except:
        print("Discord Response Timed Out !")
        await ctx.send("Discord Response Timed Out !")
    menuindex = 0
    entree = ""
    viandes = ""
    acomp = ""
    laits = ""
    desserts = ""
    for i in menu["data"]["menu"][0]["meals"][0]:
        for a in i:
            if menuindex == 0:
                entree = entree + a["name"]+"\n"
            elif menuindex == 1:
                viandes = viandes + a["name"]+"\n"
            elif menuindex == 2:
                acomp = acomp + a["name"]+"\n"
            elif menuindex == 3:
                laits = laits + a["name"]+"\n"
            elif menuindex == 4:
                desserts = desserts + a["name"]+"\n"
        menuindex += 1
    embedVar = discord.Embed(title="Le menu d'ajourd'hui est composé de :", description=" ", color=0xff3950)
    embedVar.insert_field_at(index=0, name="Entrée", value=entree, inline=False)
    embedVar.insert_field_at(index=1, name="Viandes", value=viandes, inline=False)
    embedVar.insert_field_at(index=2, name="Acompagnements", value=acomp, inline=False)
    embedVar.insert_field_at(index=3, name="Laitages", value=laits, inline=False)
    embedVar.insert_field_at(index=4, name="Desserts", value=desserts, inline=False)
    print("Entrée : \n" + entree + "\nViandes : \n" + viandes)
    await ctx.send(embed=embedVar)



# On slash command "devoirs"
@bot.slash_command(guild_ids=config["discord"]["guildid"], description="Envoye les devoirs dans ce channel")
async def devoirs(
    ctx, 
    group: discord.Option(int, "Enter your group", min_value=1, max_value=2, default=1)
    ):
    home = json.loads(getHomeworks(group))
    print(str(ctx.author) + " Executed \"devoirs\"")
    try:
        await ctx.respond("Voici les devoirs de demain : ")
    except:
        print("Discord Response Timed Out !")
        await ctx.send("Discord Response Timed Out !")
    for i in home["data"]["homeworks"]:
        col = hex_to_rgb(str(i["color"]))
        embedVar = discord.Embed(title="Pour demain en " + str(i["subject"]), description=i["description"], color=discord.Color.from_rgb(col[0],col[1],col[2]))
        await ctx.send(embed=embedVar)




# On slash command "emplois du temps"
@bot.slash_command(guild_ids=config["discord"]["guildid"], description="Envoye l'emplois du temps dans ce channel")
async def edt(
    ctx, 
    group: discord.Option(int, "Enter your group", min_value=1, max_value=2, default=1)
    ):
    timetab = json.loads(getTimetables(str(group)))
    print(str(ctx.author) + " Executed \"edt\"")
    try:
        await ctx.respond("Voici l'emplois du temps d'aujourd'hui : ")
    except:
        print("Discord Response Timed Out !")
        await ctx.send("Discord Response Timed Out !")
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




# Add you to the list of daily Menu
@bot.slash_command(guild_ids=config["discord"]["guildid"], description="Te rajoutte a la liste des personnes qui recoivent le menu tout les jours")
async def menudm(ctx):
    print(str(ctx.author) + " Executed \"menudm\"")
    verf = 0
    for d in data["Menu"]:
        if d==ctx.author.id :
            verf += 1
    if not verf==1 :
        successful = False
        try:
            data["Menu"].append(ctx.author.id)
            with open('data.json', 'w') as f:
                json.dump(data, f, ensure_ascii=False)
            print(data)
            successful = True
        except Exception as err:
            try:
                await ctx.respond("Foirré")
            except:
                print("Discord Response Timed Out !")
                await ctx.send("Discord Response Timed Out !")
            await ctx.channel.send("Erreur : \n{0}".format(err))
        if successful:
            try:
                await ctx.respond("Sucessfully added.")
            except:
                print("Discord Response Timed Out !")
                await ctx.send("Discord Response Timed Out !")
    else:
        try:
            await ctx.respond("Tu est déja dans la liste !")
        except:
            print("Discord Response Timed Out !")
            await ctx.send("Discord Response Timed Out !")




# Remove you from the list of daily Menu
@bot.slash_command(guild_ids=config["discord"]["guildid"], description="Te retire de la liste des personnes qui recoivent le menu tout les jours")
async def menudmremove(ctx):
    print(str(ctx.author) + " Executed \"menudmremove\"")
    successful = False  
    try:
        for i in data["Menu"]:
            remcount = -1
            if ctx.author.id == i:
                remcount += 1
                break
            else:
                remcount += 1
        data["Menu"].pop(remcount)
        with open('data.json', 'w') as f:
            json.dump(data, f, ensure_ascii=False)
        print(data)
        successful = True
    except Exception as err:
        try:
            await ctx.respond("Foirré")
        except:
            print("Discord Response Timed Out !")
            await ctx.send("Discord Response Timed Out !")
        await ctx.channel.send("Erreur : \n{0}".format(err))
    if successful:
        try:
            await ctx.respond("Sucessfully Removed.")
        except:
            print("Discord Response Timed Out !")
            await ctx.send("Discord Response Timed Out !")




# Add you to the list of daily Timetables
@bot.slash_command(guild_ids=config["discord"]["guildid"], description="Te rajoutte a la liste des personnes qui recoivent l'emplois du temps tout les jours")
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
            try:
                await ctx.respond("Foirré")
            except:
                print("Discord Response Timed Out !")
                await ctx.send("Discord Response Timed Out !")
            await ctx.channel.send("Erreur : \n{0}".format(err))
        if successful:
            try:
                await ctx.respond("Sucessfully added.")
            except:
                print("Discord Response Timed Out !")
                await ctx.send("Discord Response Timed Out !")
    else:
        try:
            await ctx.respond("Tu est déja dans la liste !")
        except:
            print("Discord Response Timed Out !")
            await ctx.send("Discord Response Timed Out !")




# Remove you from the list of daily Timetables
@bot.slash_command(guild_ids=config["discord"]["guildid"], description="Te retire de la liste des personnes qui recoivent l'emplois du temps tout les jours")
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
        try:
            await ctx.respond("Foirré")
        except:
            print("Discord Response Timed Out !")
            await ctx.send("Discord Response Timed Out !")
        await ctx.channel.send("Erreur : \n{0}".format(err))
    if successful:
        try:
            await ctx.respond("Sucessfully Removed.")
        except:
            print("Discord Response Timed Out !")
            await ctx.send("Discord Response Timed Out !")




# Add you to the list of daily homeworks
@bot.slash_command(guild_ids=config["discord"]["guildid"], description="Te rajoutte a la liste des personnes qui recoivent les devoirs tout les jours")
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
            try:
                await ctx.respond("Foirré")
            except:
                print("Discord Response Timed Out !")
                await ctx.send("Discord Response Timed Out !")
            await ctx.channel.send("Erreur : \n{0}".format(err))
        if successful:
            try:
                await ctx.respond("Sucessfully added.")
            except:
                print("Discord Response Timed Out !")
                await ctx.send("Discord Response Timed Out !")
    else:
        try:
            await ctx.respond("Tu est déja dans la liste !")
        except:
            print("Discord Response Timed Out !")
            await ctx.send("Discord Response Timed Out !")




# Remove you from the list of daily homeworks
@bot.slash_command(guild_ids=config["discord"]["guildid"], description="Te retire de la liste des personnes qui recoivent les devoirs tout les jours")
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
        try:
            await ctx.respond("Foirré")
        except:
            print("Discord Response Timed Out !")
            await ctx.send("Discord Response Timed Out !")
        await ctx.channel.send("Erreur : \n{0}".format(err))
    if successful:
        try:
            await ctx.respond("Sucessfully Removed.")
        except:
            print("Discord Response Timed Out !")
            await ctx.send("Discord Response Timed Out !")




# Run the bot with the token in config.json
bot.run(config["discord"]["discordtoken"])