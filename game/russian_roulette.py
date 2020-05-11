import asyncio
import random

import discord

from . import GameInterface, GameChannel, game_manager


class RussianRouletteGame(GameInterface):
    TITLE = '러시안룰렛'
    MIN_USER = 2
    MAX_USER = 6

    def __init__(self):
        GameInterface.__init__(self)
        self.COMMANDS = {'발사': self.shoot, '종료': self.end_game}
        self.busy = False
        self.gun = []
        self.user_list = []
        self.username_list = []
        self.user_index = 0

    async def start(self):
        self.busy = True
        self.on_member_changed()
        await self.show_next_turn()
        self.busy = False

    def on_member_changed(self):
        self.gun = [False for x in range(6)]
        self.gun[random.randint(0, 5)] = True
        self.user_index = 0
        self.username_list = list(self.users.keys())
        self.user_list = list(self.users.values())

    async def show_next_turn(self):
        await self.channel.send(f'>>> 다음 차례는 <@{self.user_list[self.user_index].id}> 입니다.')

    async def shoot(self, channel: GameChannel, query: list, msg: discord.Message):
        if self.busy or self != channel.running_game:
            return
        self.busy = True
        if msg.author.id != self.user_list[self.user_index].id:
            return
        await asyncio.sleep(random.randint(1, 3))
        if self.gun[0]:
            await self.channel.send(f'<:tang:709200132922671106>')
            await self.channel.send(f'>>> <@{self.user_list[self.user_index].id}> 가 죽었습니다.')

            del self.users[self.username_list[self.user_index]]
            self.on_member_changed()

            if len(self.user_list) == 1:
                await self.channel.send(f'>>> 승자는 <@{self.user_list[0].id}> 입니다.')
                self.busy = False
                await self.end_game(channel, query, msg)
                return
            await self.show_next_turn()
        else:
            await self.channel.send(f'<:chulkuk:709200132381474890>')
            self.gun = self.gun[1:]
            self.user_index = (self.user_index + 1) % len(self.users)
            await self.show_next_turn()
        self.busy = False

    async def end_game(self, channel: GameChannel, query: list, msg: discord.Message):
        if self.busy or self != channel.running_game:
            return
        self.busy = True
        self.users = {}
        channel.running_game = None
        self.busy = False


game_manager.games['러시안룰렛'] = RussianRouletteGame
