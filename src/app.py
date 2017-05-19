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

my_bot.run(os.environ['DISCORD_TOKEN'])
