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

    if message.content.startswith("b!convert"):
        args = message.content.split(" ")[1:]

        try:
            if message.content.startswith("b!convert-time") or message.content.startswith("b!convert "):

                time_args = {
                    "t_time": args[0],
                    "origin": args[1],
                    "target": args[2],
                    "mode": "t"
                }

            elif message.content.startswith("b!convert-datetime"):

                time_args = {
                    "t_time": args[0],
                    "t_date": args[1],
                    "origin": args[2],
                    "target": args[3],
                    "mode": "dt"
                }

            elif message.content.startswith("b!convert-timediff"):

                time_args = {
                    "t_time": args[0],
                    "t_date": args[1],
                    "origin": args[2],
                    "s_time": args[3],
                    "s_date": args[4],
                    "target": args[5],
                    "mode": "delta"
                }

            else:
                raise SomeError("mode_not_exist")

            results = list(time_converter(**time_args))

            if time_args["mode"] == "t":

                day_pharse = {
                    -1: "yesterday ",
                    0: "",
                    1: "tomorrow"
                }
                day_diff = day_pharse[results[-1].days]

                n_time = results[0].strftime("%I:%M%p")

                msg = "{origin} {t_time} is {n_time} {day_diff}{target}.".format(**time_args, day_diff=day_diff, n_time=n_time)

            elif time_args["mode"] == "dt":

                n_time = results[0].strftime("%B %d, %I:%M%p")

                msg = "{origin} {t_time} {t_date} is {n_time} {target}.".format(**time_args, day_diff=day_diff, n_time=n_time)

            elif time_args["mode"] == "delta":

                time_delta_args = {
                    "days": abs(results[0].days),
                    "hour": results[0].second//3600,
                    "minute": (results[0] % 3600)//60
                }
                time_delta = "{days} day {hour} hour and {minute} minute".format(**time_delta_args)

                if results[0].days < 0 or results[0].seconds < 0:
                    time_diff = "earlier"
                else:
                    time_diff = "later"

                msg = "{origin} {t_time} {t_date} is {time_delta} {time_diff} than {target} {s_time} {s_date}.".format(
                      time_delta=time_delta, time_diff=time_diff, **time_args)

            await client.send_message(message.channel, msg)

        except SomeError as e:
            err_msgs = {
                "location_not_exist": "The timezone/location you said is not supported. Sorry :p",
                "mode_not_exist": "There's something wrong with the mode you said. Say b!help-convert for help."
            }

            err_msg = err_msgs[repr(e)]

        except ValueError:
            err_msg = "There's something wrong with the time you said. Say b!help-convert for help."

        #except:
        #    err_msg = "Something is wrong with your command. Say b!help-convert for help."
        try:
            await client.send_message(message.channel, err_msg)
        except UnboundLocalError:
            pass

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
            desc = ""
            examples = ""

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
