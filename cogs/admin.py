import os
import errno
import json
import asyncio
import datetime
import discord
import admins
from discord.ext import commands
from settings.config import OWNER_ID

guild_ids_list = admins.read_guilds_ids()


class Admin(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.path = 'cogs/data/'
        self.temp_roles_config_file = 'tempRoles.json'
        self.tasks_config_file = 'tasks.json'

    def has_admin_role_or_higher():
        def predicate(ctx):
            if ctx.author.id == int(OWNER_ID):
                return True
            elif ctx.author.guild_permissions.administrator:
                return True
            else:
                admins_id_list = admins.read_admins_ids(ctx.guild.id)
                member_roles_id_list = [role.id for role in ctx.author.roles]
                for admin_id in admins_id_list:
                    if admin_id in member_roles_id_list:
                        return True
                return False

        return commands.check(predicate)

    # Add admin role to list of bot admin roles
    @commands.guild_only()
    @has_admin_role_or_higher()
    @commands.command(name='add_bot_admin_role', aliases=['add_admin_role', 'add_admin', 'aba', 'aa'])
    async def add_bot_admin_role(self, ctx, role: discord.Role):
        admins_data = admins.read_admins(ctx.guild.id)
        admins_id_list = admins.read_admins_ids(ctx.guild.id)
        if ctx.guild.get_role(role.id) is not None:
            if role.id in admins_id_list:
                print(f'Admin role ID {role.id} already is stored as admin')
                await ctx.send(f'Admin role ID {role.id} already set')
            else:
                admins_data.append(
                    {'admin_role_id': role.id}
                )
                print(f'Saving new admin role ID in json file for guild {ctx.guild.id}')
                admins.write_admins(ctx.guild.id, admins_data)
                print('Admin role ID saved')
                await ctx.send(f'Admin role name "{role.name}" with ID "{role.id}" added')
        else:
            print('Role was not found on the server')
            await ctx.send('Role was not found on the server')

    # Remove bot admin role from list of bot admins roles
    @commands.guild_only()
    @has_admin_role_or_higher()
    @commands.command(name='delete_bot_admin_role', aliases=['delete_admin_role', 'del_admin', 'dba', 'da'])
    async def delete_bot_admin_role(self, ctx, admin_role_number):
        admins_data = admins.read_admins(ctx.guild.id)
        try:
            if 0 < int(admin_role_number) <= len(admins_data) and len(admins_data) > 0:
                print(f"Deleting admin {admin_role_number}) {admins_data[int(admin_role_number) - 1]['admin_role_id']}")
                del admins_data[int(admin_role_number) - 1]
                print('Saving data to json')
                admins.write_admins(ctx.guild.id, admins_data)
                print('Saved')
                await ctx.send('Admin deleted')
            else:
                print('Admin role number is invalid or there is no admin to delete')
                await ctx.send('Admin role number is invalid or there is no admin to delete')
        except (ValueError, TypeError):
            print('Admin number is invalid')
            await ctx.send('Admin number is invalid')

    # List bot admins
    @commands.guild_only()
    @has_admin_role_or_higher()
    @commands.command(name='list_bot_admins', aliases=['lba', 'la'], hidden=True)
    async def list_bot_admins(self, ctx):
        admins_list = admins.read_admins(ctx.guild.id)
        message = ''
        index = 0
        if len(admins_list) > 0:
            for admin in admins_list:
                admin_role = ctx.guild.get_role(admin['admin_role_id'])
                if admin_role is not None:
                    message += f"{index + 1}) {admin_role.name}:{admin_role.id}\n"
                    index += 1
                else:
                    message += f"{index + 1}) {admin['admin_role_id']} (This role seems to not exist anymore)\n"
                    index += 1
            await ctx.send('```' + message + '```')
        else:
            print('No admins to show')
            await ctx.send('They are no admins set')

    # Give role to a member
    @commands.guild_only()
    @has_admin_role_or_higher()
    @commands.command(name='add_role', aliases=['arole', 'ar'])
    async def add_role(self, ctx, member: discord.Member, role: discord.Role):
        if ctx.guild.get_member(member.id) is not None:
            if ctx.guild.get_role(role.id) is not None:
                try:
                    print(f'Adding role "{role.name}" to member "{member.name}"')
                    await member.add_roles(role)
                    print('Role added successfully')
                    await ctx.send(f'Role "{role.name}" added successfully to "{member.name}"')
                except discord.Forbidden:
                    print('You do not have permissions to add this roles')
                    await ctx.send('You do not have permissions to add this roles')
                except discord.HTTPException:
                    print('Adding role failed')
                    await ctx.send('Adding role failed')
            else:
                print('Role was not found on the server')
                await ctx.send('Role was not found on the server')
        else:
            print('Member is not on the server')
            await ctx.send('Member is not on the server')

    # Remove role from a member
    @commands.guild_only()
    @has_admin_role_or_higher()
    @commands.command(name='remove_role', aliases=['rrole', 'rr'])
    async def remove_role(self, ctx, member: discord.Member, role: discord.Role):
        if ctx.guild.get_member(member.id) is not None:
            if ctx.guild.get_role(role.id) is not None:
                try:
                    print(f'Removing role "{role.name}" from member "{member.name}"')
                    await member.remove_roles(role)
                    print('Role removed successfully')
                    await ctx.send(f'Role "{role.name}" removed successfully from "{member.name}"')
                except discord.Forbidden:
                    print('You do not have permissions to remove this roles')
                    await ctx.send('You do not have permissions to add this roles')
                except discord.HTTPException:
                    print('Removing role failed')
                    await ctx.send('Removing role failed')
            else:
                print('Role was not found on the server')
                await ctx.send('Role was not found on the server')
        else:
            print('Member is not on the server')
            await ctx.send('Member is not on the server')

    # Give a temporary role to a member
    # For now time must be given in minutes
    # TODO Make it so that if a role doesn't exist, ask if bot should create it (role with no perm, name + color only)
    @commands.guild_only()
    @has_admin_role_or_higher()
    @commands.command(name='temp_role', aliases=['trole', 'tr'])
    async def temp_role(self, ctx, member: discord.Member, role: discord.Role, duration_in_min):
        if ctx.guild.get_member(member.id) is not None:
            if ctx.guild.get_role(role.id) is not None:
                try:
                    if int(duration_in_min) > 0:
                        # role_id = discord.utils.get(ctx.guild.roles, name=role.name).id
                        role_id = role.id
                        temp_roles_data = self.read_temp_roles(ctx.guild.id)
                        max_role_time = str(datetime.datetime.now() + datetime.timedelta(minutes=int(duration_in_min)))
                        if [member.id for id_val in temp_roles_data if member.id in id_val.values()
                                                                       and role_id in id_val.values()]:
                            for data in temp_roles_data:
                                if data['member_id'] == member.id and data['role_id'] == role_id:
                                    data['time'] = max_role_time
                                    self.write_temp_roles(ctx.guild.id, temp_roles_data)
                                    print(f'Member edited correctly in tempRole json for guild {ctx.guild.name}:'
                                          f'{ctx.guild.id}')
                                    await ctx.send('Member Temporary Role Timer edited successfully')
                                    break
                        else:
                            await member.add_roles(role)
                            temp_roles_data.append(
                                {'member_id': member.id,
                                 'role_id': role_id,
                                 'time': max_role_time}
                            )
                            self.write_temp_roles(ctx.guild.id, temp_roles_data)
                            print(f'Member added successfully in tempRol json for guild {ctx.guild.name}:'
                                  f'{ctx.guild.id}')
                            await ctx.send('Member Temporary Role Timer added successfully')
                    else:
                        print(f'Duration was not a value in minutes')
                        await ctx.send('Duration was not a valid value. It must be in minute(s) and >0')
                except (ValueError, TypeError) as e:
                    print(f'Duration was not a value in minutes')
                    await ctx.send('Duration was not a valid value. It must be in minute(s) and >0')
            else:
                print('Role was not found on the server')
                await ctx.send('Role was not found on the server')
        else:
            print('Member is not on the server')
            await ctx.send('Member is not on the server')

    # Remove bot admin role from list of bot admins roles
    @commands.guild_only()
    @has_admin_role_or_higher()
    @commands.command(name='delete_temp_role', aliases=['del_temp_role', 'del_trole', 'dtr'])
    async def delete_temp_role(self, ctx, temp_role_number):
        temp_roles_data = self.read_temp_roles(ctx.guild.id)
        try:
            if 0 < int(temp_role_number) <= len(temp_roles_data) and len(temp_roles_data) > 0:
                print(
                    f"Deleting temporary role {temp_role_number}) "
                    f"{temp_roles_data[int(temp_role_number) - 1]['member_id']}"
                    f"{temp_roles_data[int(temp_role_number) - 1]['role_id']}")
                del temp_roles_data[int(temp_role_number) - 1]
                print('Saving data to json')
                admins.write_admins(ctx.guild.id, temp_roles_data)
                print('Saved')
                await ctx.send('temp role deleted')
            else:
                print('Temp role number is invalid or there is no temp role to delete')
                await ctx.send('Temp role number is invalid or there is no temp role to delete')
        except (ValueError, TypeError):
            print('Temp role number is invalid')
            await ctx.send('Temp role number is invalid')

    @commands.guild_only()
    @has_admin_role_or_higher()
    @commands.command(name='list_temp_role', aliases=['ltrole', 'ltr'])
    async def list_temp_role(self, ctx):
        temp_roles_data = self.read_temp_roles(ctx.guild.id)
        message = ''
        index = 0
        if len(temp_roles_data) > 0:
            for temp_role in temp_roles_data:
                member = ctx.guild.get_member(temp_role['member_id'])
                role = ctx.guild.get_role(temp_role['role_id'])
                if member is not None:
                    if role is not None:
                        message += f"{index + 1}) Member: {member.name}:{temp_role['member_id']}\n\t" \
                                   f"Role: {role.name}:{temp_role['role_id']}\n\t" \
                                   f"Expiration Time: {temp_role['time']}\n"
                        index += 1
                    else:
                        message += f"{index + 1}) Member: {member.name}:{temp_role['member_id']}\n\t" \
                                   f"Role: {temp_role['role_id']} (This role seems to not exist anymore)\n\t" \
                                   f"Expiration Time: {temp_role['time']}\n"
                        index += 1
                else:
                    message += f"{index + 1}) Member: {temp_role['member_id']} (This member seems to be no more " \
                               f"on this server)\n\t" \
                               f"Role: {temp_role['role_id']} (This role seems to not exist anymore)\n\t" \
                               f"Expiration Time: {temp_role['time']}\n"
                    index += 1
            await ctx.send('```' + message + '```')
        else:
            print('No tasks to show')
            await ctx.send('There is no tasks set')

    # Add an announcement task / Max 5 tasks per guild for now / Task name is the unique ID for now
    # TODO Add choice of voice announcement (list available audio file/title)
    @commands.command(name='add_task', aliases=['at'], hidden=True)
    @commands.guild_only()
    @has_admin_role_or_higher()
    async def add_task(self, ctx, task_name, message, text_channel: discord.TextChannel, month_value, day_value,
                       hours_value, minutes_value, voice_channel_name=None):
        try:
            # text_channel = ''
            voice_channel_id = ''
            voice_channel_enabled = ''
            text_channels = ctx.guild.text_channels
            voice_channels = ctx.guild.voice_channels
            tasks_data = self.read_tasks(ctx.guild.id)
            if await self.check_add_task_params(ctx, task_name, message, text_channel.name, month_value,
                                                day_value, hours_value, minutes_value, text_channels, voice_channels,
                                                voice_channel_name):
                # Check if a task already exists with this name
                if any(task.get('task_name', False) == task_name for task in tasks_data):
                    # text_channel.id
                    # text_channel_id = next(text_channel.id for text_channel in text_channels
                    #                        if text_channel.name == text_channel.name)
                    if voice_channel_name is None:
                        voice_channel_id = 1234
                        voice_channel_enabled = 0
                    else:
                        # Here we go through the tasks and check that if there is multiple voice announcement,
                        # that the difference between them is at least 1 minute. This is to avoid the bot trying to
                        # join two channels at the same time in same server.
                        for task in tasks_data:
                            if int(task['voice_channel']) == 1 and task['task_name'] != task_name:
                                if int(task['day']) == int(day_value) and int(task['hours']) == int(hours_value) \
                                        and -1 < (int(task['minutes']) - int(minutes_value)) < 1:
                                    await ctx.send('Two voice tasks must have at least 1 minute between them.')
                                    raise admins.DeltaSmallerThanOne()
                        voice_channel_id = next(voice_channel.id for voice_channel in voice_channels
                                                if voice_channel_name == voice_channel.name)
                        voice_channel_enabled = 1
                    if text_channel.id and voice_channel_id:
                        for data in tasks_data:
                            if data['task_name'] == task_name:
                                data['message'] = message
                                data['text_channel_id'] = text_channel.id
                                data['voice_channel'] = voice_channel_enabled
                                data['voice_channel_id'] = voice_channel_id
                                data['month'] = int(month_value)
                                data['day'] = int(day_value)
                                data['hours'] = int(hours_value)
                                data['minutes'] = int(minutes_value)
                                self.write_task(ctx.guild.id, tasks_data)
                                print(f'Task "{task_name}" was edited successfully')
                                await ctx.send(f'Task "{task_name}" was edited successfully')
                                break
                    else:
                        print('Something went wrong! text and voice channel ids shouldn\'t be empty!')
                        await ctx.send('Something went wrong! text/voice channel IDs shouldn\'t be empty! '
                                       'Try again.')
                else:
                    if len(tasks_data) == 5:
                        await ctx.send('You already have the maximum allowed number of tasks.')
                        raise admins.MaxTasksReachedException()
                    # text_channel.id
                    # text_channel.id = next(text_channel.id for text_channel in text_channels
                    #                        if text_channel.name == text_channel.name)
                    if voice_channel_name is None:
                        voice_channel_id = 1234
                        voice_channel_enabled = 0
                    else:
                        # Here we go through the tasks and check that if there is multiple voice announcement,
                        # that the difference between them is at least 1 minute. This is to avoid the bot trying to
                        # join two channels at the same time in same server.
                        for task in tasks_data:
                            if int(task['voice_channel']) == 1 and task['task_name'] != task_name:
                                if int(task['day']) == int(day_value) and int(task['hours']) == int(hours_value) \
                                        and -1 < (int(task['minutes']) - int(minutes_value)) < 1:
                                    await ctx.send('Two voice tasks must have at least 1 minute between them.')
                                    raise admins.DeltaSmallerThanOne()
                        voice_channel_id = next(voice_channel.id for voice_channel in voice_channels
                                                if voice_channel_name == voice_channel.name)
                        voice_channel_enabled = 1
                    if text_channel.id and voice_channel_id:
                        tasks_data.append(
                            {'task_name': task_name,
                             'message': message,
                             'text_channel_id': text_channel.id,
                             'voice_channel': voice_channel_enabled,
                             'voice_channel_id': voice_channel_id,
                             'month': int(month_value),
                             'day': int(day_value),
                             'hours': int(hours_value),
                             'minutes': int(minutes_value)}
                        )
                        self.write_task(ctx.guild.id, tasks_data)
                        print(f'Task added successfully in tasks json for guild {ctx.guild.name}:{ctx.guild.id}')
                        await ctx.send('Task added successfully')
                    else:
                        print('Something went wrong! text and voice channel ids shouldn\'t be empty!')
                        await ctx.send('Something went wrong! text/voice channel IDs shouldn\'t be empty! '
                                       'Try again.')
            else:
                print('Wrong command args')
                await ctx.send('Command should be: [p]cmd message(string) txt_channel(string) Month(int->1-12 or -1)'
                               ' Day(int->0-6 or -1) hours(int->0-23 or -1) minutes(int-0-59)'
                               ' voice_channel(string-Optional)')
        except (ValueError, TypeError) as e:
            print('Wrong type of args')
            await ctx.send('Command should be: [p]cmd message(string) txt_channel(string) Month(int->1-12 or -1)'
                           ' Day(int->0-6 or -1) hours(int->0-23 or -1) minutes(int-0-59) '
                           'voice_channel(string-Optional)')
        except admins.MaxTasksReachedException:
            print('Max. Number of tasks reached.')
        except admins.DeltaSmallerThanOne:
            print('Delta between two voice tasks was smaller than one.')

    # List all tasks name
    @commands.guild_only()
    @has_admin_role_or_higher()
    @commands.command(name='list_tasks', aliases=['lt'], hidden=True)
    async def list_tasks(self, ctx, details=None):
        tasks = self.read_tasks(ctx.guild.id)
        message = ''
        index = 0
        if len(tasks) > 0:
            if details is not None and details == 'd':
                for task in tasks:
                    message += f"{index + 1}) {task['task_name']}\n\t" \
                               f"Message: {task['message']}\n\t" \
                               f"Text Channel ID: {task['text_channel_id']}\n\t" \
                               f"Has voice channel: {task['voice_channel']}\n\t" \
                               f"Voice Channel ID: {task['voice_channel_id']}\n\t" \
                               f"Month: {task['month']}\n\t" \
                               f"Day: {task['day']}\n\t" \
                               f"Hours: {task['hours']}\n\t" \
                               f"Minutes: {task['minutes']}\n"
                    index += 1
            else:
                for task in tasks:
                    message += f"{index + 1}) {task['task_name']}\n"
                    index += 1
            await ctx.send('```' + message + '```')
        else:
            print('No tasks to show')
            await ctx.send('There is no tasks set')

    # Delete a task
    @commands.guild_only()
    @has_admin_role_or_higher()
    @commands.command(name='delete_task', aliases=['del_task', 'dt'])
    async def delete_task(self, ctx, task_number):
        tasks = self.read_tasks(ctx.guild.id)
        try:
            if 0 < int(task_number) <= len(tasks) and len(tasks) > 0:
                print(f"Deleting task {task_number}) {tasks[int(task_number) - 1]['task_name']}")
                del tasks[int(task_number) - 1]
                print('Saving data to json')
                self.write_task(ctx.guild.id, tasks)
                print('Saved')
                await ctx.send('Task deleted')
            else:
                print('Task number is invalid or there is no task to delete')
                await ctx.send('Task number is invalid or there is no task to delete')
        except (ValueError, TypeError):
            print('Task number is invalid')
            await ctx.send('Task number is invalid')

    # Purge x number of message in the current channel
    @commands.guild_only()
    @commands.command(name='purge', aliases=['clear', 'delete', 'cls'])
    @has_admin_role_or_higher()
    async def purge(self, ctx, number_of_messages):
        try:
            if int(number_of_messages) > 100:
                await ctx.send('You cannot bulk delete more than 100 messages or '
                               'messages that are older than 14 days old.')
            else:
                await ctx.message.channel.purge(limit=int(number_of_messages) + 1)
                print(f'Purged {int(number_of_messages) + 1} messages in channel #{ctx.message.channel.name}.\n'
                      f'({number_of_messages} message(s) from channel + the cmd message)')
        except TypeError:
            print('TypeError: The purge cmd argument was not int.')
            await ctx.send('Command: purge\nArgument was not an int.')
        except ValueError:
            print('ValueError: The purge cmd argument was not int.')
            await ctx.send('Command: purge\nArgument was not an int.')

    @commands.guild_only()
    @has_admin_role_or_higher()
    @commands.command(name='kick')
    async def kick(self, ctx, member, reason=None):
        if ctx.guild.get_member(member.id) is not None:
            try:
                print('Kicking member')
                await ctx.guild.kick(member, reason)
                await ctx.send(f'{member.name} was kicked!')
            except discord.Forbidden:
                print('You do not have the proper permissions to kick')
                await ctx.send('You do not have the proper permissions to kick')
            except discord.HTTPException:
                print('Kicking failed')
                await ctx.send('Kicking failed')
        else:
            print('Member is not on the server')
            await ctx.send('Member is not on the server')

    @commands.guild_only()
    @has_admin_role_or_higher()
    @commands.command(name='ban')
    async def ban(self, ctx, member, reason=None):
        if ctx.guild.get_member(member.id) is not None:
            try:
                print('Banning member')
                await ctx.guild.kick(member, reason)
                await ctx.send(f'{member.name} was banned!')
            except discord.Forbidden:
                print('You do not have the proper permissions to ban')
                await ctx.send('You do not have the proper permissions to ban')
            except discord.HTTPException:
                print('Banning failed')
                await ctx.send('Banning failed')
        else:
            print('Member is not on the server')
            await ctx.send('Member is not on the server')

    # Move from ctx channel to target channel
    @commands.guild_only()
    @has_admin_role_or_higher()
    @commands.command(name='move_all', aliases=['ma'])
    async def move_all(self, ctx, voice_channel: discord.VoiceChannel):
        if ctx.author.voice is None:
            print('Author not connected to a channel')
            await ctx.send('Please connect to a voice channel first.')
        else:
            await ctx.message.add_reaction('⌛')
            author_voice_channel = ctx.author.voice.channel
            guild_voice_channels = ctx.guild.voice_channels
            for member in author_voice_channel.members:
                try:
                    await member.move_to(voice_channel)
                except discord.Forbidden:
                    print('You do not have the permission to move members')
                    await ctx.send('You do not have the permission to move members')
                    break
                except discord.HTTPException:
                    print('The operation failed')
                    await ctx.send('The operation failed. Please try again.')
                    break
                except:
                    continue
            await ctx.message.remove_reaction('⌛', self.bot.user)
            await ctx.message.add_reaction('✅')

    # Move a member to my voice channel
    @commands.guild_only()
    @has_admin_role_or_higher()
    @commands.command(name='move_to_me', aliases=['mtm'])
    async def move_to_me(self, ctx, member: discord.Member):
        if ctx.author.voice is None:
            print('Author not connected to a channel')
            await ctx.send('Please connect to a voice channel first.')
        elif member is not None:
            if member.voice is not None:
                await ctx.message.add_reaction('⌛')
                author_voice_channel = ctx.author.voice.channel
                try:
                    await member.move_to(author_voice_channel)
                except discord.Forbidden:
                    print('You do not have the permission to move members')
                    await ctx.send('You do not have the permission to move members')
                except discord.HTTPException:
                    print('The operation failed')
                    await ctx.send('The operation failed. Please try again.')
                await ctx.message.remove_reaction('⌛', self.bot.user)
                await ctx.message.add_reaction('✅')
            else:
                print(f'Member {member.name} is not in a voice channel')
                await ctx.send(f'Member {member.name} is not in a voice channel')
        else:
            print('Member was not found')
            await ctx.send(f'Member {member} was not found')

    # Move a role to a specified voice channel
    @commands.guild_only()
    @has_admin_role_or_higher()
    @commands.command(name='move_role', aliases=['mr'])
    async def move_role(self, ctx, role: discord.Role, voice_channel: discord.VoiceChannel,
                        *voice_channels_to_ignore: discord.VoiceChannel):
        if voice_channels_to_ignore:
            await ctx.message.add_reaction('⌛')
            voice_channels = ctx.guild.voice_channels
            for v_channel in voice_channels:
                if v_channel not in voice_channels_to_ignore:
                    for member in v_channel.members:
                        if role in member.roles:
                            try:
                                await member.move_to(voice_channel)
                            except discord.Forbidden:
                                print('You do not have the permission to move members')
                                await ctx.send('You do not have the permission to move members')
                                break
                            except discord.HTTPException:
                                print('The operation failed')
                                await ctx.send('The operation failed. Please try again.')
                                break
                            except:
                                continue
                else:
                    print(f'Ignoring channel: {v_channel.name}')
            await ctx.message.remove_reaction('⌛', self.bot.user)
            await ctx.message.add_reaction('✅')
        else:
            await ctx.message.add_reaction('⌛')
            voice_channels = ctx.guild.voice_channels
            for v_channel in voice_channels:
                for member in v_channel.members:
                    if role in member.roles:
                        try:
                            await member.move_to(voice_channel)
                        except discord.Forbidden:
                            print('You do not have the permission to move members')
                            await ctx.send('You do not have the permission to move members')
                            break
                        except discord.HTTPException:
                            print('The operation failed')
                            await ctx.send('The operation failed. Please try again.')
                            break
                        except:
                            continue
            await ctx.message.remove_reaction('⌛', self.bot.user)
            await ctx.message.add_reaction('✅')

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
            with open(file_path, 'r') as temp_roles_list:
                temp_roles = json.load(temp_roles_list)
                temp_roles_list.close()
        except FileNotFoundError:
            print('File does not exist or was not found, creating it.')
            if not os.path.exists(os.path.dirname(file_path)):
                try:
                    os.makedirs(os.path.dirname(file_path))
                except OSError as exc:  # Guard against race condition
                    if exc.errno != errno.EEXIST:
                        raise
            with open(file_path, 'w') as temp_role_list:
                json.dump(temp_roles, temp_role_list, indent=4)
                temp_role_list.close()
        return temp_roles

    # Write task in tasks.json
    def write_task(self, guild_id, tasks_data):
        with open(self.path + str(guild_id) + '/' + self.tasks_config_file, 'w') as tasks_file:
            json.dump(tasks_data, tasks_file, indent=4)
            tasks_file.close()

    # Read the tasks.json file for the specified guild
    def read_tasks(self, guild_id):
        tasks = []
        file_path = self.path + str(guild_id) + '/' + self.tasks_config_file
        try:
            with open(file_path, 'r') as task_file:
                tasks = json.load(task_file)
                task_file.close()
        except FileNotFoundError:
            print('File does not exist or was not found, creating it.')
            if not os.path.exists(os.path.dirname(file_path)):
                try:
                    os.makedirs(os.path.dirname(file_path))
                except OSError as exc:  # Guard against race condition
                    if exc.errno != errno.EEXIST:
                        raise
            with open(file_path, 'w') as task_file:
                json.dump(tasks, task_file, indent=4)
                task_file.close()
        return tasks

    # Check if text channel exists in guild text channels list
    @staticmethod
    def text_channel_exists(text_channel_name, guild_text_channels_list):
        if [text_channel for text_channel in guild_text_channels_list if text_channel_name == text_channel.name]:
            return True
        else:
            return False

    # check if voice channel exists in guild voice channels list
    @staticmethod
    def voice_channel_exists(voice_channel_name, guild_voice_channels_list):
        if [voice_channel for voice_channel in guild_voice_channels_list if voice_channel_name == voice_channel.name]:
            return True
        else:
            return False

    # Checks add_task() param
    async def check_add_task_params(self, ctx, task_name, message, text_channel_name, month_value, day_value,
                                    hours_value,
                                    minutes_value,
                                    text_channels, voice_channels, voice_channel_name=None):
        try:
            if len(task_name) > 150:
                return False
            if len(message) > 2000:
                return False
            if int(month_value) < -1 or int(month_value) == 0 or int(month_value) > 12:
                return False
            if int(day_value) < -1 or int(day_value) >= 7:
                return False
            if int(hours_value) < -1 or int(hours_value) >= 24:
                return False
            if int(minutes_value) < 0 or int(minutes_value) >= 60:
                return False
            if not self.text_channel_exists(text_channel_name, text_channels):
                print(f'❌ The text channel "{text_channel_name}" was not found on the server.')
                await ctx.send(f'❌ The text channel "{text_channel_name}" was not found on the server.')
                return False
            if voice_channel_name is not None:
                if not self.voice_channel_exists(voice_channel_name, voice_channels):
                    print(f'❌ The voice channel "{voice_channel_name}" was not found on the server.')
                    await ctx.send(f'❌ The voice channel "{voice_channel_name}" '
                                   f'was not found on the server.')
                    return False
            return True
        except (TypeError, ValueError):
            return False


def setup(bot):
    bot.add_cog(Admin(bot))
