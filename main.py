import discord, asyncio, credentials, re
from sys import exit
from random import sample as randSample
from time import gmtime
from SomeError import SomeError
from timeconverter import time_converter

client = discord.Client()

@client.event
async def on_ready():

    print("Logged in as")
    print(client.user.name)
    print(client.user.id)
    print("------")

    await randPlay()

global recommendations
recommendations = []

@client.event
async def on_message(message):

    permissions = message.author.server_permissions

    for permission_name, have_permission in permissions:
        if permission_name == "administrator":
            admin = have_permission
            break

    #Auto assign roles in #set-your-role
    if message.channel.name == "set-your-role":

        if not set(message.author.roles).isdisjoint(set(["Beginners", "Intermediates", "Experts"])):
            await client.send_message(message.channel, "You already set your expertise level, if you are looking for a level up, please contact an admin.")

        message_text = message.content.lower()

        #needs more alias
        expertise = {
            "Beginners": set("beginner"),
            "Intermediates": set("intermediate"),
            "Experts": set("expert")
        }

        for level in expertise:
            difference = {}
            difference[len(set(message_text).symmetric_difference(expertise[level]))] = level

        if min(difference.keys()) <= 4:
            level = difference[min(difference.keys())]
            for role in message.server.roles:
                if role.name.lower() == level.lower():
                    await client.add_roles(message.author, role)
                    break

    #if message.content.startswith("b!convert"):
    #    args = message.content.split(" ")[1:]

    #    if message.content.startswith("b!convert-time"):
    #        try:
    #            time_converter()




    #queue the resource suggestion
    if message.content.startswith("b!recommend") and message.channel.name == "test":

        recommendations.append(message.content[13:] + " Provider: {0}".format(message.author.name))
        print(recommendations)
        await client.send_message(message.channel, "Thank you for the recommendation. The admins have been alerted.")

        await call_admin(message.channel, "New recommendation.")

    if admin:

        if message.content.startswith("b!getrecommendation"):
            await client.send_message(message.channel, recommendations.pop(0))
            await client.send_message(message.channel, "{0} more in queue.".format(len(recommendations)))

        # For testing only.
        #if message.content.startswith("b!eval"):
        #    eval(message.content[6:])

        if message.content.startswith("b!admintest"):
            await client.send_message(message.channel, "All hail lord {0}.".format(message.author.name))

        if message.content.startswith("b!logout"):
            await client.logout()
            print("Exiting.")
            try:
                exit()
            except:
                pass

        if message.content.startswith("b!test"):
            desc = "AHH shit."
            em = discord.Embed(title='My Embed Title', description=desc)
            await client.send_message(message.channel, embed=em)

        #if message.content.startswith("b!alerttest"):
        #    await call_admin(message.channel)

    if message.content.startswith("b!help"):
        if message.content.startswith("b!help-convert"):
            desc = "Say b!convert <hour:minute> <timezone/location> <your timezone/location> to convert time.\nSupport both 24 hour and 12 hour format."
            examples = """b!convert 8pm tokyo london
> 8pm Tokyo is 12 pm London
b!convert 17 Singapore EST
> 17 Singapore is 4 EST"""

            content = discord.Embed(title="Time converter", description = desc)
            content.add_field(name="Examples", value = examples)
            await client.send_message(message.channel, embed=content)

        help_content = "Type b!recommend + your recommendation in #place-holder to give out an recommendation for resource."
        if admin:
            help_content += "\nb!getrecommendation to retrive an recommendation."

        client.send_message(message.channel, help_content)


@client.event
async def on_member_join(member):

    #Welcome message when member join.
    if not member.bot:

        channels = member.server.channels

        for channel in channels:
            if channel.name == "general":
                t_channel = channel
                break

        #spider privided the message.
        await client.send_message(t_channel,
            "Welcome to the server, {0} ! To set your expertise level, go to #set-your-role , if you have any questions/suggestions, go to #suggestions  or ping an admin.".format(member.name))

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
async def call_admin(channel, reason="None"):

    text = "Generals @admin , another settlement needs your help. #{0} {1}".format(channel.name, reason)

    #434578647110778882 is the channel id for LearnJapanese #secret-scheming.
    await client.send_message(client.get_channel("434578647110778882"), text)
    #await client.send_message(client.get_channel("434287964269445122"), text)

client.run(credentials.getToken())
