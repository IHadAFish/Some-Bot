import discord, sys
import asyncio
import credentials
from random import sample as randSample
from time import gmtime as gmtime

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

    premissions = message.author.premissions

    for premission_name, have_premission in premissions:
        if premission_name == "administrator":
            admin = have_premission
            break

    if admin:

        # For testing only.
        if message.content.startswith("!eval"):
            eval(message.content[6:])

        if message.content.startswith("!logout"):
            await client.logout()
            print("Exiting.")
            try:
                sys.exit()
            except:
                pass

    if message.content.startswith("!test"):
        await client.send_message(message.channel, "Reporting in.")

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

    if not gmtime()[3] % 2:

        plays = ["with himself", "with your mind", "with gravity", "dead", "tricks"]
        playing = randSample(plays, 1)[0]
        
        await client.change_presence(game=discord.Game(name=playing))

client.run(credentials.getToken())
