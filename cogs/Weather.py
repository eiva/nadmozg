from discord.ext.commands import Bot, group, command
import requests
import asyncio
from utils.Db import Session, GeoLoc
from discord.embeds import Embed
import os

class Weather(object):
    '''
    Current weather.
    '''

    def __init__(self, bot: Bot) -> None:
        self._bot = bot
        self._token = os.environ['DARKSKY_TOKEN']

    def _color_by_temp(self, t):
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

    async def _get_forecast(self, loc: GeoLoc):
        url = 'https://{url}/{token}/{latitude:.4f},{longitude:.4f}'.format(
            url='api.darksky.net/forecast',
            token=self._token,
            latitude=loc.lat,
            longitude=loc.lon)

        loop = asyncio.get_event_loop()
        async_request = loop.run_in_executor(None, requests.get, url)
        response = await async_request

        return dict(response.json())['currently']

    @command(pass_context=True)
    async def weather(self, ctx, ln):
        '''
        Show weather forecast for location.
        '''

        loc_name = ln.upper()
        loc = Session.query(GeoLoc).filter(GeoLoc.name == loc_name).first()
        if not loc:
             await self._bot.say('Use `!config geo list` to see all locations or `!config geo add` to add new one')

        data = await self._get_forecast(loc)

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
        embed = Embed(colour=self._color_by_temp(t_in_c), title="Weather in " + loc_name, description=result)
        await self._bot.send_message(ctx.message.channel, content = None, embed=embed)