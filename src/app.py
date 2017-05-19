import os
import discord
import asyncio
import sys
from discord.ext.commands import Bot

my_bot = Bot(command_prefix="!") 

@my_bot.event 
@asyncio.coroutine 
def on_read():
    print("Client logged in")

@my_bot.command()
@asyncio.coroutine
def hello(*args):
    return my_bot.say("Hello, world!")


@my_bot.command()
@asyncio.coroutine
def dump(*args):
    return my_bot.say('```\n' + str(args) + '\n```')


@my_bot.command()
@asyncio.coroutine
def reload(*args):
    yield from my_bot.say("Reloading...")
    yield from my_bot.close()

@my_bot.command()
@asyncio.coroutine
def weather(param):
    if len(param) != 1:
        return my_bot.say("Ussage: !weather {dc, mos, b}")
    param = param[0].upper()
    if param == 'DC':
        coords=(38.9977, -77.0988)
    elif param == 'MOS':
        coords=(55.75222, 37.615560)
    elif param == 'B':
        coords=(52.5243700, 13.4105300)
    else:
        return my_bot.say("Only dc, mos ot b for now")

    token = "a229ef1d142a0f2af70e4d920ab45698"
    url = 'https://{url}/{token}/{latitude:.4f},{longitude:.4f}'.format(
        url='api.darksky.net/forecast',
        token=token,
        latitude=coords[0],
        longitude=coords[1],
    )
    logging.debug("Fetching %r", url)
    loop = asyncio.get_event_loop()
    async_request = loop.run_in_executor(None, requests.get, url)
    response = yield from async_request
    logging.debug("Result %r", response.status_code)
    data = response.json()['currently']

    def to_celsius(f):
        return (float(f) - 32.0) * 5.0 / 9.0

    result = "{0:.0f} \u00B0C".format(to_celsius(data['apparentTemperature']))
    if data['windSpeed'] >= 2.0:
        result += " at {0:.1f} mph wind".format(data['windSpeed'])
    if data['precipProbability'] > 0:
        result += " and I am {0:.0f}% sure it is {1}".format(
            data['precipProbability'] * 100,
            "raining" if data['temperature'] > 32.0 else "snowing")
    return my_bot.say(result)

my_bot.run(os.environ['DISCORD_TOKEN'])
