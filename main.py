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

            elif message.content.startswith("b!convert-date"):

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

            if time_args["mode"] == "t":

                results = list(time_converter(**time_args))

                day_pharse = {
                    -1: "of yesterday ",
                    0: "",
                    1: "of tomorrow "
                }
                day_diff = day_pharse[results[-1]]

                n_time = results[0].strftime("%I:%M%p")

                msg = "{origin} {t_time} is {n_time} {day_diff}{target}.".format(**time_args, day_diff=day_diff, n_time=n_time)

            elif time_args["mode"] == "dt":

                results = [time_converter(**time_args)]

                n_time = results[0].strftime("%B %d, %I:%M%p")

                msg = "{origin} {t_time} {t_date} is {n_time} {target}.".format(**time_args, n_time=n_time)

            elif time_args["mode"] == "delta":

                results = list(time_converter(**time_args))

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

            desc = "There are 2 mode for time converter. Say b!help-convert to get this message."
            content = discord.Embed(title="Time converter", description=desc)

            #Time convert
            t_convert_content = "Say b!convert <time> <original timezone/cityname> <target timezone/cityname>\nIf there's more than one word in your city name, put a _ in between them.\n"
            t_convert_example = """Example:
```> b!convert 6:30 HongKong EST
> HongKong 6:30 is 05:43PM EST.```"""

            content.add_field(name="Time convert", value=t_convert_content+t_convert_example)

            dt_convert_content = "Say b!convert-date <time> <date> <original timezone/cityname> <target timezone/cityname>\nIf there's more than one word in your city name, put a _ in between them.\nMake sure the format for the date is date-month.\n"
            dt_convert_example = """Example:
```> b!convert-date 6:30am 23-12 HongKong iceland
> HongKong 6:30 23-11 is November 22, 10:30PM Iceland.```"""

            content.add_field(name="Date convert", value=dt_convert_content+dt_convert_example)
            await client.send_message(message.channel, embed=content)

        else:
            desc = """b!recommend <the recommendation> in #place-holder to give out an recommendation for resource.
b!help-convert for help on the time converter."""
            help_content = discord.Embed(title="Commands:", description=desc)

            if admin:

                admin_content = "b!getrecommendation to retrive an recommendation."
                help_content.add_field(name="Admin commands:", value=admin_content)


            await client.send_message(message.channel, embed=help_content)


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

    plays = ["with himself", "with your mind", "with gravity", "dead", "with fire"]
    playing = randSample(plays, 1)[0]

    while True:

        await client.change_presence(game=discord.Game(name=playing))

        for _ in range(3600):
            await asyncio.sleep(1)

    if list(gmtime())[3] % 2:
            await client.change_presence(game=discord.Game(name=playing))

@client.event
async def call_admin(channel, reason=None):

    text = "Generals @admin , another settlement needs your help. #{0} {1}".format(channel.name, reason)

    #434578647110778882 is the channel id for LearnJapanese #secret-scheming.
    await client.send_message(client.get_channel("434578647110778882"), text)
    #await client.send_message(client.get_channel("434287964269445122"), text)

client.run(credentials.getToken())
