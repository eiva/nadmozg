import requests
import os
import discord
import asyncio
import sys
import psycopg2
import urllib.parse
from discord.ext.commands import Bot
from sqlalchemy import create_engine
from sqlalchemy import Column, Integer, String, Float
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import socket
from contextlib import contextmanager
import time
import logging

Base = declarative_base()

def send_metric(metric, value):
    prefix = os.environ["HOSTEDGRAPHITE_PREFIX"]
    conn = socket.create_connection((prefix + ".carbon.hostedgraphite.com", 2003))
    conn.send("{}.nadmozg.{} {}\n".format(os.environ["HOSTEDGRAPHITE_APIKEY"], metric, value))
    conn.close()

@contextmanager
def timeblock(metric):
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
my_bot = Bot(command_prefix="!")


@my_bot.event
@asyncio.coroutine
def on_read():
    print('Client logged in')

def say_in_block(message: str):
    return my_bot.say('```\n' + message + '\n```')

def config_geo(*args):
    '''
    !config geo (add dc 4.5 8.6)
    '''

    command = args[0].upper()
    if command == 'ADD':
        name = str(args[1].upper())
        lat = float(args[2])
        lon = float(args[3])
        new_loc = GeoLoc(name=name, lat=lat, lon=lon)
        session.add(new_loc)
        return my_bot.say('New location added' + str(new_loc))
    elif command == 'LIST':
        res = session.query(GeoLoc).all()
        s = '\n'.join([str(r) for r in res])
        return say_in_block(s)
    else:
        return my_bot.say('Unknown geo command: {{ ADD, LIST }}')

@my_bot.command()
@asyncio.coroutine
def config(*args):
    '''
    Make some configuration magic.
    '''
    try:
        command = args[0].upper()
        if command == 'GEO':
            return config_geo(*args[1:])
        else:
            return my_bot.say('Unknown command: {{ GEO }}')
    except Exception as e:
        return my_bot.say(e)

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
def weather(*param):
    '''
    Show weather forecast for location.
    '''
    print(param)
    if len(param) != 1:
        yield from my_bot.say('Ussage: !weather {dc, mos, b, nyc, sf}')
        return

    loc_name = param[0].upper()
    loc = session.query(GeoLoc).filter(GeoLoc.name == loc_name).first()
    if not loc:
         yield from my_bot.say('Use `!config geo list` to see all locations or `!config geo add` to add new one')

    token = os.environ['DARKSKY_TOKEN']
    url = 'https://{url}/{token}/{latitude:.4f},{longitude:.4f}'.format(
        url='api.darksky.net/forecast',
        token=token,
        latitude=loc.lat,
        longitude=loc.lon)

    loop = asyncio.get_event_loop()
    async_request = loop.run_in_executor(None, requests.get, url)
    response = yield from async_request

    data = response.json()['currently']

    def to_celsius(f):
        return (float(f) - 32.0) * 5.0 / 9.0

    result = '{0:.0f} \u00B0C'.format(to_celsius(data['apparentTemperature']))
    if data['windSpeed'] >= 2.0:
        result += ' at {0:.1f} mph wind'.format(data['windSpeed'])
    if data['precipProbability'] > 0:
        result += ' and I am {0:.0f}% sure it is {1}'.format(
            data['precipProbability'] * 100,
            'raining' if data['temperature'] > 32.0 else 'snowing')
    yield from my_bot.say(result)

print("Starting bot")
my_bot.run(os.environ['DISCORD_TOKEN'])
