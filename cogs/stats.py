import discord
import datetime
from discord.ext import commands
from discord.ext.commands.cooldowns import BucketType


class Stats(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    # Get the uptime of the bot. In a short description format by default.
    def get_uptime(self, full=False):
        current_time = datetime.datetime.utcnow()
        delta = current_time - self.bot.uptime
        hours, remainder = divmod(int(delta.total_seconds()), 3600)
        minutes, seconds = divmod(remainder, 60)
        days, hours = divmod(hours, 24)

        if full:
            return ('{} days, {} hours, {} minutes, and {} seconds'.
                    format(days, hours, minutes, seconds))

        else:
            return ('{}d {}h {}m {}s'.
                    format(days, hours, minutes, seconds))

    # Posts the bots uptime to the channel
    @commands.command()
    @commands.cooldown(1, 3, BucketType.user)
    async def uptime(self, ctx):
        await ctx.send('🔌 Uptime: **' + self.get_uptime(True) + '**')

    # Check the latency of the bot
    @commands.command()
    @commands.cooldown(1, 3, BucketType.channel)
    async def ping(self, ctx):
        latency = round(self.bot.latency * 1000, 2)
        await ctx.send('🏓 Latency: ' + str(latency) + 'ms')

    # Display statistics for the bot
    @commands.command(aliases=['statistics'])
    @commands.cooldown(1, 3, BucketType.channel)
    async def stats(self, ctx):
        # Count users online in guilds and user average
        total_members = 0
        online_users = 0
        for guild in self.bot.guilds:
            total_members += len(guild.members)
            for member in guild.members:
                if member.status == discord.Status.online:
                    online_users += 1
        user_average = round((online_users / len(self.bot.guilds)), 2)
        guild_count = str(len(self.bot.guilds))

        # Count number of commands executed
        command_count = 0
        for key in self.bot.command_stats:
            command_count += self.bot.command_stats[key]

        # Embed statistics output
        embed = discord.Embed(colour=discord.Colour(0x44981e))
        embed.set_thumbnail(url=self.bot.user.avatar_url)
        embed.set_author(name=self.bot.user.name + ' Statistics',
                         url='https://www.roughsoul.community',
                         icon_url=self.bot.user.avatar_url)

        # Add all statistics
        # embed.add_field(name='Bot Owner', value='Jaiseck#0001', inline=True)
        embed.add_field(name='Bot Owner', value='<@105630062618931200>', inline=True)
        embed.add_field(name='Server Count', value=guild_count, inline=True)
        embed.add_field(name='Total Members', value=total_members, inline=True)
        embed.add_field(name='Online Users', value=online_users, inline=True)
        embed.add_field(name='Average Online', value=user_average, inline=True)
        embed.add_field(name='Uptime', value=self.get_uptime(), inline=True)
        embed.add_field(name='Commands Used', value=command_count, inline=True)
        await ctx.send(embed=embed)


def setup(bot):
    bot.add_cog(Stats(bot))
