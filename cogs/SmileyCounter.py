import requests
import os
import time
from discord.ext.commands import Bot
import random

class SmileyCounter(object):
    '''
    Skiminok bracket counter draft.
    '''

    def __init__(self, bot: Bot) -> None:
        self._bot = bot
        self._last = time.time()

    async def on_message(self, message):
        if message.author.name == 'skiminokf':
            t = time.time()
            if t - self._last > 60:
                self._last = t
                r = self._react(self._count_smiley(message.content))
                if r:
                    await my_bot.send_message(message.channel, r)

    def _react(self, s: int) -> str:
        if s <= 2:
            return None
        elif s > 2 and s < 5:
            return ":)"
        elif s >= 5 and s < 10:
            return random.choice(("Вот ржака", "Аххахаха", "Гыыыы)", "Лол"))
        elif s < 15:
            return random.choice(("Ааааа порвало!!!!",
                                  "Ахахахаха.... фууу... давно я так не ржал",
                                  "Ржунимагу", "Ааааааа лоооооол!!!!!!"))
        else:
            return "Эталон ржача! Кименог Одобряэ."

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