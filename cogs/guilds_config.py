"""This Cog is to create the basic setup of the bot for a guild"""

import json
import asyncio
import discord
from os import makedirs
from os.path import isfile
from os.path import isdir
from discord.ext import commands
from messaging import create_embed
from settings.config import OWNER_ID
from messaging import create_embed_fields

# Define Class to configure Guilds
# TODO: Add logging to file (setup.log)
class GuildsConfig(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.path = 'cogs/data/'
        self.admin_role_config_file = 'admins.json'
        self.text_channel_config_file = 'textChannel.json'
        self.voice_channel_config_file = 'voiceChannel.json'
        self.embed_title = 'Rough Soul Bot Setup'
        self.embed_color = 0x4900e5
        self.embed_author_name = ''
        self.embed_author_icon_url = ''
        self.embed_thumbnail = ''
        self.embed_footer = 'Rough Soul'

    @commands.Cog.listener()
    async def on_ready(self):
        self.embed_author_name = self.bot.user.name
        self.embed_author_icon_url = str(self.bot.user.avatar_url)
        self.embed_thumbnail = self.embed_author_icon_url

    def exception_handler(func):
        async def func_wrapper(*args, **kwargs):
            try:
                await func(*args, **kwargs)
            except discord.NotFound:
                self = args[0]
                ctx = args[1]

                print('404 Message Not Found. (Probably deleted by someone)')
                embed_description = '** ⚠ Setup Message Deleted ⚠ **'
                embed_field1 = ['Someone deleted the Bot Setup Message.',
                                'Please, do not delete the Bot message while the setup is running.\n'
                                'Ending Setup in 5 sec...', False]
                embed_fields = await create_embed_fields(embed_field1)
                embed_message = await create_embed(self.embed_title, embed_description, self.embed_color,
                                                   self.embed_author_name,
                                                   self.embed_author_icon_url, self.embed_thumbnail,
                                                   self.embed_footer, embed_fields)
                message_with_embed = await ctx.send(embed=embed_message)
                await asyncio.sleep(5)
                # await GuildsConfig.delete_messages(GuildsConfig.ctx, message_id_list)
                print('Ending process...')
                await GuildsConfig.setup_menu(self, ctx, 7, message_with_embed)
        return func_wrapper

    # Setup the config for the current guild and store in json file
    # TODO: Add ability to have other Roles do the settings per Guild
    @commands.is_owner()
    @commands.command(name="setup_guild", aliases=['sg'], hidden=True)
    async def setup_guild(self, ctx):
        await ctx.message.delete()
        await self.setup_menu(ctx, 1)

    @staticmethod
    def check(message):
        return (message.content == message.content and
                str(message.author.id) == str(OWNER_ID))

    async def setup_menu(self, ctx, list_number, message_with_embed=None):
        switcher = {
            1: self.setup_init,
            2: self.set_admin_role,
            3: self.set_text_channel,
            4: self.set_voice_channel,
            5: self.setup_finish,
            6: self.setup_timeout,
            7: self.setup_canceled,
        }
        # Get function from switcher dictionary
        func = switcher.get(list_number, lambda: 'Invalid input')
        # Execute the function
        if message_with_embed is None:
            await func(ctx)
        else:
            await func(ctx, message_with_embed)

    async def create_menu_embed(self):
        embed_description = '__You will need to setup 3 settings:__'
        embed_field1 = ['Admin Role', 'Set the bot Main Admin Role.', True]
        embed_field2 = ['Text Channel', 'Set the Text Channel for Announcements', True]
        embed_field3 = ['Voice Channel', 'Set the Voice Channel for Announcements', True]
        embed_field4 = ['__Stopping the process:__', 'If you want to stop in the middle of the process, '
                                                     'Just don\'t answer the bot for 30 seconds.', False]
        embed_field5 = ['Should we start ?', '(y/n)', False]

        embed_fields = await create_embed_fields(embed_field1, embed_field2, embed_field3, embed_field4, embed_field5)

        embed_message = await create_embed(self.embed_title, embed_description, self.embed_color,
                                           self.embed_author_name, self.embed_author_icon_url, self.embed_thumbnail,
                                           self.embed_footer, embed_fields)
        return embed_message

    @exception_handler
    async def setup_init(self, ctx):
        message_id_list = []
        if isdir(self.path):
            if isfile(self.path + str(ctx.guild.id) + '/' + self.admin_role_config_file) or \
                    isfile(self.path + str(ctx.guild.id) + '/' + self.text_channel_config_file) or \
                    isfile(self.path + str(ctx.guild.id) + '/' + self.voice_channel_config_file):
                embed_description = '** ⚠ One or more config file(s) have been found! ⚠ **'
                embed_field1 = ['Are you sure you want to continue with the setup process?',
                                'Doing so will overwrite the actual file(s)', False]
                embed_field2 = ['Continue?', '(y/n)', False]
                embed_fields = await create_embed_fields(embed_field1, embed_field2)
                embed_message = await create_embed(self.embed_title, embed_description, self.embed_color,
                                                   self.embed_author_name, self.embed_author_icon_url,
                                                   self.embed_thumbnail,
                                                   self.embed_footer, embed_fields)
                message_with_embed = await ctx.send(embed=embed_message)
                try:
                    response = await self.bot.wait_for('message', check=self.check, timeout=30)
                    if response.content.lower() == 'y':
                        message_id_list.append(response.id)
                        await self.delete_messages(ctx, message_id_list)
                        print('Setup Config File(s) Found Warning messages deleted. Starting setup...')
                        await self.start_setup(ctx, message_with_embed)
                    elif response.content.lower() == 'n':
                        print('User canceled the setup (config file(s) found).')
                        message_id_list.append(response.id)
                        await self.delete_messages(ctx, message_id_list)
                        print('All setup messages deleted. Ending process...')
                        await self.setup_menu(ctx, 7, message_with_embed)
                    else:
                        print('User gave an incorrect answer.')
                        embed_description = '❌ **Invalid answer, taking it as a No.** ❌'
                        embed_message = await create_embed(self.embed_title, embed_description, self.embed_color,
                                                           self.embed_author_name,
                                                           self.embed_author_icon_url, self.embed_thumbnail,
                                                           self.embed_footer)
                        await message_with_embed.edit(embed=embed_message)
                        await asyncio.sleep(2)
                        await self.delete_messages(ctx, message_id_list)
                        print('All setup messages deleted. Ending process...')
                        await self.setup_menu(ctx, 7, message_with_embed)
                except asyncio.TimeoutError:
                    print('Timeout...')
                    await self.delete_messages(ctx, message_id_list)
                    print('All setup messages deleted. Ending process...')
                    await self.setup_menu(ctx, 6, message_with_embed)
            else:
                await self.start_setup(ctx)
        else:
            await self.start_setup(ctx)

    # Start the setup
    @exception_handler
    async def start_setup(self, ctx, message_with_embed=None):
        message_id_list = []
        # try:
        if message_with_embed is None:
            embed_message = await self.create_menu_embed()
            message_with_embed = await ctx.send(embed=embed_message)
        else:
            embed_message = await self.create_menu_embed()
            await message_with_embed.edit(embed=embed_message)
        try:
            response = await self.bot.wait_for('message', check=self.check, timeout=30)
            if response.content.lower() == 'y':
                message_id_list.append(response.id)
                await self.delete_messages(ctx, message_id_list)
                print('All start_setup setup messages deleted. Starting setup_menu 2...')
                await self.setup_menu(ctx, 2, message_with_embed)
            elif response.content.lower() == 'n':
                print('User canceled the setup.')
                message_id_list.append(response.id)
                await self.delete_messages(ctx, message_id_list)
                print('All setup messages deleted. Ending process...')
                await self.setup_menu(ctx, 7, message_with_embed)
            else:
                print('User gave an incorrect answer.')
                embed_description = '❌ **Invalid answer, taking it as a No.** ❌'
                embed_message = await create_embed(self.embed_title, embed_description, self.embed_color,
                                                   self.embed_author_name,
                                                   self.embed_author_icon_url, self.embed_thumbnail,
                                                   self.embed_footer)
                await message_with_embed.edit(embed=embed_message)
                await asyncio.sleep(2)
                await self.delete_messages(ctx, message_id_list)
                print('All setup messages deleted. Ending process...')
                await self.setup_menu(ctx, 7, message_with_embed)
        except asyncio.TimeoutError:
            print('Timeout...')
            await self.delete_messages(ctx, message_id_list)
            print('All setup messages deleted. Ending process...')
            await self.setup_menu(ctx, 6, message_with_embed)
        # except discord.NotFound:
        #     print('404 Message Not Found. (Probably deleted by someone)')
        #     embed_description = '** ⚠ Setup Message Deleted ⚠ **'
        #     embed_field1 = ['Someone deleted the Bot Setup Message.',
        #                     'Please, do not delete the Bot message while the setup is running.\n'
        #                     'Ending Setup in 5 sec...', False]
        #     embed_fields = await create_embed_fields(embed_field1)
        #     embed_message = await create_embed(self.embed_title, embed_description, self.embed_color,
        #                                        self.embed_author_name,
        #                                        self.embed_author_icon_url, self.embed_thumbnail,
        #                                        self.embed_footer, embed_fields)
        #     message_with_embed = await ctx.send(embed=embed_message)
        #     await asyncio.sleep(5)
        #     await self.delete_messages(ctx, message_id_list)
        #     print('Ending process...')
        #     await self.setup_menu(ctx, 7, message_with_embed)

    # Set and save the main admin role of the bot for this server
    @exception_handler
    async def set_admin_role(self, ctx, message_with_embed):
        message_id_list = []
        admin_role = {}
        embed_description = '**Please enter the bot __Main Admin Role__ that should be used:**'
        embed_message = await create_embed(self.embed_title, embed_description, self.embed_color,
                                           self.embed_author_name,
                                           self.embed_author_icon_url, self.embed_thumbnail, self.embed_footer)
        # try:
        while True:
            await message_with_embed.edit(embed=embed_message)
            try:
                response = await self.bot.wait_for('message', check=self.check, timeout=30)
                message_id_list.append(response.id)
                roles = ctx.guild.roles
                if [response.content for role in roles if response.content == role.name]:
                    admin_role['admin_role_id'] = next(role.id for role in roles if response.content == role.name)
                    if admin_role:
                        status = 3
                        break
                    else:
                        print('Something went wrong! admin_role shouldn\'t be empty!')
                        status = 7
                        break
                else:
                    print(f'❌ The role "{response.content}" was not found on the server.')
                    await self.delete_messages(ctx, message_id_list)
                    embed_field1 = [f'❌ The role "{response.content}" was not found on your server.',
                                    'Please try again or wait 30 sec to cancel setup process.', False]
                    embed_fields = await create_embed_fields(embed_field1)
                    embed_message = await create_embed(self.embed_title, embed_description, self.embed_color,
                                                       self.embed_author_name,
                                                       self.embed_author_icon_url, self.embed_thumbnail,
                                                       self.embed_footer, embed_fields)
                    await message_with_embed.edit(embed=embed_message)
            except asyncio.TimeoutError:
                status = 6
                break

        if status == 3:
            print('Deleting setup messages...')
            await self.delete_messages(ctx, message_id_list)
            await asyncio.sleep(1)
            embed_description = f'Saving the role ID "{admin_role["admin_role_id"]}"...'
            embed_message = await create_embed(self.embed_title, embed_description, self.embed_color,
                                               self.embed_author_name,
                                               self.embed_author_icon_url, self.embed_thumbnail,
                                               self.embed_footer)
            await message_with_embed.edit(embed=embed_message)
            makedirs(self.path + str(ctx.guild.id), exist_ok=True)
            self.write_main_admin_role(ctx.guild.id, admin_role)
            print(f'Main admin role ID {admin_role["admin_role_id"]} saved to '
                  f'{self.path}{ctx.guild.id}/{self.admin_role_config_file}.')
            print('All set_admin_role setup messages deleted. Starting setup_menu 3...')
            await self.setup_menu(ctx, 3, message_with_embed)
        elif status == 6:
            print('Timeout...')
            await self.delete_messages(ctx, message_id_list)
            print('All setup messages deleted. Ending process...')
            await self.setup_menu(ctx, 6, message_with_embed)
        elif status == 7:
            await self.delete_messages(ctx, message_id_list)
            print('All setup messages deleted. Ending process...')
            await self.setup_menu(ctx, 7, message_with_embed)
        else:
            print('Something went really wrong! Check your code.')
            await self.delete_messages(ctx, message_id_list)
            print('All setup messages deleted. Ending process...')
            await self.setup_menu(ctx, 7, message_with_embed)

    # Set text channel
    @exception_handler
    async def set_text_channel(self, ctx, message_with_embed):
        message_id_list = []
        text_channel = {}
        embed_description = '**Please enter the __Text Channel__ name that should be used:**'

        embed_message = await create_embed(self.embed_title, embed_description, self.embed_color,
                                           self.embed_author_name,
                                           self.embed_author_icon_url, self.embed_thumbnail, self.embed_footer)
        while True:
            await message_with_embed.edit(embed=embed_message)
            try:
                response = await self.bot.wait_for('message', check=self.check, timeout=30)
                message_id_list.append(response.id)
                text_channels = ctx.guild.text_channels
                if [response.content for text_channel in text_channels if response.content == text_channel.name]:
                    text_channel['text_channel_id'] = next(text_channel.id for text_channel in text_channels
                                                           if response.content == text_channel.name)
                    if text_channel:
                        status = 4
                        break
                    else:
                        print('Something went wrong! text_channel shouldn\'t be empty!')
                        status = 7
                        break
                else:
                    print(f'❌ The text channel "{response.content}" was not found on the server.')
                    await self.delete_messages(ctx, message_id_list)
                    embed_field1 = [f'❌ The text channel "{response.content}" was not found on your server.',
                                    'Please try again or wait 30 sec to cancel setup process.', False]
                    embed_fields = await create_embed_fields(embed_field1)
                    embed_message = await create_embed(self.embed_title, embed_description, self.embed_color,
                                                       self.embed_author_name,
                                                       self.embed_author_icon_url, self.embed_thumbnail,
                                                       self.embed_footer, embed_fields)
                    await message_with_embed.edit(embed=embed_message)
            except asyncio.TimeoutError:
                status = 6
                break
        if status == 4:
            print('Deleting setup messages...')
            await self.delete_messages(ctx, message_id_list)
            await asyncio.sleep(1)
            embed_description = f'Saving the text channel ID "{text_channel["text_channel_id"]}"...'
            embed_message = await create_embed(self.embed_title, embed_description, self.embed_color,
                                               self.embed_author_name,
                                               self.embed_author_icon_url, self.embed_thumbnail,
                                               self.embed_footer)
            await message_with_embed.edit(embed=embed_message)
            makedirs(self.path + str(ctx.guild.id), exist_ok=True)
            self.write_text_channel(ctx.guild.id, text_channel)
            print(f'Text channel {text_channel["text_channel_id"]} saved to '
                  f'{self.path}{ctx.guild.id}/{self.text_channel_config_file}.')
            print('All set_text_channel setup messages deleted. Starting setup_menu 4...')
            await self.setup_menu(ctx, 4, message_with_embed)
        elif status == 6:
            print('Timeout...')
            await self.delete_messages(ctx, message_id_list)
            print('All setup messages deleted. Ending process...')
            await self.setup_menu(ctx, 6, message_with_embed)
        elif status == 7:
            await self.delete_messages(ctx, message_id_list)
            print('All setup messages deleted. Ending process...')
            await self.setup_menu(ctx, 7, message_with_embed)
        else:
            print('Something went really wrong! Check your code.')
            await self.delete_messages(ctx, message_id_list)
            print('All setup messages deleted. Ending process...')
            await self.setup_menu(ctx, 7, message_with_embed)

    # set voice channel
    @exception_handler
    async def set_voice_channel(self, ctx, message_with_embed):
        message_id_list = []
        voice_channel = {}
        embed_description = '**Please enter the __Voice Channel__ name that should be used:**'

        embed_message = await create_embed(self.embed_title, embed_description, self.embed_color,
                                           self.embed_author_name,
                                           self.embed_author_icon_url, self.embed_thumbnail, self.embed_footer)
        while True:
            await message_with_embed.edit(embed=embed_message)
            try:
                response = await self.bot.wait_for('message', check=self.check, timeout=30)
                message_id_list.append(response.id)
                voice_channels = ctx.guild.voice_channels
                if [response.content for voice_channel in voice_channels if response.content == voice_channel.name]:
                    voice_channel['voice_channel_id'] = next(voice_channel.id for voice_channel in voice_channels
                                                             if response.content == voice_channel.name)
                    if voice_channel:
                        status = 5
                        break
                    else:
                        print('Something went wrong! text_channel shouldn\'t be empty!')
                        status = 7
                        break
                else:
                    print(f'❌ The voice channel "{response.content}" was not found on the server.')
                    await self.delete_messages(ctx, message_id_list)
                    embed_field1 = [f'❌ The voice channel "{response.content}" was not found on your server.',
                                    'Please try again or wait 30 sec to cancel setup process.', False]
                    embed_fields = await create_embed_fields(embed_field1)
                    embed_message = await create_embed(self.embed_title, embed_description, self.embed_color,
                                                       self.embed_author_name,
                                                       self.embed_author_icon_url, self.embed_thumbnail,
                                                       self.embed_footer, embed_fields)
                    await message_with_embed.edit(embed=embed_message)
            except asyncio.TimeoutError:
                status = 6
                break
        if status == 5:
            print('Deleting setup messages...')
            await self.delete_messages(ctx, message_id_list)
            await asyncio.sleep(1)
            embed_description = f'Saving the text channel ID "{voice_channel["voice_channel_id"]}"...'
            embed_message = await create_embed(self.embed_title, embed_description, self.embed_color,
                                               self.embed_author_name,
                                               self.embed_author_icon_url, self.embed_thumbnail,
                                               self.embed_footer)
            await message_with_embed.edit(embed=embed_message)
            makedirs(self.path + str(ctx.guild.id), exist_ok=True)
            self.write_voice_channel(ctx.guild.id, voice_channel)
            print(f'Voice channel {voice_channel["voice_channel_id"]} saved to '
                  f'{self.path}{ctx.guild.id}/{self.voice_channel_config_file}.')
            print('All set_voice_channel setup messages deleted. Starting setup_menu 5...')
            await self.setup_menu(ctx, 5, message_with_embed)
        elif status == 6:
            print('Timeout...')
            await self.delete_messages(ctx, message_id_list)
            print('All setup messages deleted. Ending process...')
            await self.setup_menu(ctx, 6, message_with_embed)
        elif status == 7:
            await self.delete_messages(ctx, message_id_list)
            print('All setup messages deleted. Ending process...')
            await self.setup_menu(ctx, 7, message_with_embed)
        else:
            print('Something went really wrong! Check your code.')
            await self.delete_messages(ctx, message_id_list)
            print('All setup messages deleted. Ending process...')
            await self.setup_menu(ctx, 7, message_with_embed)

    @exception_handler
    async def setup_finish(self, ctx, message_with_embed=None):
        message_id_list = []
        if isfile(self.path + str(ctx.guild.id) + '/' + self.admin_role_config_file) and \
                isfile(self.path + str(ctx.guild.id) + '/' + self.text_channel_config_file) and \
                isfile(self.path + str(ctx.guild.id) + '/' + self.voice_channel_config_file):
            embed_description = 'Finishing Setup'
            embed_field1 = ['✅ Tank you. Setup is now finished. ✅', 'Cleaning up chat in 5 sec....', False]
            embed_fields = await create_embed_fields(embed_field1)
            embed_message = await create_embed(self.embed_title, embed_description, self.embed_color,
                                               self.embed_author_name,
                                               self.embed_author_icon_url, self.embed_thumbnail,
                                               self.embed_footer, embed_fields)
            await message_with_embed.edit(embed=embed_message)
            message_id_list.append(message_with_embed.id)
            print('Setup finished, all file present on drive.')
            await asyncio.sleep(5)
            await self.delete_messages(ctx, message_id_list)
            print('All setup messages deleted. Process finished.')
        else:
            embed_description = '❌ Something went wrong. Please try again.'
            embed_message = await create_embed(self.embed_title, embed_description, self.embed_color,
                                               self.embed_author_name,
                                               self.embed_author_icon_url, self.embed_thumbnail,
                                               self.embed_footer)
            await message_with_embed.edit(embed=embed_message)
            await asyncio.sleep(2)
            await self.delete_messages(ctx, message_id_list)
            print('All setup messages deleted. Ending process...')
            await self.setup_menu(ctx, 7, message_with_embed)

    # @staticmethod
    @exception_handler
    async def setup_timeout(self, ctx, message_with_embed=None):
        print('Timeout. Setup process canceled.')
        embed_description = '❌ **Timeout. Setup process canceled.** ❌\nCleaning up chat in 5 sec....'
        embed_message = await create_embed(self.embed_title, embed_description, self.embed_color,
                                           self.embed_author_name,
                                           self.embed_author_icon_url, self.embed_thumbnail,
                                           self.embed_footer)
        await message_with_embed.edit(embed=embed_message)
        await asyncio.sleep(5)
        await message_with_embed.delete()
        print('Timeout message deleted. Process finished.')
        pass

    # @staticmethod
    @exception_handler
    async def setup_canceled(self, ctx, message_with_embed=None):
        print('Setup process canceled.')
        embed_description = '❌ **Setup process canceled.** ❌\nCleaning up chat in 5 sec....'
        embed_message = await create_embed(self.embed_title, embed_description, self.embed_color,
                                           self.embed_author_name,
                                           self.embed_author_icon_url, self.embed_thumbnail,
                                           self.embed_footer)
        await message_with_embed.edit(embed=embed_message)
        await asyncio.sleep(5)
        await message_with_embed.delete()
        print('Setup process cancel message deleted. Process finished.')
        pass

    # Write the main admin role for this server in admins.json file.
    # /!\ This function will overwrite the file and ignore all existing added admin roles /!\
    # @staticmethod
    def write_main_admin_role(self, guild_id, admin_role_info):
        with open(self.path + str(guild_id) + '/' + self.admin_role_config_file, 'w') as admin_list:
            json.dump(admin_role_info, admin_list, indent=4)
            admin_list.close()

    # Write the text channel used for announcements in textChannel.json
    # @staticmethod
    def write_text_channel(self, guild_id, text_channel_info):
        with open(self.path + str(guild_id) + '/' + self.text_channel_config_file, 'w') as text_channel_list:
            json.dump(text_channel_info, text_channel_list, indent=4)
            text_channel_list.close()

    # Write the text channel used for announcements in textChannel.json
    # @staticmethod
    def write_voice_channel(self, guild_id, voice_channel_info):
        with open(self.path + str(guild_id) + '/' + self.voice_channel_config_file, 'w') as voice_channel_list:
            json.dump(voice_channel_info, voice_channel_list, indent=4)
            voice_channel_list.close()

    @staticmethod
    async def delete_messages(ctx, message_id_list):
        print('Deleting messages...')
        for message_id in message_id_list:
            try:
                msg = await ctx.message.channel.fetch_message(message_id)
                await msg.delete()
            except discord.DiscordException:
                pass

    # async def set_temp_role():
    #     await ctx.send('Please enter the temporary role that should be used:')
    #     try:
    #         response = await self.bot.wait_for('message', check=check,
    #                                            timeout=30)
    #         # role = discord.utils.get(ctx.guild.roles, name='Temp')
    #         if discord.utils.get(ctx.guild.roles, name=response.content):
    #             setup_guild_data['temp_role'] = response.content
    #             # await ctx.message.add_reaction('✅')
    #             await ctx.send('✅')
    #             print(setup_guild_data['temp_role'])
    #             await setup_menu(3)
    #         else:
    #             # await response.add_reaction('❌')
    #             await ctx.send('❌ This role does not exist on your server.')
    #             await setup_menu(2)
    #     except asyncio.TimeoutError:
    #         await setup_menu(6)

    # # Read the Guilds config from json file
    # @staticmethod
    # def read_guilds_config(guild_id):
    #     with open('data/guildConfigs.json', 'r') as guilds_config_list:
    #         guilds_config_data = json.load(guilds_config_list)
    #         guilds_config_list.close()
    #
    #     return guilds_config_data


def setup(bot):
    bot.add_cog(GuildsConfig(bot))
