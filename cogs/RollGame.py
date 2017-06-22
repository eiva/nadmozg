import asyncio
from discord.ext.commands import Bot, group, Context
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
            uid = ctx.message.author.name
            if hasattr(ctx.message.author, 'nick'):
                if ctx.message.author.nick:
                    uid = ctx.message.author.nick
            args = ctx.message.content.split()
            if len(args) == 2:
                res = self._roll_with_arg(uid, args[1])
                if res:
                    await self._bot.say(res)
                    return
            elif len(args) == 1:
                await self._generate_simple_roll(uid, ctx)
                return
            await self._bot.say("Try something like '!roll', '!roll <max>', '!roll <min>-<max>', '!roll 3d5'.")


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

    async def _generate_simple_roll(self, uid, ctx):
        '''
        Geenerate reply for simple roll (including the roll game check)
        '''
        r = random.randint(1, 100)
        cid = ctx.message.channel.id
        
        c = self._roll(cid, uid, r)
        await self._bot.say('__' + uid + '__ :game_die: _[1-100]_' + 
                            ' **' + str(r) + "**"
                        + (", but I'll not count it "
                            ":stuck_out_tongue_closed_eyes: " 
                            if not c else ''))

    def _roll_with_arg(self, uid: str, arg: str) -> str:
        '''
        Try to parse arg and generate value if one of template is match
        '''
        def try_parse_int(s):
            try:
                return int(s)
            except ValueError:
                return None

        def try_int():
            val = try_parse_int(arg)
            if not val:
                return None
            if val > 1:
                return str(random.randint(1, val))
            return None

        def try_int_range():
            try:
                vals = arg.split('-')
                if len(vals) != 2:
                    return None
                f = try_parse_int(vals[0])
                s = try_parse_int(vals[1])
                if not f or not s:
                    return None
                mi = min(f, s)
                ma = max(f, s)
                return str(random.randint(mi, ma))
            except ValueError:
                return None

        def try_d():
            try:
                vals = arg.split('d')
                if len(vals) != 2:
                    return None
                num = try_parse_int(vals[0])
                d = try_parse_int(vals[1])
                if not num or not d:
                    return None
                if num > 20:
                    return None
                roll = [0] * num
                for i in range(num):
                    roll[i] = random.randint(1, d)
                return '[' + ', '.join([str(r) for r in roll]) + '] = ' + str(sum(roll))
            except ValueError:
                return None

        def format_reply(s):
            return '__' + uid + '__ :game_die: _[' + arg + ']_ **' + s + '**'

        s = try_int()
        if s:
            return format_reply(s)
        s = try_int_range()
        if s:
            return format_reply(s)
        s = try_d()
        if s:
            return format_reply(s)
        return None

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
