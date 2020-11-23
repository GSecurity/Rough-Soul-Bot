import os
import errno
import json
import asyncio
import discord
import admins
import datetime as dt
import cogs.admin as adm
from discord.ext import commands
from settings.config import OWNER_ID


# Define Class for giving temporary roles
class TempRole(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.path = 'cogs/data/'
        self.temp_roles_config_file = 'tempRoles.json'
        self.check_temp_role_task = ''

    async def check_temp_role(self):
        await self.bot.wait_until_ready()

        while not self.bot.is_closed():
            print(f'{dt.datetime.now().day}-{dt.datetime.now().month}-{dt.datetime.now().year} {dt.datetime.now().hour}:{dt.datetime.now().minute}:{dt.datetime.now().second}'
                  f' - Checking temporary roles...')
            # get actual date and time
            testnow = dt.datetime.now()
            temp_role_data = []
            temporary_temp_role_data = []
            guild_ids = admins.read_guilds_ids()
            for guild_id in guild_ids:
                temp_role_data = self.read_temp_roles(guild_id)
                temporary_temp_role_data = self.read_temp_roles(guild_id)
                guild_data = self.bot.get_guild(int(guild_id))
                print(f'{dt.datetime.now().day}-{dt.datetime.now().month}-{dt.datetime.now().year} {dt.datetime.now().hour}:{dt.datetime.now().minute}:'
                      f'{dt.datetime.now().second} - Checking temporary roles for server: {guild_data.name}:{guild_data.id}')
                for index in range(len(temp_role_data)):
                    # check if the time stored is smaller than the actual time
                    if dt.datetime.strptime(temp_role_data[index]['time'],
                                            "%Y-%m-%d %H:%M:%S.%f") < testnow:
                        member = discord.utils.get(guild_data.members, id=temp_role_data[index]['member_id'])
                        role = discord.utils.get(guild_data.roles, id=temp_role_data[index]['role_id'])
                        if member:
                            if role:
                                print(f'Removing role for {member.name}:{member.id}')
                                await member.remove_roles(role)
                                print(f'Deleting list entry for this member+temp_role in json')
                                del temporary_temp_role_data[index]
                                print(f'Saving current config to json for guild  {guild_data.name}:{guild_id}')
                                self.write_temp_roles(guild_data.id, temporary_temp_role_data)
                                print('Saving done')
                            else:
                                print(f'Role "{temp_role_data[index]["role_id"]}" does not exist anymore')
                                print(f'Deleting list entry for this member+temp_role in json')
                                del temporary_temp_role_data[index]
                                print(f'Saving current config to json for guild  {guild_data.name}:{guild_id}')
                                self.write_temp_roles(guild_data.id, temporary_temp_role_data)
                                print('Saving done')
                        else:
                            print(f'Member {temp_role_data[index]["member_id"]} is no more on this server: '
                                  f'{guild_data.name}:{guild_data.id}')
                            print('Deleting list entry for this member+temp_role in json')
                            del temporary_temp_role_data[index]
                            print(f'Saving current config to json for guild  {guild_data.name}:{guild_id}')
                            self.write_temp_roles(guild_data.id, temporary_temp_role_data)
                            print('Saving done')
            print(f'{dt.datetime.now().day}-{dt.datetime.now().month}-{dt.datetime.now().year} {dt.datetime.now().hour}:{dt.datetime.now().minute}:{dt.datetime.now().second}'
                  f' - Done checking temporary roles')
            # pause loop
            await asyncio.sleep(60)

    @commands.Cog.listener()
    async def on_ready(self):
        self.check_temp_role_task = self.bot.loop.create_task(self.check_temp_role())
        print('Task CHK_TMP_ROLE started.')

    @commands.guild_only()
    @commands.is_owner()
    @commands.command(name='start_temp_role_check', aliases=['statrc'], hidden=True)
    async def start_temp_role_check(self, ctx):
        self.check_temp_role_task = self.bot.loop.create_task(self.check_temp_role())
        print('Task CHK_TMP_ROLE Started.')
        await ctx.send('Task CHK_TMP_ROLE started.')

    @commands.guild_only()
    @commands.is_owner()
    @commands.command(name='stop_temp_role_check', aliases=['stotrc'], hidden=True)
    async def stop_temp_role_check(self, ctx):
        self.check_temp_role_task.cancel()
        print('Task CHK_TMP_ROLE Stopped')
        await ctx.send('Task CHK_TMP_ROLE stopped.')

    # Write temporary role in tempRoles.json
    def write_temp_roles(self, guild_id, temp_role_data):
        with open(self.path + str(guild_id) + '/' + self.temp_roles_config_file, 'w') as temp_role_list:
            json.dump(temp_role_data, temp_role_list, indent=4)
            temp_role_list.close()

    # Read the tempRoles.json file for the specified guild
    def read_temp_roles(self, guild_id):
        temp_roles = []
        file_path = self.path + str(guild_id) + '/' + self.temp_roles_config_file
        try:
            with open(file_path, 'r') as temp_roles_file:
                temp_roles = json.load(temp_roles_file)
                temp_roles_file.close()
        except FileNotFoundError:
            print('File does not exist or was not found, creating it.')
            if not os.path.exists(os.path.dirname(file_path)):
                try:
                    os.makedirs(os.path.dirname(file_path))
                except OSError as exc:  # Guard against race condition
                    if exc.errno != errno.EEXIST:
                        raise
            with open(file_path, 'w') as temp_role_file:
                json.dump(temp_roles, temp_role_file, indent=4)
                temp_role_file.close()
        return temp_roles


def setup(bot):
    bot.add_cog(TempRole(bot))
