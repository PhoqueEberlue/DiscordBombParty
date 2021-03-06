from discord.ext import commands
from .slapz import Slapz
from .player import Player
from asyncio import TimeoutError
from random import choice
import discord


class CogSlapz(commands.Cog):

    def __init__(self, bot: discord.client) -> None:
        self.bot = bot
        self._createMsg = "Click on the reaction to join the Slapz game!"

    @commands.command()
    async def slapz(self, ctx: commands.Context) -> None:
        await ctx.send(self._createMsg)
        partyMessage = ctx.channel.last_message
        await partyMessage.add_reaction("✅")

    @commands.command()
    async def playslapz(self, ctx: commands.Context) -> None:
        reac = None
        players = []
        async for message in ctx.channel.history(limit=100):
            if message.author == self.bot.user and message.content == self._createMsg:
                reac = message.reactions[0]
                break
        strPlayerList = ''
        if reac is not None:
            async for user in reac.users():
                if user != self.bot.user:
                    players.append(Player(user))
                    strPlayerList += f' {user.mention} |'
        if len(players) < 2:
            await ctx.send('not enough players')
        else:
            game = Slapz(players)
            while not game.getEnd():
                currentPlayer = game.nextPlayer()
                await ctx.send(
                    f'{currentPlayer.getUser().mention}\'s turn \nInventory: {currentPlayer.getInventory()}, HP: {currentPlayer.getHp()}\nChose your action: move or eat')
                msg = await self.waitmsg(ctx, currentPlayer)
                if msg == "timeout":
                    msg = choice(["m", "p"])
                if msg in ["move", "m", "1"]:
                    action = game.Move(currentPlayer)
                    if action[0] == "fight":
                        #game.fight(action[1])
                        await ctx.send(f'{currentPlayer} vs {action[1]}\nChose your action: attack or eat')
                        fightmsg = await self.waitmsg(ctx, currentPlayer)
                        if fightmsg == "timeout":
                            fightmsg = choice(["a", "e"])
                        if fightmsg in ["attack", "a", "1"]:
                            await ctx.send(f'{currentPlayer.attack(action[1])}')
                            if action[1].getHp() <= 0:
                                game.removePlayer(action[1])
                                await ctx.send(f'{action[1]} was eliminated by {currentPlayer}')
                            else:
                                await ctx.send(action[1].attack(currentPlayer))
                                if currentPlayer.getHp() <= 0:
                                    game.removePlayer(currentPlayer)
                                    await ctx.send(f'{currentPlayer} was eliminated by {action[1]}')
                        elif fightmsg in ["eat", "e", "2"]:
                            currentPlayer.eat()
                            await ctx.send(action[1].attack(currentPlayer))
                            if currentPlayer.getHp() <= 0:
                                game.removePlayer(currentPlayer)
                                await ctx.send(f'{currentPlayer} was eliminated by {action[1]}')
                    if action[0] == "loot":
                        await ctx.send(f'you looted {action[1]}')
                    if action[0] == "full":
                        await ctx.send("your inventory is full")
                elif msg in ["eat", "e", "2"]:
                    currentPlayer.eat()
                game.updateCoef()
            await ctx.send(f'{game.getWinner().getUser().mention} won')

    async def waitmsg(self, ctx: commands.context, player: Player) -> str:
        try:
            msg = await self.bot.wait_for('message', check=lambda
                message: message.author == player.getUser() and ctx.channel == message.channel, timeout=15)
            return msg.content
        except TimeoutError:
            return "timeout"


def setup(bot: discord.client) -> None:
    bot.add_cog(CogSlapz(bot))
