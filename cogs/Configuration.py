from discord.ext.commands import Bot, group, command
from utils.Db import Session, GeoLoc


class Configuration(object):
    '''
    Various configuration utils.
    '''

    def __init__(self, bot: Bot) -> None:
        self._bot = bot

    @group(name="config", pass_context=True)
    async def config(self, ctx):
        '''
        Make some configuration magic.
        '''
        if ctx.invoked_subcommand is None:
            await self._bot.say('Unknown command: {{ GEO }}')

    @config.group(name = 'geo', pass_context=True)
    async def _config_geo(self, ctx):
        '''
        Manage geographical locations.
        '''
        if ctx.invoked_subcommand is None:
            await self._bot.say('Unknown command: {{ ADD, LIST }}')

    @_config_geo.command(name="list", pass_context=False)
    async def _config_geo_list(self):
        '''
        List geographical locations.
        '''
        res = Session.query(GeoLoc).all()
        s = '\n'.join([str(r) for r in res])
        await self._bot.say('```\n' + s + '\n```')

    @_config_geo.command(name="add", pass_context=False)
    async def _config_geo_add(self, n, la, lo):
        '''
        Add location <location code> <lat> <lon>
        '''
        name = str(n.upper())
        lat = float(la)
        lon = float(lo)
        new_loc = GeoLoc(name=name, lat=lat, lon=lon)
        Session.add(new_loc)
        await self._bot.say('New location added' + str(new_loc))
