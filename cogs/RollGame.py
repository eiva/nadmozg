from discord.ext.commands import Bot, group, command
import random


class RollGame(object):
    '''
    Random number game.
    '''

    def __init__(self, bot: Bot) -> None:
        self._bot = bot
        self._state = dict()

    @group(name="roll", pass_context=True)
    async def roll(self, ctx):
        '''
        Roll a random number.
        By default it is [1-100].
        '''
        if ctx.invoked_subcommand is None:
            r = random.randint(1, 100)
            cid = ctx.message.channel.id
        
            uid = ctx.message.author.name
            if hasattr(ctx.message.author, 'nick'):
                if ctx.message.author.nick:
                    uid = ctx.message.author.nick

            c = self._roll(cid, uid, r)
            await self._bot.say('__' + uid + '__ :game_die: **' + str(r) + "**"
                            + (", but I'll not count it "
                               ":stuck_out_tongue_closed_eyes: " 
                               if not c else ''))

    @roll.command(name="start", pass_context=True)
    async def _roll_start(self, ctx):
        '''
        Start rolling game.
        '''
        cid = ctx.message.channel.id
        if not self._start(cid):
            await self._bot.say("Game already in progress, make your roll")
        else:
            await self._bot.say(':timer: Roll game started. Lets rock and `!roll`!\n' +
                             "Hurry, you have only one minute and only one try.\n" + 
                             "~~And than I'll kill all humans!!! bugaga!!!~~...")
            await asyncio.sleep(60)
            res = self._stop(cid)
            if not res:
                await self._bot.say(":robot: *So boring....*")
            else:
                suf = 's' if len(res) > 1 else ''
                con = ' are ' if len(res) > 1 else ' is '
                await self._bot.say(":first_place: And the winner" +  suf + con +
                                 ', '.join(['**'+ r + '**' for r in res]) + '!' +
                                 "\n Congrats, human" + suf + "!")

    def _start(self, cid) -> bool:
        if cid in self._state:
            return False
        self._state[str(cid)] = dict()
        return True

    def _roll(self, cid, uid, val):
        if str(cid) not in self._state:
            return True
        if uid in self._state[cid]:
            return False
        self._state[cid][uid] = val
        return True

    def _stop(self, channel_id):
        state = self._state[channel_id]
        del self._state[channel_id]
        return [k for k,v in state.items() if v == max(state.values())]

