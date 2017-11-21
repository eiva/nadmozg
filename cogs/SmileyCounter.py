import requests
import os
import time
from discord.ext.commands import Bot
import random
import keen

class SmileyCounter(object):
    '''
    Skiminok bracket counter draft.
    '''

    def __init__(self, bot: Bot) -> None:
        self._bot = bot
        self._last = time.time()
        
    def __log(self, grade: int) -> None:
        keen.add_event("smile", {"str": grade})

    async def on_message(self, message):
        if message.author.name == 'skiminokf':
            t = time.time()
            if t - self._last > 60:
                self._last = t
                r = self._react(self._count_smiley(message.content))
                if r:
                    await self._bot.send_message(message.channel, r)

    def _react(self, s: int) -> str:
        if s <= 2:
            self.__log(0)
            return None
        elif s > 2 and s < 5:
            self.__log(1)
            return ":)"
        elif s >= 5 and s < 10:
            self.__log(2)
            return random.choice(("Вот ржака", "Аххахаха", "Гыыыы)", "Лол"))
        elif s < 15:
            self.__log(3)
            return random.choice(("Порвало!!!!",
                                  "Ахахахаха!!!! :)))",
                                  "Ржунимагу", "Ааааааа лоооооол!!!!!!"))
        else:
            self.__log(4)
            return "Да-ну, разве это ржака?!"

    def _count_smiley(self, s: str) -> int:
        '''
        Counts maximum amount of consecutive ')' chars
        '''
        m= 0
        count = 0
        for c in s:
            if c == ')':
                count += 1
            else:
                m = max(count, m)
                count = 0
        return max(count, m)
