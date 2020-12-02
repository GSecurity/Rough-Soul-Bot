import os
import errno
import json
import admins
import asyncio
import discord
import datetime as dt
from concurrent.futures import ThreadPoolExecutor
from discord.ext import commands

# TODO Add audio selection for the task

# vc = None


# Define Class for tasks
class Tasks(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.path = 'cogs/data/'
        self.tasks_config_file = 'tasks.json'
        self.check_tasks_task = ''


    @staticmethod
    async def disconnect_voice():
        print('Done playing, disconnecting...')
        await vc.disconnect()
        print('Disconnected')

    def my_after(self, error):
        # global vc
        # vc.disconnect()
        # print(self.bot.voice_clients)
        # vc = discord.utils.get(self.bot.voice_clients, error.guild)
        vcs = self.bot.voice_clients
        for vc in vcs:
            if not vc.is_playing():
                coro = vc.disconnect()
                fut = asyncio.run_coroutine_threadsafe(coro, self.bot.loop)
                try:
                    fut.result()
                except:
                    pass


    # Play the music file
    @staticmethod
    async def check_is_playing():
        # global vc
        test_playing = vc.is_playing()
        while test_playing:
            # print('playing...')
            test_playing = vc.is_playing()
            await asyncio.sleep(5)
            # vc.stop()
        print('Done playing, disconnecting...')
        await vc.disconnect()
        print('Disconnected')

    # TODO Check https://discordpy.readthedocs.io/en/latest/ext/tasks/ to optimize the task system
    # This checks for recurring tasks. For now, only hourly, daily, monthly, or yearly tasks possible.
    # You can't go under "every hour" for now. May add "every  minute" later on but not less.
    async def check_tasks(self):
        await self.bot.wait_until_ready()
        # global vc
        while not self.bot.is_closed():
            print(f'{dt.datetime.now().day}-{dt.datetime.now().month}-{dt.datetime.now().year} {dt.datetime.now().hour}'
                  f':{dt.datetime.now().minute}:{dt.datetime.now().second} - Checking tasks...')
            # get actual date and time
            tasks_data = []
            guild_ids = admins.read_guilds_ids()
            for guild_id in guild_ids:
                tasks_data = self.read_tasks(guild_id)
                guild_data = self.bot.get_guild(int(guild_id))
                print(f'{dt.datetime.now().day}-{dt.datetime.now().month}-{dt.datetime.now().year} '
                      f'{dt.datetime.now().hour}:{dt.datetime.now().minute}:{dt.datetime.now().second}'
                      f' - Checking tasks for server: {guild_data.name}:{guild_data.id}')
                for index in range(len(tasks_data)):
                    what_to_check = self.task_date_time_check(tasks_data[index]['month'], tasks_data[index]['day'],
                                                              tasks_data[index]['hours'])
                    await self.run_task_if_ready(what_to_check, index, tasks_data)
            print(f'{dt.datetime.now().day}-{dt.datetime.now().month}-{dt.datetime.now().year} {dt.datetime.now().hour}'
                  f':{dt.datetime.now().minute}:{dt.datetime.now().second} - Done checking tasks')
            # pause loop
            await asyncio.sleep(60)

    @commands.guild_only()
    @commands.is_owner()
    @commands.command(name='start_tasks_check', aliases=['statc'], hidden=True)
    async def start_tasks_check(self, ctx):
        self.check_tasks_task = self.bot.loop.create_task(self.check_tasks())
        print('Task CHK_TASKS Started.')
        await ctx.send('Task CHK_TASKS started.')

    @commands.guild_only()
    @commands.is_owner()
    @commands.command(name='stop_tasks_check', aliases=['stotc'], hidden=True)
    async def stop_tasks_check(self, ctx):
        self.check_tasks_task.cancel()
        print('Task CH_TASKS Stopped')
        await ctx.send('Task CHK_TASKS stopped.')

    @commands.Cog.listener()
    async def on_ready(self):
        self.check_tasks_task = self.bot.loop.create_task(self.check_tasks())
        print('Task CHK_TASKS started.')

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

    # Check what date or time should be checked.
    # Return 4 for month, 3 for day, 2 for hours, 1 for minutes
    # For Ex. if return 2, task loop will only check if datetime.now() = same hours and minutes and ignore day and month
    @staticmethod
    def task_date_time_check(month_value, day_value, hours_value):
        if int(month_value) == -1:
            if int(day_value) == -1:
                if int(hours_value) == -1:
                    return 1
                else:
                    return 2
            else:
                return 3
        else:
            return 4

    # Check the tasks, given the value (check task_date_time_check) it will only check month, day, hours or minutes
    async def run_task_if_ready(self, check_type_value, index, tasks_data):
        test_now = dt.datetime.now()
        # global vc
        # vc = None
        if check_type_value == 4:
            if test_now.month == tasks_data[index]['month'] and test_now.weekday() == tasks_data[index]['day']\
                    and test_now.hour == tasks_data[index]['hours'] and test_now.minute == tasks_data[index]['minutes']:
                if tasks_data[index]['voice_channel'] == 0:
                    text_channel = self.bot.get_channel(tasks_data[index]['text_channel_id'])
                    print(f'Sending message to text channel {text_channel.name}:{text_channel.id}')
                    await text_channel.send(tasks_data[index]['message'])
                    print('Message sent')
                if tasks_data[index]['voice_channel'] == 1:
                    text_channel = self.bot.get_channel(tasks_data[index]['text_channel_id'])
                    print(f'Sending message to text channel {text_channel.name}:{text_channel.id}')
                    await text_channel.send(tasks_data[index]['message'])
                    print('Message sent')
                    voice_channel = self.bot.get_channel(tasks_data[index]['voice_channel_id'])
                    print(f'Connecting to voice channel {voice_channel.name}:{voice_channel.id}')
                    vc = await voice_channel.connect()
                    print('Joined voice channel.')
                    vc.play(discord.FFmpegPCMAudio('./media/RaidTime.opus'), after=self.my_after)
        elif check_type_value == 3:
            if test_now.weekday() == tasks_data[index]['day'] and test_now.hour == tasks_data[index]['hours'] \
                    and test_now.minute == tasks_data[index]['minutes']:
                if tasks_data[index]['voice_channel'] == 0:
                    text_channel = self.bot.get_channel(tasks_data[index]['text_channel_id'])
                    print(f'Sending message to text channel {text_channel.name}:{text_channel.id}')
                    await text_channel.send(tasks_data[index]['message'])
                    print('Message sent')
                if tasks_data[index]['voice_channel'] == 1:
                    text_channel = self.bot.get_channel(tasks_data[index]['text_channel_id'])
                    print(f'Sending message to text channel {text_channel.name}:{text_channel.id}')
                    await text_channel.send(tasks_data[index]['message'])
                    print('Message sent')
                    voice_channel = self.bot.get_channel(tasks_data[index]['voice_channel_id'])
                    print(f'Connecting to voice channel {voice_channel.name}:{voice_channel.id}')
                    vc = await voice_channel.connect()
                    print('Joined voice channel.')
                    vc.play(discord.FFmpegPCMAudio('./media/RaidTime.opus'), after=self.my_after)
        elif check_type_value == 2:
            if test_now.hour == tasks_data[index]['hours'] and test_now.minute == tasks_data[index]['minutes']:
                if tasks_data[index]['voice_channel'] == 0:
                    text_channel = self.bot.get_channel(tasks_data[index]['text_channel_id'])
                    print(f'Sending message to text channel {text_channel.name}:{text_channel.id}')
                    await text_channel.send(tasks_data[index]['message'])
                    print('Message sent')
                if tasks_data[index]['voice_channel'] == 1:
                    text_channel = self.bot.get_channel(tasks_data[index]['text_channel_id'])
                    print(f'Sending message to text channel {text_channel.name}:{text_channel.id}')
                    await text_channel.send(tasks_data[index]['message'])
                    print('Message sent')
                    voice_channel = self.bot.get_channel(tasks_data[index]['voice_channel_id'])
                    print(f'Connecting to voice channel {voice_channel.name}:{voice_channel.id}')
                    vc = await voice_channel.connect()
                    print('Joined voice channel.')
                    vc.play(discord.FFmpegPCMAudio('./media/RaidTime.opus'), after=self.my_after)
        elif check_type_value == 1:
            if test_now.minute == tasks_data[index]['minutes']:
                if tasks_data[index]['voice_channel'] == 0:
                    text_channel = self.bot.get_channel(tasks_data[index]['text_channel_id'])
                    print(f'Sending message to text channel {text_channel.name}:{text_channel.id}')
                    await text_channel.send(tasks_data[index]['message'])
                    print('Message sent')
                if tasks_data[index]['voice_channel'] == 1:
                    text_channel = self.bot.get_channel(tasks_data[index]['text_channel_id'])
                    print(f'Sending message to text channel {text_channel.name}:{text_channel.id}')
                    await text_channel.send(tasks_data[index]['message'])
                    print('Message sent')
                    voice_channel = self.bot.get_channel(tasks_data[index]['voice_channel_id'])
                    print(f'Connecting to voice channel {voice_channel.name}:{voice_channel.id}')
                    vc = await voice_channel.connect()
                    print('Joined voice channel.')
                    vc.play(discord.FFmpegPCMAudio('./media/RaidTime.opus'), after=self.my_after)
        else:
            print('Error in run_task_if_ready(), this should never happen')


def setup(bot):
    bot.add_cog(Tasks(bot))
