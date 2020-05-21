import discord

import config
import static


class GameChannel:
    def __init__(self):
        self.running_game = None
        self.games = {}
        self.channel = None


class GameInterface:
    TITLE = 'unknown'
    COMMANDS = {}
    LISTENER = None
    MIN_USER = 0
    MAX_USER = 0

    def __init__(self):
        self.users = {}
        self.game_channel = None

    def runnable(self):
        return self.MIN_USER <= len(self.users) <= self.MAX_USER

    async def start(self):
        pass

    # async def sample(self, bot: static.DiscordBot, query: list, msg: discord.Message):
    #   pass


def is_admin(user: discord.User):
    return user.id == 348066198983933954


def nick_to_name(nick):
    copied_nick = str(nick)
    # if copied_nick.find('(') != -1:
    #    copied_nick = (copied_nick[:copied_nick.find('(')] + copied_nick[copied_nick.find(')') + 1:]).strip()
    if len(copied_nick) > 3:
        copied_nick = copied_nick[-3:]
    return copied_nick


class GameManager:
    number_to_emote_map = {0: '0️⃣', 1: '1️⃣', 2: '2️⃣', 3: '3️⃣', 4: '4️⃣', 5: '5️⃣', 6: '6️⃣', 7: '7️⃣', 8: '8️⃣',
                           9: '9️⃣', 10: '🔟', 'other': '🔢'}

    allowed_channels = []
    guild = None
    guild_members = {}
    game_channels = {}
    games = {}

    def user_to_member(self, user: discord):
        for member_name in self.guild_members:
            member = self.guild_members[member_name]
            if member.id == user.id:
                return member
        return None

    async def ready(self, discord_bot):
        for member in self.guild.members:
            if member.nick is not None:
                self.guild_members[nick_to_name(member.nick).strip()] = member
            else:
                self.guild_members[nick_to_name(member.name).strip()] = member
        for channel in self.allowed_channels:
            game_channel = GameChannel()
            game_channel.games = dict(self.games)
            game_channel.channel = channel
            for game_name in self.games:
                game = self.games[game_name]()
                game.game_channel = game_channel
                for command_name in game.COMMANDS:
                    static.CommandBinding.assign_command(game_channel, command_name, [channel])(
                        game.COMMANDS[command_name])
                if game.LISTENER is not None:
                    static.CommandBinding.assign_listener(game_channel, game.TITLE, None)(game.LISTENER)
                game_channel.games[game_name] = game
            self.game_channels[channel.id] = game_channel

    def number_to_emote(self, num):
        if num in self.number_to_emote_map.keys():
            return self.number_to_emote_map[num]
        else:
            return self.number_to_emote_map['other']


game_manager = GameManager()


@static.DiscordModule.assign_onready(game_manager)
async def on_ready(discord_bot: static.DiscordBot, self: GameManager):
    self.allowed_channels = [discord_bot.client.get_channel(config.discord_info['free channel id']),
                             discord_bot.client.get_channel(config.discord_info['1st class channel id']),
                             discord_bot.client.get_channel(config.discord_info['2nd class channel id']),
                             discord_bot.client.get_channel(config.discord_info['3rd class channel id']),
                             ]
    for channel in self.allowed_channels:
        self.game_channels[channel.id] = channel
    self.guild = discord_bot.client.get_guild(config.discord_info['black cow guild id'])
    await self.ready(discord_bot)

    @static.CommandBinding.assign_command('게임참가', self.allowed_channels)
    async def join_game(query: list, msg: discord.Message, **kwargs):

        game_channel = self.game_channels[msg.channel.id]
        if game_channel.running_game is not None:
            await msg.channel.send(
                f'>>> {game_channel.running_game.TITLE}(이)가 이미 실행중입니다.\n해당 게임이 종료된 후에 다시 시도 해주세요')
            return
        if len(query) == 0:
            text = '>>> 게임목록\n'
            for game in game_channel.games.values():
                if game.runnable():
                    text += f'**{game.TITLE}** [{game.MIN_USER}≤{len(game.users)}≤{game.MAX_USER}]\n'
                else:
                    text += f'{game.TITLE} [{game.MIN_USER}≤{len(game.users)}≤{game.MAX_USER}]\n'
            await msg.channel.send(text)
        elif len(query) >= 1:
            game_name = query[0]
            if game_name not in game_channel.games:
                await msg.channel.send(f'>>> {game_name}(은)는 없는 게임입니다.')
                return
            game = game_channel.games[game_name]
            if len(query) == 1:
                if len(game.users) >= game.MAX_USER:
                    await msg.channel.send(f'>>> 인원제한을 초과하여 참가하지 못 했습니다.')
                else:
                    for user_name in self.guild_members:
                        user = self.guild_members[user_name]
                        if msg.author.id == user.id:
                            game.users[user_name] = user
                            break
            else:
                for user_name in query[1:]:
                    if user_name in self.guild_members:
                        user = self.guild_members[user_name]
                        if is_admin(msg.author) or msg.author.id == user.id:
                            if len(game.users) >= game.MAX_USER:
                                await msg.channel.send(f'>>> 인원제한을 초과하여 일부 인원은 참가하지 못 했습니다.')
                                break
                            else:
                                game.users[user_name] = user
                        else:
                            await msg.add_reaction(emoji='🛑')
            await msg.add_reaction(emoji=self.number_to_emote(len(game.users)))

    @static.CommandBinding.assign_command('게임시작', self.allowed_channels)
    async def start_game(query: list, msg: discord.Message, **kwargs):
        game_channel = self.game_channels[msg.channel.id]
        if game_channel.running_game is not None:
            await msg.channel.send(
                f'>>> {game_channel.running_game.TITLE}(이)가 이미 실행중입니다.\n해당 게임이 종료된 후에 다시 시도 해주세요')
            return

        if len(query) == 0:
            text = '>>> 게임목록\n'
            for game in game_channel.games.values():
                if game.runnable():
                    text += f'**{game.TITLE}** [{game.MIN_USER}≤{len(game.users)}≤{game.MAX_USER}]\n'
                else:
                    text += f'{game.TITLE} [{game.MIN_USER}≤{len(game.users)}≤{game.MAX_USER}]\n'
            await msg.channel.send(text)
        elif len(query) == 1:
            game_name = query[0]
            if game_name not in game_channel.games:
                await msg.channel.send(f'>>> {game_name}(은)는 없는 게임입니다.')
                return
            game = game_channel.games[game_name]
            if game.runnable():
                await msg.channel.send(f'>>> {game.TITLE}(을)를 시작합니다.')
                game_channel.running_game = game
                await game_channel.running_game.start()
            else:
                await msg.channel.send(
                    f'>>> 게임 인원이 적절하지 않습니다. {game.TITLE} [{game.MIN_USER}<={len(game.users)}<={game.MAX_USER}]\n')
        else:
            raise Exception('not matched arguments count')
