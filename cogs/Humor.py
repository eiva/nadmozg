from discord.ext.commands import Bot, command
from discord.embeds import Embed
import random
import html
import asyncio
import requests

class Humor(object):
    '''
    Fun stuff.
    '''

    def __init__(self, bot: Bot) -> None:
        self._bot = bot

    @command()
    async def bash(self):
        '''
        А нука башни!
        '''
        url = 'http://bash.im/forweb/?u'
        headers = {'User-Agent': 'Mozilla/5.0'}
        loop = asyncio.get_event_loop()
        async_request = loop.run_in_executor(None, lambda: requests.get(url, headers=headers))
        r = await async_request
        r.encoding = 'utf-8'
        text = r.text
        text = text[text.find('b_q_t'):]
        text = text[text.find('">')+2:]
    
        text = text[:text.find("<' + '/div>")]
        text = text.replace("<' + 'br>", '\n')
        text = text.replace("<' + 'br />", '\n')
        text = html.unescape(text)

        embed = Embed(color=1, description=text)
        embed.set_footer(text="Bash.im")
        await self._bot.say(embed=embed)