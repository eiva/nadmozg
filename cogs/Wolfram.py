import os
import asyncio
from discord.embeds import Embed
from discord.ext.commands import command, Bot
from urllib.parse import quote
from lxml import etree
import requests


class Wolfram(object):
    '''
    Execute query on wolfram alpha api and return kind of most related replys.
    '''

    def __init__(self, bot: Bot) -> None:
        self._bot = bot
        self._api = os.environ["WOLFRAM_API"]

    def _query(self, query: str) -> Embed:
        query = query.encode('utf-8')
        
        response = requests.get('http://api.wolframalpha.com/v2/query?input=%s&appid=%s'%(quote(query), self._api))
        try:
            tree = etree.fromstring(response.content)
            results = []
            embed = Embed(color=0xFFFFFF)
        
            ident = tree.xpath('//pod[contains(@scanner, "Identity")]/subpod/plaintext')

            if len(ident) > 0:
                embed.title = ident[0].text

            ok = False
            def append(name, path):
                nonlocal ok
                if ok:
                    return
                nonlocal embed
                res = tree.xpath(path)
                if len(res) > 0:
                    ok = True
                    print('Adding ', res[0].text)
                    embed.add_field(name=name, value=res[0].text)

            append('Solution','//pod[contains(@title, "Solution")]/subpod/plaintext')
            append('Result','//pod[contains(@title, "Result")]/subpod/plaintext')
            append('Value','//pod[contains(@scanner, "Numeric")]/subpod/plaintext')
            append('Data','//pod[contains(@scanner, "Data")]/subpod/plaintext')
            append('Numerical solution', '//pod[contains(@title, "Numerical solution")]/subpod/plaintext')
            append('Numerical solutions', '//pod[contains(@title, "Numerical solutions")]/subpod/plaintext')
            if ok:
                print('returning data')
                return embed
            print("No result", response.text)
            return None
        except Exception as e:
            print("Exception", e, response.text)
            return None

    @command()
    async def q(self, *query:str):
        '''
        Try to ask some stupid question, and I'll try to answer it.
        '''
        qq = ' '.join(query)
        loop = asyncio.get_event_loop()
        async_request = loop.run_in_executor(None, lambda: self._query(qq))
        e = await async_request
        if e:
            await self._bot.say(embed=e)
        else:
            await self._bot.say('Dont know answer for: *' + qq +'* :weary: ')

