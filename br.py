import asyncio

import discord

import config
import static


class Bera:
    user_list = []
    user_index = 0
    bera_count = 0
    main_channel = None
    guild = None
    run = False
    busy_flag = False

    async def acquire(self):
        self.busy_flag = True

    def release(self):
        self.busy_flag = False

    @staticmethod
    def get_username(user):
        if user.nick is None:
            return user.name
        return user.nick

    def say_number(self, number):
        self.bera_count += number
        if self.bera_count >= 31:
            return True
        else:
            return False

    async def clear(self, msg):
        self.user_list = []
        self.user_index = 0
        self.run = False
        await msg.channel.send(f'>>> ***게임 오버***')


bera = Bera()


@static.DiscordModule.assign_onready(bera)
async def on_ready(discord_bot: static.DiscordBot, self: Bera):
    self.main_channel = discord_bot.client.get_channel(config.discord_info['free channel id'])
    self.guild = discord_bot.client.get_guild(config.discord_info['black cow guild id'])
    channel_filter = [self.main_channel]

    @static.CommandBinding.assign_command(discord_bot, '배라', channel_filter)
    async def make_reload(bot: static.DiscordBot, query: list, msg: discord.Message):
        if len(query) == 0:
            desc = '>>> ***배라***\n' + \
                   'ㄱ배라 김윤수 <-- 러시안 룰렛게임에 참가합니다. 따옴표로 여러명을 여러번 넣을 수 있습니다.\n' + \
                   'ㄱ시작 <-- 러시안 룰렛 인원을 확정하고 게임을 시작합니다.\n' + \
                   'ㄱ3 <-- 3을 말합니다.\n' + \
                   'ㄱ종료 배라 <-- 게임을 종료합니다.'
            await msg.channel.send(desc)
        else:
            if self.run:
                await msg.channel.send(f'>>> 진행중에는 참가가 불가합니다.')
                return
            if self.busy_flag:
                return
            await self.acquire()
            for value in query:
                if len(value) > 0:
                    user = None
                    for member in self.guild.members:
                        if member.nick is not None:
                            if member.nick.find(value) != -1:
                                user = member
                                break
                        else:
                            if member.name.find(value) != -1:
                                user = member
                                break
                    if user is not None:
                        self.user_list.append(user)
            size = len(self.user_list)
            if size == 0:
                await msg.add_reaction(emoji='0️⃣')
                self.run = False
            else:
                self.run = True
                if size == 1:
                    await msg.add_reaction(emoji='1️⃣')
                elif size == 2:
                    await msg.add_reaction(emoji='2️⃣')
                elif size == 3:
                    await msg.add_reaction(emoji='3️⃣')
                elif size == 4:
                    await msg.add_reaction(emoji='4️⃣')
                elif size == 5:
                    await msg.add_reaction(emoji='5️⃣')
                elif size == 6:
                    await msg.add_reaction(emoji='6️⃣')
                elif size == 7:
                    await msg.add_reaction(emoji='7️⃣')
                elif size == 8:
                    await msg.add_reaction(emoji='8️⃣')
                elif size == 9:
                    await msg.add_reaction(emoji='9️⃣')
                elif size == 10:
                    await msg.add_reaction(emoji='🔟')
                else:
                    await msg.add_reaction(emoji='🔢')
            self.release()

    @static.CommandBinding.assign_command(discord_bot, '시작', channel_filter)
    async def lock(bot: static.DiscordBot, query: list, msg: discord.Message):
        if not self.run:
            return
        if self.busy_flag:
            return
        await self.acquire()
        if len(self.user_list) == 0:
            await msg.channel.send('참가한 사람이 없습니다.')
            return
        self.user_index = 0
        self.bera_count = 1
        await msg.channel.send(f'>>> ***게임 시작***')
        desc = ''
        for k, user in enumerate(self.user_list):
            if k > 0:
                desc += ', '
            desc += self.get_username(user)
        await msg.channel.send('총 인원: ' + desc)
        await msg.channel.send(f'다음 순서: <@{self.user_list[self.user_index].id}>')
        self.run = True
        self.release()

    @static.CommandBinding.assign_command(discord_bot, '1', channel_filter)
    async def fire(bot: static.DiscordBot, query: list, msg: discord.Message):
        if not self.run:
            return
        if self.busy_flag:
            return
        await self.acquire()
        if len(self.user_list) == 0:
            await msg.channel.send('참가한 사람이 없습니다.')
        elif msg.author.id == self.user_list[self.user_index].id:
            target_name = self.get_username(self.user_list[self.user_index])
            text = ''
            does_say_31 = False
            for k in range(1):
                if k > 0:
                    text += ", "
                text += str(self.bera_count)
                if self.bera_count == 31:
                    does_say_31 = True
                    break
                self.bera_count += 1
            await msg.channel.send(f'{target_name}(이)가 {text} 를 말 했습니다.')
            await asyncio.sleep(1)
            if does_say_31:
                await msg.channel.send(f'<@{self.user_list[self.user_index].id}>(은)는 죽었습니다.')
                await asyncio.sleep(1)
                await self.clear(msg)
            else:
                self.user_index = (self.user_index + 1) % len(self.user_list)
                await msg.channel.send(f'다음 순서: <@{self.user_list[self.user_index].id}>')
        self.release()

    @static.CommandBinding.assign_command(discord_bot, '2', channel_filter)
    async def fire(bot: static.DiscordBot, query: list, msg: discord.Message):
        if not self.run:
            return
        if self.busy_flag:
            return
        await self.acquire()
        if len(self.user_list) == 0:
            await msg.channel.send('참가한 사람이 없습니다.')
        elif msg.author.id == self.user_list[self.user_index].id:
            target_name = self.get_username(self.user_list[self.user_index])
            text = ''
            does_say_31 = False
            for k in range(2):
                if k > 0:
                    text += ", "
                text += str(self.bera_count)
                if self.bera_count == 31:
                    does_say_31 = True
                    break
                self.bera_count += 1
            await msg.channel.send(f'{target_name}(이)가 {text} 를 말 했습니다.')
            await asyncio.sleep(1)
            if does_say_31:
                await msg.channel.send(f'<@{self.user_list[self.user_index].id}>(은)는 죽었습니다.')
                await asyncio.sleep(1)
                await self.clear(msg)
            else:
                self.user_index = (self.user_index + 1) % len(self.user_list)
                await msg.channel.send(f'다음 순서: <@{self.user_list[self.user_index].id}>')
        self.release()

    @static.CommandBinding.assign_command(discord_bot, '3', channel_filter)
    async def fire(bot: static.DiscordBot, query: list, msg: discord.Message):
        if not self.run:
            return
        if self.busy_flag:
            return
        await self.acquire()
        if len(self.user_list) == 0:
            await msg.channel.send('참가한 사람이 없습니다.')
        elif msg.author.id == self.user_list[self.user_index].id:
            target_name = self.get_username(self.user_list[self.user_index])
            text = ''
            does_say_31 = False
            for k in range(3):
                if k > 0:
                    text += ", "
                text += str(self.bera_count)
                if self.bera_count == 31:
                    does_say_31 = True
                    break
                self.bera_count += 1
            await msg.channel.send(f'{target_name}(이)가 {text} 를 말 했습니다.')
            await asyncio.sleep(1)
            if does_say_31:
                await msg.channel.send(f'<@{self.user_list[self.user_index].id}>(은)는 죽었습니다.')
                await asyncio.sleep(1)
                await self.clear(msg)
            else:
                self.user_index = (self.user_index + 1) % len(self.user_list)
                await msg.channel.send(f'다음 순서: <@{self.user_list[self.user_index].id}>')
        self.release()

    @static.CommandBinding.assign_command(discord_bot, '종료', channel_filter)
    async def end_game(bot: static.DiscordBot, query: list, msg: discord.Message):
        if not self.run:
            return
        if '배라' not in query:
            return
        if self.busy_flag:
            return
        await self.acquire()
        await self.clear(msg)
        self.release()
