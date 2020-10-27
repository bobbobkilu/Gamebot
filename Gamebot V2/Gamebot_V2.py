import discord
import logging
import os
import re
import sys
from urllib import request

logging.basicConfig(level=logging.INFO)
__location__ = os.path.realpath(os.path.join(os.getcwd(), os.path.dirname(__file__)))
client = discord.Client()

#set variables from environment variables
token = os.environ.get('TOKEN');
owner = os.environ.get('OWNER');


botChannel = 341343329356742670
currentGame = "";
fileList = os.listdir(os.path.join(__location__, "Images"))

#functions
def getGameName(content):

    global fileList

    for i in range(len(fileList)):

       currentFile = fileList[i]
       currentFile = currentFile.replace(".png","")

       if currentFile.lower() in content.lower():
           return currentFile

    return ""

    return False

#Updates the server icon to match the game being played
async def onPlayerUpdate(member):
    global currentGame
    gameActivity = None;
    print("CurrentGame:\t" + currentGame)
    print("Member:\t" + member.name)

    try:
        voiceChannel = member.voice.channel
    except:
        return

    for activity in member.activities:
        if activity.type == discord.activity.ActivityType.playing:
            gameActivity = activity
            print("Activity:\t" + gameActivity.name)

    if (gameActivity != None and gameActivity.name == "Tabletop Simulator" and voiceChannel.id == 329887569238163467):

        try:
            details = re.sub(r'\([^)]*\)', '', gameActivity.details)
            print("Details:\t" + details)
        except:
           print("Error getting details")
           return

        if (details == "Grooving in the menus" or details ==  "No game loaded" or str(details)== currentGame):
            print("No post Nessisary")
            return

        else:
            print("Checking for images")
            file = "Images/" + getGameName(details) + ".png"
            if file != "Images/.png":
                print("Image found")
                try:
                    await member.guild.get_channel(botChannel).send("Current game: " + details)
                except:
                    None
                newIcon = open(file, 'rb')
                await member.guild.edit(icon = newIcon.read())
                newIcon.close()
                   
            else:
                print("No image found")
                try:
                    await member.guild.get_channel(botChannel).send("Current game: " + details)
                except:
                    None
                newIcon = open('in_progress.png', 'rb')
                await member.guild.edit(icon = newIcon.read())
                newIcon.close()

            currentGame = str(details)
        


#login info
@client.event
async def on_ready():
    print('Logged in as')
    print(client.user.name)
    print(client.user.id)
    print('------')



@client.event

async def on_voice_state_update(member, oState, nState):
    #On First Player Join Function
    if (nState.channel != None and nState.channel.id == 329887569238163467) and (oState.channel == None or oState.channel.id != 329887569238163467) and len(client.get_channel(329887569238163467).members) == 1:
        await onPlayerUpdate(member)

        #ping players
        await member.guild.get_channel(botChannel).send(member.guild.get_role(495480333635026954).mention + ", " + member.display_name + " hath summoned thee for games.")

    #On Last Player Left Function
    if (nState.channel == None and oState.channel.id == 329887569238163467) and len(client.get_channel(329887569238163467).members) == 0:
        await member.guild.get_channel(botChannel).send("The games are over.")
        newIcon = open('normal.png', 'rb')
        await member.guild.edit(icon = newIcon.read())
        newIcon.close()



#On Member Update
@client.event
async def on_member_update(oMember,nMember):
    await onPlayerUpdate(nMember)


#On Message Functions
@client.event
async def on_message(message):
    global fileList

        #dont talk to yourself
    if message.author == client.user:
            return

        #only talk in is-there-a-game
    if message.channel.id != botChannel:
            return


        #Add/Remove Pinglist
    if message.content.startswith("!ping"):
            if message.guild.get_role(495480333635026954) in message.author.roles:
                await message.author.remove_roles(message.guild.get_role(495480333635026954))
                await message.channel.send("You have been removed from the ping list.")
            else:
                await message.author.add_roles(message.guild.get_role(495480333635026954))
                await message.channel.send("You have been added to the ping list.")

            with open("Config.txt", "w") as configfile:
                config.write(configfile)
                
         #Help function
    if message.content.startswith("!list"):
            await message.channel.send("Available Images: \n ```" + " \n".join([i.replace(".png","") for i in fileList]) + "```")


    #add to list
    if message.content.startswith("!add"):
            fileName = "Images/" + message.content.replace("!add ", "") + ".png"
            if fileName in fileList:
                await message.channel.send("Image already present")
                return

            if message.attachments != []:
                try:
                   await message.attachments[0].save(fileName)
                   await message.channel.send("Image added to list")
                   fileList = os.listdir(os.path.join(__location__, "Images"))
                except:
                   print(sys.exc_info())
                   await message.channel.send("invalid image")
                   return
                

            else:
                print("no attachments")
                await message.channel.send("invalid image")


client.run(token)


