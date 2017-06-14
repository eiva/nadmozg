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


Base = declarative_base()

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

Session = sessionmaker(bind=db_engine, autocommit=True)
session = Session()

my_bot = Bot(command_prefix="!") 

@my_bot.event 
@asyncio.coroutine 
def on_read():
    print("Client logged in")

def say_in_block(message: str):
    return my_bot.say('```\n' + message + '\n```')

def config_geo(*args):
    '''
    !config geo (add dc 4.5 8.6)
    '''
    # session.add(GeoLoc(name='DC', lat=38.9977, lon=-77.0988))
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
        s = '\n'.join(res)
        return say_in_block(s)
    else:
        return my_bot.say('Unknown geo command: {{ ADD, LIST }}')

@my_bot.command()
@asyncio.coroutine
def config(*args):
    '''
    Make come configuration magic
    '''
    try:
        command = args[0].upper()
        if command == 'GEO':
            return config_geo(args[1:])

        return my_bot.say('Unknown command: {{ GEO }}')
    except Exception as e:
        return my_bot.say(e)

@my_bot.command()
@asyncio.coroutine
def ccc(command, subcommand, *args):
    return my_bot.say(command, ";", subcommand, ";", '.'.join(args))

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
    print(param)
    if len(param) != 1:
        yield from my_bot.say("Ussage: !weather {dc, mos, b, nyc, sf}")
        return

    param = param[0].upper()
    print(param)
    if param == 'DC':
        coords=(38.9977, -77.0988)
    elif param == 'MOS':
        coords=(55.75222, 37.615560)
    elif param == 'B':
        coords=(52.5243700, 13.4105300)
    elif param == 'NYC':
        coords=(40.730610, -73.935342)
    elif param == 'SF':
        coords = (37.751, -122.3784)
    else:
        yield from my_bot.say("Only dc, nyc, sf, mos ot b for now")
        return

    token = os.environ['DARKSKY_TOKEN']
    url = 'https://{url}/{token}/{latitude:.4f},{longitude:.4f}'.format(
        url='api.darksky.net/forecast',
        token=token,
        latitude=coords[0],
        longitude=coords[1],
    )

    loop = asyncio.get_event_loop()
    async_request = loop.run_in_executor(None, requests.get, url)
    response = yield from async_request

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
    yield from my_bot.say(result)

my_bot.run(os.environ['DISCORD_TOKEN'])
