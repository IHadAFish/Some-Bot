import discord, sys
import asyncio
import credentials

client = discord.Client()

@client.event
async def on_ready():
    print("Logged in as")
    print(client.user.name)
    print(client.user.id)
    print("------")

@client.event
async def on_message(message):

    if message.content.startswith("!logout"):
        await client.logout()
        print("Exiting.")
        try:
            sys.exit()
        except:
            pass

@client.event
async def on_member_join(member):

    if not member.bot:

        channels = member.server.channels

        for channel in channels:
            if channel.name == "general":
                t_channel = channel
                break

        await client.send_message(t_channel, "Welcome")

client.run(credentials.getToken())
