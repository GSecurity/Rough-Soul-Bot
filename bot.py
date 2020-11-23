import os
import errno
import json
import discord
import datetime
import prefixes
from admins import read_guilds_ids
from admins import read_admins
from discord.ext import commands
from settings.config import TOKEN
from cogs.temp_role import TempRole

intents = discord.Intents.default()
intents.members = True
intents.presences = True
guilds_ids_folder = read_guilds_ids()
cogs_data_path = './cogs/data/'


# Get the prefixes for the bot
def get_prefix(bot, message):
    extras = prefixes.prefixes_for(message.guild, bot.prefix_data)
    return commands.when_mentioned_or(*extras)(bot, message)


# All cogs that will be loaded on bots startup
# 'cogs.guilds_config'
startup_extensions = [
    'cogs.general', 'cogs.stats', 'cogs.owner', 'cogs.admin', 'cogs.temp_role', 'cogs.tasks'
]


class RSMBot(commands.AutoShardedBot):
    def __init__(self):
        super().__init__(command_prefix=get_prefix, case_insensitive=True, intents=intents)

        self.remove_command('help')
        self.command_stats = self.read_command_stats()
        # self.temp_role_data = TempRole.read_temp_roles()
        self.prefix_data = prefixes.read_prefixes()
        # self.admin_roles = admins.read_admins()
        self.uptime = datetime.datetime.utcnow()
        # TODO: Change the logging channel mechanics to be configurable per Guild
        self.LOGGING_CHANNEL = 762646728011808788

        for extension in startup_extensions:
            try:
                self.load_extension(extension)
            except Exception as e:
                exc = '{}: {}'.format(type(e).__name__, e)
                print('Failed to load extension {}\n{}'.format(extension, exc))

        # Print bot information, update status and set uptime when bot is ready
        @self.event
        async def on_ready():
            global guilds_ids_folder
            global cogs_data_path
            # We're checking if the data folder for the guild exists, if not, we create it and
            # create the main admin.json file. the other files are created with the loop starts and should not
            # prevent any error using commands.
            print('Checking if guild data folder exist')
            for guild in bot.guilds:
                if guild.id not in guilds_ids_folder:
                    path_dir = cogs_data_path + str(guild.id)
                    if not os.path.exists(path_dir):
                        try:
                            print(f'{guild.id} data folder does not exist, creating it')
                            os.makedirs(path_dir)
                            print('Creating admins.json')
                            read_admins(guild.id)
                            print('admins.json created')
                        except OSError as exc:  # Guard against race condition
                            if exc.errno != errno.EEXIST:
                                raise
            print('Done checking data folders')
            guilds = '\n - '.join([f'{guild.name} (ID: {guild.id})' for guild in bot.guilds])
            print('Bot is READY!')
            print('Logged in as: ' + str(self.user.name))
            print('With ClientID: ' + str(self.user.id))
            print('To the following guild(s):\n'
                  f' - {guilds}')
            print('------')
            if not hasattr(self, 'uptime'):
                self.uptime = datetime.datetime.utcnow()

    # Prevent bot from replying to other bots
    async def on_message(self, message):
        if not message.author.bot:
            ctx = await bot.get_context(message)
            await self.invoke(ctx)

    # Track number of command executed
    async def on_command(self, ctx):
        command = ctx.command.qualified_name
        if command in self.command_stats:
            self.command_stats[command] += 1

        else:
            self.command_stats[command] = 1

        self.write_command_stats(self.command_stats)

    # Commands error handler
    async def on_command_error(self, ctx, error):
        logging = self.get_channel(self.LOGGING_CHANNEL)
        if isinstance(error, commands.CommandOnCooldown):
            time_left = round(error.retry_after, 2)
            await ctx.send(':hourglass: Command on cooldown. Slow '
                           'down. (' + str(time_left) + 's)',
                           delete_after=max(error.retry_after, 1))

        elif isinstance(error, commands.MissingPermissions) and \
                ctx.command.qualified_name != 'forcestop':
            await ctx.send('<:xmark:411718670482407424> Sorry, '
                           'you don\'t have the permissions '
                           'for that command! ')

        elif isinstance(error, commands.NoPrivateMessage):
            await ctx.send(error)

        elif isinstance(error, commands.CommandNotFound):
            # await ctx.send('Command does not exist.')
            pass

        elif isinstance(error, commands.MissingPermissions):
            await logging.send(error)
            await logging.send('Command :' + str(ctx.command.qualified_name))
            await logging.send('Missing Perms: ' + error.missing_perms)

        else:
            await logging.send('Command: ' + str(ctx.command.qualified_name))
            await logging.send(error)
            print(error)

    # Read the command statistics from json file
    @staticmethod
    def read_command_stats():
        with open('cogs/data/commandStats.json', 'r') as command_counter:
            command_stats = json.load(command_counter)
            command_counter.close()
        return command_stats

    # Dump the command statistics to json file
    @staticmethod
    def write_command_stats(command_stats):
        with open('cogs/data/commandStats.json', 'w') as command_counter:
            json.dump(command_stats, command_counter, indent=4)
            command_counter.close()


bot = RSMBot()

bot.run(TOKEN)
