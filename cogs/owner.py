import asyncio
import aiohttp
import discord
from discord.ext import commands
from settings.config import OWNER_ID


class Owner(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    # Send the message given as param
    @commands.command(name='test_message', aliases=['tm'], hidden=True)
    @commands.is_owner()
    async def test_message(self, ctx, message):
        await ctx.send(message)

    # Change the Bot avatar
    @commands.command(hidden=True)
    @commands.is_owner()
    async def avatar(self, ctx, avatar_url):
        async with aiohttp.ClientSession() as aioClient:
            async with aioClient.get(avatar_url) as resp:
                new_avatar = await resp.read()
                await self.bot.user.edit(avatar=new_avatar)
                await ctx.send('Avatar changed!')

    # Change the Bot status/presence
    @commands.command(hidden=True)
    @commands.is_owner()
    async def status(self, ctx, *, message: str):
        check_status = message.format(len(self.bot.guilds))
        print(check_status)
        if check_status == 'none':
            await self.bot.change_presence(activity=None)
        else:
            new_status = discord.Game(name=message.format(len(self.bot.guilds)))
            await self.bot.change_presence(activity=new_status)
            self.bot.status_format = message
            await ctx.send('Status changed!')

    # Get the number of all the commands executed
    @commands.command(hidden=True)
    @commands.is_owner()
    async def command_stats(self, ctx):
        command_count = ''
        for key in self.bot.command_stats:
            command_count += (key + ': ' + str(self.bot.command_stats[key]) +
                              '\n')

        await ctx.send(command_count)

    # Loads a cog (requires dot path)
    @commands.command(hidden=True)
    @commands.is_owner()
    async def load(self, ctx, *, cog: str):
        try:
            self.bot.load_extension(cog)
        except Exception as e:
            await ctx.message.add_reaction('❌')
        else:
            await ctx.message.add_reaction('✅')

    # Unloads a cog (requires dot path)
    @commands.command(hidden=True)
    @commands.is_owner()
    async def unload(self, ctx, *, cog: str):
        try:
            self.bot.unload_extension(cog)
        except Exception as e:
            await ctx.message.add_reaction('❌')
        else:
            await ctx.message.add_reaction('✅')

    # Reloads a cog (requires dot path)
    @commands.command(hidden=True)
    @commands.is_owner()
    async def reload(self, ctx, *, cog: str):
        try:
            self.bot.unload_extension(cog)
            self.bot.load_extension(cog)
        except Exception as e:
            await ctx.message.add_reaction('❌')
        else:
            await ctx.message.add_reaction('✅')

    # Shuts the bot down - usable by the bot owner - requires confirmation
    @commands.command(hidden=True)
    @commands.is_owner()
    async def shutdown(self, ctx):
        # Make confirmation message based on bots username to prevent
        # myself from shutting wrong bot down.
        def check(message):
            return (message.content == self.bot.user.name[:4] and
                    str(message.author.id) == str(OWNER_ID))

        try:
            await ctx.send('Respond ' + self.bot.user.name[:4] +
                           ' to shutdown')

            response = await self.bot.wait_for('message', check=check, timeout=10)
            await response.add_reaction('✅')
            await self.bot.logout()
            await self.bot.close()

        except asyncio.TimeoutError:
            pass


def setup(bot):
    bot.add_cog(Owner(bot))
