import discord

import config


class CommandBinding:
    command_binding = {}

    def __init__(self, **kwargs):
        self.command_name = 'unknown'
        self.channel_filter = []
        self.function = None
        for key in kwargs:
            setattr(self, key, kwargs[key])

    @classmethod
    def assign_command(cls, obj, command_name, channel_filter):
        def assign(function):
            cls.command_binding[command_name] = CommandBinding(baseobject=obj,
                                                               command_name=command_name,
                                                               channel_filter=channel_filter,
                                                               function=function)

        return assign

    @classmethod
    async def run_command(cls, command_name, bot, query, msg):
        if command_name in cls.command_binding:
            command_info = cls.command_binding[command_name]
            if msg.channel not in command_info.channel_filter:
                await msg.add_reaction(emoji='❕')
                return
            await command_info.function(command_info.baseobject, query, msg)
            # def get_timetable(bot: DiscordBot, query: list[str], msg: discord.Message):
        else:
            await msg.add_reaction(emoji='❔')


class DiscordModule:
    modules = []

    def __init__(self, **kwargs):
        self.base_object = None
        self.async_function = None
        for key in kwargs:
            setattr(self, key, kwargs[key])

    @classmethod
    def assign_onready(cls, base_object):
        def assign(async_function):
            cls.modules.append(DiscordModule(base_object=base_object, async_function=async_function))

        return assign

    @classmethod
    async def match_onready(cls, bot):
        for discord_module in cls.modules:
            await discord_module.async_function(bot, discord_module.base_object)


class DiscordBot:
    client = None
    channel = None
    guild = None
    discord_token = open('discord_bot_token', 'r').read()

    def __init__(self, client):
        self.client = client

    def run(self):
        self.client.run(self.discord_token)

    async def ready(self):
        self.channel = self.client.get_channel(config.discord_info['free channel id'])
        self.guild = self.client.get_guild(config.discord_info['black cow guild id'])
        await DiscordModule.match_onready(self)

    async def read_msg(self, msg: discord.Message):
        if len(msg.content) < 2 or msg.author.bot:
            return
        if msg.content[0] != 'ㄱ':
            return
        command = msg.content
        query = []
        if msg.content.find(' ') != -1:
            command = msg.content[:msg.content.find(' ')]
            query = [arg.strip() for arg in msg.content[msg.content.find(' ') + 1:].split(',')]
        command = command[1:]

        await CommandBinding.run_command(command, self, query, msg)


__client__ = discord.Client()
discord_bot = DiscordBot(__client__)


@__client__.event
async def on_ready():
    print('Start Process')
    await discord_bot.ready()


@__client__.event
async def on_message(msg):
    await discord_bot.read_msg(msg)
