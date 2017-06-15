import requests
import os
import asyncio
import sys
import psycopg2
import urllib.parse
from sqlalchemy import create_engine
from sqlalchemy import Column, Integer, String, Float
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

import discord
from discord.ext.commands import Bot, group
from discord.embeds import Embed

import socket
from contextlib import contextmanager
import time
import logging
import random

print('Starting bot')
random.seed()

Base = declarative_base()

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

class GeoLoc(Base):
    '''
    Definition of geographical location.
    '''
    __tablename__ = 'geoloc'
    name = Column(String, primary_key=True)
    lat = Column(Float, nullable=False)
    lon = Column(Float, nullable=False)

    def __repr__(self):
        return "<GeoLoc(%s, (%f, %f))>"%(self.name, self.lat, self.lon)


db_engine = create_engine(os.environ["DATABASE_URL"])
Base.metadata.create_all(db_engine)
print("Created")
Session = sessionmaker(bind=db_engine, autocommit=True)
session = Session()
print("Session")
my_bot = Bot(command_prefix="!", description="I'm pretty stupid")

async def say_in_block(message: str):
    await my_bot.say('```\n' + message + '\n```')

@my_bot.event
async def on_read():
    print('Client logged in')

@my_bot.group(name="config", pass_context=True)
async def config(ctx):
    '''
    Make some configuration magic.
    '''
    if ctx.invoked_subcommand is None:
        await my_bot.say('Unknown command: {{ GEO }}')

@config.group(name = 'geo', pass_context=True)
async def _config_geo(ctx):
    '''
    Manage geographical locations.
    '''
    if ctx.invoked_subcommand is None:
        await my_bot.say('Unknown command: {{ ADD, LIST }}')

@_config_geo.command(name="list", pass_context=False)
async def _config_geo_list():
    '''
    List geographical locations.
    '''
    res = session.query(GeoLoc).all()
    s = '\n'.join([str(r) for r in res])
    await say_in_block(s)

@_config_geo.command(name="add", pass_context=False)
async def _config_geo_add(n, la, lo):
    '''
    Add location <location code> <lat> <lon>
    '''
    name = str(n.upper())
    lat = float(la)
    lon = float(lo)
    new_loc = GeoLoc(name=name, lat=lat, lon=lon)
    session.add(new_loc)
    await my_bot.say('New location added' + str(new_loc))

@my_bot.command()
async def dump(*args):
    return my_bot.say('```\n' + str(args) + '\n```')

@my_bot.command()
async def reload():
    await my_bot.say("Reloading...")
    await my_bot.close()

def color_by_temp(t):
    '''
    Select color from temperature in C.
    '''
    if t < -15:
        return 0
    elif t < 0:
        return 0x1433ce
    elif t < 15:
        return 0x83eac9
    elif t < 25:
        return 0x45d140
    elif t < 30:
        return 0xd6cd20
    else:
       return 0xd64420

async def get_forecast(loc: GeoLoc):
    token = os.environ['DARKSKY_TOKEN']
    url = 'https://{url}/{token}/{latitude:.4f},{longitude:.4f}'.format(
        url='api.darksky.net/forecast',
        token=token,
        latitude=loc.lat,
        longitude=loc.lon)

    loop = asyncio.get_event_loop()
    async_request = loop.run_in_executor(None, requests.get, url)
    response = await async_request

    return dict(response.json())['currently']

@my_bot.command(pass_context=True)
async def weather(ctx, ln):
    '''
    Show weather forecast for location.
    '''

    loc_name = ln.upper()
    loc = session.query(GeoLoc).filter(GeoLoc.name == loc_name).first()
    if not loc:
         await my_bot.say('Use `!config geo list` to see all locations or `!config geo add` to add new one')

    data = await get_forecast(loc)

    def to_celsius(f):
        return (float(f) - 32.0) * 5.0 / 9.0

    t_in_c = to_celsius(data['apparentTemperature'])

    result = '{0:.0f} \u00B0C'.format(t_in_c)
    if data['windSpeed'] >= 2.0:
        result += ' at {0:.1f} mph wind'.format(data['windSpeed'])
    if data['precipProbability'] > 0:
        result += ' and I am {0:.0f}% sure it is {1}'.format(
            data['precipProbability'] * 100,
            'raining' if data['temperature'] > 32.0 else 'snowing')
    embed = Embed(colour=color_by_temp(t_in_c), title="Weather in " + loc_name, description=result)
    await my_bot.send_message(ctx.message.channel, content = None, embed=embed)

@my_bot.command()
async def roll(*args):
    '''
    Roll a random number.
    By default it is [1-100].
    '''
    return my_bot.say(':game_die: ' + str(random.randint(1, 100)))

print('Bot is started...')
my_bot.run(os.environ['DISCORD_TOKEN'])
