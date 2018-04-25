import discord, sys
import asyncio
import credentials
from random import sample as randSample
from time import gmtime as gmtime
from time import sleep

client = discord.Client()

@client.event
async def on_ready():

    print("Logged in as")
    print(client.user.name)
    print(client.user.id)
    print("------")

    await randPlay()

@client.event
async def on_message(message):

    permissions = message.author.server_permissions

    for permission_name, have_permission in permissions:
        if permission_name == "administrator":
            admin = have_permission
            break

    if message.channel.name == "set-your-role":
        message_text = message.content.lower()

        beginner = ["beginner"]

    if admin:

        # For testing only.
        if message.content.startswith("b!eval"):
            eval(message.content[6:])

        if message.content.startswith("b!admintest"):
            await client.send_message(message.channel, "All hail lord {0}.".format(message.author.name))

        if message.content.startswith("b!logout"):
            await client.logout()
            print("Exiting.")
            try:
                sys.exit()
            except:
                pass

        if message.content.startswith("b!test"):
            await client.send_message(message.channel, "Reporting in.")

        if message.content.startswith("b!alerttest"):
            await call_admin(message.channel)

@client.event
async def on_member_join(member):

    if not member.bot:

        channels = member.server.channels

        for channel in channels:
            if channel.name == "general":
                t_channel = channel
                break

        await client.send_message(t_channel, "Welcome")

@client.event
async def randPlay():
    #I need to fix this.

    plays = ["with himself", "with your mind", "with gravity", "dead"]
    playing = randSample(plays, 1)[0]

    while True:

        await client.change_presence(game=discord.Game(name=playing))

        for _ in range(3600):
            await asyncio.sleep(1)

    if list(gmtime())[3] % 2:
            await client.change_presence(game=discord.Game(name=playing))

@client.event
async def call_admin(channel):

    text = "Generals @admin , another settlement needs your help. #{0}".format(channel.name)

    #434578647110778882 is the channel id for LearnJapanese #secret-scheming.
    await client.send_message(client.get_channel("434578647110778882"), text)
    #await client.send_message(client.get_channel("434287964269445122"), text)

client.run(credentials.getToken())
