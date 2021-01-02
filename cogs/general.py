import discord
from discord.ext import commands
from discord.ext.commands.cooldowns import BucketType
import bot_info
import prefixes
from messaging import create_embed
from messaging import create_embed_fields


class General(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    # Try to send a DM to author, otherwise post in channel
    # TODO: change except to dm a message to the user explaining why he couldn't sent message to author
    @staticmethod
    async def dm_author(ctx, message):
        try:
            await ctx.author.send(message)

        except discord.Forbidden:
            await ctx.send(message)

    # Whispers a description of the bot with author, framework, guild count etc.
    # If user has DMs disabled, send the message in the channel
    @commands.command()
    @commands.cooldown(1, 3, BucketType.user)
    async def info(self, ctx):
        await self.dm_author(ctx, bot_info.bot_info + '\n***Currently active '
                                                      'in ' + str(len(self.bot.guilds)) + ' servers***')

    # Whispers a list of the bot commands, If the user has DMs disabled,
    # sends the message in the channel
    @commands.command()
    @commands.cooldown(1, 3, BucketType.user)
    async def help(self, ctx, *, category: str = None):
        # Post general help commands
        if category is None:
            embed_title = 'Rough Soul Bot V0.9r'
            embed_color = 0x4900e5
            embed_author_name = self.bot.user.name
            embed_author_icon_url = str(self.bot.user.avatar_url)
            embed_thumbnail = embed_author_icon_url
            embed_footer = 'Rough Soul'
            embed_message1_description = 'Page 1 of 2'
            embed_message2_description = 'Page 2 of 2'
            embed_message1_field1 = ['**__CORE:__**',
                                     '**help** _Send this list of commands_\n'
                                     '**info** _Send a DM with more info about the bot_\n'
                                     '**prefix** _Show the prefixes available on your server (alias: prefixes)_\n'
                                     '**stats** _Show some of the bot statistics_\n'
                                     '**ping** _Show bot latency_\n'
                                     '**uptime** _Show bot uptime_\n'
                                     '**invite** _Send a DM with an invite link for the bot_\n'
                                     '**source** _Show the link for the bot\'s github repository_\n'
                                     '**update** _Show the last addition to the bot_\n',
                                     False]
            embed_message1_field2 = ['**__Bot Admin:__**',
                                     '**temp_role** _Add a temporary role to a member_\n'
                                     '**add_task** _Add a task to the bot for your server. (Max. 5)_\n'
                                     '**add_bot_admin_role** _Add a Bot Admin Role_\n'
                                     '**delete_bot_admin_role** _Delete Bot Admin Roles_\n'
                                     '**list_bot_admins** _List Bot Admin Roles_\n'
                                     '**add_role** _Add a role to a member_\n'
                                     '**remove_role** _Remove a role form a member_\n'
                                     '**temp_role** _Define a temporary role for a member_\n'
                                     '**delete_temp_role** _Delete the temporary role_\n'
                                     '**list_temp_role** _List the temporary roles_\n'
                                     '**list_tasks** _List the tasks (list_tasks d - list the tasks with details)_\n'
                                     '**delete_task** _Delete a specified task_\n'
                                     '**purge** _Clean the x last messages in the actual text channel_\n'
                                     '**kick** _Kick the member_\n'
                                     '**ban** _Ban the member_\n'
                                     '**move_all** _Move current voice member to target voice channel_\n'
                                     '**move_to_me** _Move member to your voice channel_\n'
                                     '**move_role** _Move voice members that have the role to target voice channel_\n',
                                     False]
            embed_message2_field1 = ['**__Administrator:__**',
                                     '**leave_server** _Allow administrators to make Bot leave the server_\n',
                                     False]
            embed_message2_field2 = ['**__Owner:__**',
                                     '**avatar** _Change the Bot avatar_\n'
                                     '**status** _Change the Bot status/presence_\n'
                                     '**command_stats** _Get the number of all the commands executed_\n'
                                     '**load** _Loads a cog (requires dot path)_\n'
                                     '**unload** _Unloads a cog (requires dot path)_\n'
                                     '**reload** _Reloads a cog (requires dot path)_\n'
                                     '**join** _Makes the bot join the voice channel_\n'
                                     '**leave** _Makes the bot leave the voice channel_\n'
                                     '**shutdown** _Shuts the bot down - requires confirmation_\n',
                                     False]

            embed_message1_fields = await create_embed_fields(embed_message1_field1, embed_message1_field2)
            embed_message2_fields = await create_embed_fields(embed_message2_field1, embed_message2_field2)
            embed_message1 = await create_embed(embed_title, embed_message1_description, embed_color, embed_author_name,
                                                embed_author_icon_url, embed_thumbnail, embed_footer,
                                                embed_message1_fields)
            embed_message2 = await create_embed(embed_title, embed_message2_description, embed_color, embed_author_name,
                                                embed_author_icon_url, embed_thumbnail, embed_footer,
                                                embed_message2_fields)
            await ctx.author.send(embed=embed_message1)
            await ctx.author.send(embed=embed_message2)

    # DM user with an invite link for the bot
    @commands.command()
    @commands.cooldown(1, 3, BucketType.user)
    async def invite(self, ctx):
        await self.dm_author(ctx, 'You can add me to your own server using the link below:\n'
                                  '<https://discord.com/api/oauth2/authorize?client_id=' + str(self.bot.user.id) +
                             '&permissions=2147482999&scope=bot>')

    # Sends url to RSMBot github repo
    @commands.command(aliases=['github', 'repo'])
    @commands.cooldown(1, 3, BucketType.user)
    async def source(self, ctx):
        await ctx.send('Github Repo Source: \n'
                       '<https://github.com/GSecurity/Rough-Soul-Bot>')

    # Display information regarding the last update
    @commands.command()
    @commands.cooldown(1, 3, BucketType.user)
    async def update(self, ctx):
        await ctx.send("I'm being heavily reworked. But here are the last improvements:\n"
                       "- Removed the need of initial setup from owner/admin (Done)\n"
                       "- Restructurized the way server data/config are stored (Done)\n"
                       "- Reworked the bot bases functionality / cleanup (~90%)\n"
                       "- Reworked the task system (~95%)\n"
                       "- Added list task function (Done)\n"
                       "- Reworked the temporary role function (Done)\n"
                       "- Added list temporary role function (Done)\n"
                       "- Reworked the add bot admin role function (Done)\n"
                       "- Added list bot admin role function (Done)\n"
                       "- Added give role function (Done)\n"
                       "- Added remove role function (Done)\n"
                       "- Added new check for commands permission (admin or higher perms) (done)\n"
                       "- Added a purge function (Delete x previous messages in channel) (Done)\n"
                       "- Added a test message function (Owner only) (Done)\n"
                       "- Added Bot's repo in the source command. Files will be uploaded soon (Done)\n"
                       "- Updated Bot's invite link from the invite command (Done)\n"
                       "- Reworked the help function (Done)\n"
                       "- Updating the help function content (~40%)\n"
                       "- Added kick command\n"
                       "- Added ban command\n"
                       "- Added move_all command\n"
                       "- Added move_to_me command\n"
                       "- Added move_role command\n"
                       "- Max allowed tasks per server is now 10 (was 5)\n"
                       "\n"
                       "As the bot keeps evolving in the future, so will the current and new features.\n")

    # Allow administrators to make RSMBot leave the server
    @commands.command()
    @commands.guild_only()
    @commands.has_permissions(administrator=True)
    async def leave_server(self, ctx):
        await ctx.send('Leaving server. Goodbye! 👋')
        await ctx.guild.leave()

    # Display the prefixes used on the current guild
    @commands.command(aliases=['prefixes'])
    @commands.cooldown(1, 3, BucketType.channel)
    async def prefix(self, ctx):
        guild_prefixes = prefixes.prefixes_for(ctx.message.guild,
                                               self.bot.prefix_data)
        if len(guild_prefixes) > 1:
            await ctx.send('This servers prefixes are: `rsm` and `' +
                           guild_prefixes[-1] + '`.')

        else:
            await ctx.send('This servers prefixes are: `rsm`.')

    # Allows for a single custom prefix per-guild
    @commands.command()
    @commands.guild_only()
    # @commands.has_permissions(manage_guild=True)
    @commands.is_owner()
    @commands.cooldown(3, 60, BucketType.guild)
    async def setprefix(self, ctx, *, new_prefix: str = None):
        guild_index = prefixes.find_guild(ctx.message.guild,
                                          self.bot.prefix_data)
        # Require entering a prefix
        if new_prefix is None:
            await ctx.send('You did not provide a new prefix.')

        # Limit prefix to 10 characters, may increase
        elif len(new_prefix) > 10:
            await ctx.send('Custom server prefix too long (Max 10 chars).')

        elif self.bot.prefix_data[guild_index]['prefix'] == new_prefix:
            await ctx.send('This server custom prefix is already `' +
                           new_prefix + '`.')

        # Add a new custom guild prefix if one doesn't already exist
        elif guild_index == -1:
            self.bot.prefix_data.append(
                {'guildID': ctx.message.guild.id,
                 'prefix': new_prefix}
            )
            prefixes.write_prefixes(self.bot.prefix_data)
            await ctx.send('This servers custom prefix changed to `'
                           + new_prefix + '`.')

        # Otherwise, modify the current prefix to the new one
        else:
            self.bot.prefix_data[guild_index]['prefix'] = new_prefix
            prefixes.write_prefixes(self.bot.prefix_data)
            await ctx.send('This servers custom prefix changed to `' +
                           new_prefix + '`.')

    # Join command
    @commands.command(hidden=True)
    @commands.is_owner()
    async def join(self, ctx, voice_channel: discord.VoiceChannel):
        if voice_channel is not None:
            await voice_channel.connect()
            print('Joined voice channel.')
        else:
            print('Voice channel not found')
            await ctx.send('Voice channel not found')

    # Leave command
    @commands.command(hidden=True)
    @commands.is_owner()
    async def leave(self, ctx):
        if ctx.voice_client:
            await ctx.voice_client.disconnect()
            print('Disconnected from voice channel.')
        else:
            print('Bot is not in a voice channel')


def setup(bot):
    bot.add_cog(General(bot))
