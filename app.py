from discord.ext.commands import Bot

import socket
from contextlib import contextmanager

import utils.Db

from cogs.SmileyCounter import SmileyCounter
from cogs.Wolfram import Wolfram
from cogs.RollGame import RollGame
from cogs.Configuration import Configuration
from cogs.Weather import Weather
from cogs.Humor import Humor

import os
import random
random.seed()


@contextmanager
def timeblock(metric):
    def send_metric(metric, value):
        prefix = os.environ["HOSTEDGRAPHITE_PREFIX"]
        conn = socket.create_connection((prefix + ".carbon.hostedgraphite.com", 2003))
        conn.send("{}.nadmozg.{} {}\n".format(os.environ["HOSTEDGRAPHITE_APIKEY"], metric, value))
        conn.close()
    start = time.perf_counter()
    try:
        yield
    finally:
        end = time.perf_counter()
        send_metric(metric, end - start)


my_bot = Bot(command_prefix="!", description="I'm pretty stupid")
my_bot.add_cog(SmileyCounter(my_bot))
my_bot.add_cog(Wolfram(my_bot))
my_bot.add_cog(RollGame(my_bot))
my_bot.add_cog(Configuration(my_bot))
my_bot.add_cog(Weather(my_bot))
my_bot.add_cog(Humor(my_bot))

print('Running...')
my_bot.run(os.environ['DISCORD_TOKEN'])
