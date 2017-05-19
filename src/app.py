import os
import discord
import asyncio
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

my_bot.run(os.environ['DISCORD_TOKEN'])
