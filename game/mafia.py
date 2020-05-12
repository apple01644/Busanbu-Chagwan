import asyncio
import random

import discord

import static
from . import GameInterface, GameChannel, game_manager


async def get_dm_channel(user: discord.User):
    ch = user.dm_channel
    if ch is None:
        ch = await user.create_dm()
    return ch


class MafiaUser:
    def __init__(self, pk, user, name, role='citizen', live=True):
        self.pk = pk
        self.user = user
        self.role = role
        self.live = live
        self.name = name


class MafiaGame(GameInterface):
    TITLE = '마피아'
    MIN_USER = 4
    MAX_USER = 8

    def __init__(self):
        GameInterface.__init__(self)
        self.COMMANDS = {'종료': self.end_game}
        self.LISTENER = self.listener
        self.busy = False
        self.players = []
        self.nick_to_id = {}
        self.mode = 'unknown'
        self.chooses = {}
        self.day = 0
        self.run = False

    async def start(self):
        while self.busy:
            await asyncio.sleep(0.05)
        self.busy = True
        self.day = 0
        self.run = True

        dices = [-1 for k in range(4)]
        for k in range(4):
            while True:
                dice = random.randint(0, len(self.users) - 1)
                if dice not in dices:
                    dices[k] = dice
                    break
        self.players = [MafiaUser(pk=k, user=self.users[username], name=username) for k, username in
                        enumerate(self.users)]
        self.nick_to_id = {nick: k for k, nick in enumerate(self.users)}

        self.players[dices[0]].role = 'mafia'
        if len(self.players) >= 6:
            self.players[dices[1]].role = 'mafia'
            self.players[dices[2]].role = 'doctor'
            self.players[dices[3]].role = 'police'
        for player in self.players:
            embed = discord.Embed()
            embed.set_author(name=player.name, icon_url=player.user.avatar_url)
            embed.title = f'당신은 시민입니다.'
            embed.description = 'ㄱ투표 홍길동 : 이 명령어로 낮에 죽일 사람을 결정할 수 있습니다.'

            if player.role == 'doctor':
                embed.title = f'당신은 의사입니다.'
                embed.description += '\nㄱ보호 홍길동 : 이 명령어로 매일 밤 마다 마피아로부터 지킬 사람을 결정할 수 있습니다.'
                embed.description += '\n당신의 의사입니다. 경찰/시민과 협력해서 시민팀을 승리로 이끄세요.'
            elif player.role == 'mafia':
                embed.title = f'당신은 마피아입니다.'
                embed.description += '\nㄱ공격 홍길동 : 이 명령어로 마피아들은 매일 밤 마다 죽일 사람을 1명 결정할 수 있습니다.'
                embed.description += '\n당신의 마피아입니다. 시민들을 기망하고 경찰/의사를 사칭하여 마피아팀을 승리로 이끄세요.'
            elif player.role == 'police':
                embed.title = f'당신은 경찰입니다.'
                embed.description += '\nㄱ조사 홍길동 : 이 명령어로 매일 밤 마다 사람을 조사할 수 있습니다.'
                embed.description += '\n당신의 경찰입니다. 진실을 알리고 마피아를 찾아내 시민팀을 승리로 이끄세요.'

            dm_channel = await get_dm_channel(player.user)
            await dm_channel.send(embed=embed)
            await player.user.edit(reason='For mafia', mute=True, deafen=True)
        self.busy = False
        self.mode = '밤'
        while self.run:
            if self.day > 0:
                await self.broadcast('>>> 60초 뒤 해가 뜹니다.')
                await asyncio.sleep(30)
                if not self.run:
                    break
            await self.broadcast('>>> 30초 뒤 해가 뜹니다.')
            await asyncio.sleep(20)
            if not self.run:
                break
            await self.broadcast('>>> 10초 뒤 해가 뜹니다.')
            await asyncio.sleep(10)
            if not self.run:
                break
            await self.day_begin()
            if not self.run:
                break
            for player in self.players:
                await player.user.edit(reason='For mafia', mute=False, deafen=False)
            if self.is_game_finished() != '':
                break

            if self.day > 1:
                await self.broadcast('>>> 2분 뒤 해가 저뭅니다.')
                await asyncio.sleep(60)
                if not self.run:
                    break
            await self.broadcast('>>> 60초 뒤 해가 저뭅니다.')
            await asyncio.sleep(30)
            if not self.run:
                break
            await self.broadcast('>>> 30초 뒤 해가 저뭅니다.')
            await asyncio.sleep(20)
            if not self.run:
                break
            await self.broadcast('>>> 10초 뒤 해가 저뭅니다.')
            await asyncio.sleep(10)
            if not self.run:
                break
            await self.night_begin()
            if not self.run:
                break
            if self.is_game_finished() != '':
                break

        if self.is_game_finished() == 'citizen_win':
            text = '>>> 시민이 승리했습니다.'
        elif self.is_game_finished() == 'mafia_win':
            text = '>>> 마피아가 승리했습니다.'
        else:
            text = '>>> 비정상적으로 종료 됐습니다.'

        for player in self.players:
            text += f'\n{player.name} {player.role}'
        await self.broadcast(text)
        await self.game_channel.channel.send(text)
        await self.end_game()

    async def daily_alarm(self):
        embed = discord.Embed()
        embed.title = f'{self.day}일차 {self.mode}입니다.'
        embed.description = '생존자들: '
        k = -1
        for player in self.players:
            k += 1
            if player.live:
                if k > 0:
                    embed.description += ', '
                embed.description += player.name
        await self.broadcast(embed=embed)

    def is_game_finished(self):
        mafia_count = 0
        citizen_count = 0
        for player in self.players:
            if player.live:
                if player.role == 'mafia':
                    mafia_count += 1
                else:
                    citizen_count += 1
        if mafia_count == 0:
            return 'citizen_win'
        elif citizen_count == mafia_count:
            return 'mafia_win'
        else:
            return ''

    async def broadcast(self, content=None, embed=None):
        for player in self.players:
            dm_channel = await get_dm_channel(player.user)
            await dm_channel.send(content=content, embed=embed)

    async def send_message_for_everyone(self, target: MafiaUser, content: str):
        embed = discord.Embed()
        embed.set_author(name=target.name, icon_url=target.user.avatar_url)
        embed.description = content
        for player in self.players:
            if player.pk != target.pk:
                dm_channel = await get_dm_channel(player.user)
                await dm_channel.send(embed=embed)

    async def send_message_for_mafia(self, target: MafiaUser, content: str):
        embed = discord.Embed()
        embed.set_author(name=target.name, icon_url=target.user.avatar_url)
        embed.description = content
        for player in self.players:
            if player.pk != target.pk and player.role == 'mafia':
                dm_channel = await get_dm_channel(player.user)
                await dm_channel.send(embed=embed)

    def get_user_by_id(self, user: discord.User):
        for player in self.players:
            if player.user.id == user.id:
                return player
        return None

    async def day_begin(self):
        while self.busy:
            await asyncio.sleep(0.05)
        self.busy = True
        self.mode = '낮'
        self.day += 1
        embed = discord.Embed()
        embed.description = ''
        if 'mafia' in self.chooses:
            target = self.players[self.chooses['mafia']]
            embed.set_author(name=f'{self.day}일차 낮입니다.', icon_url=target.user.avatar_url)
            kill = True

            if 'doctor' in self.chooses:
                if target.pk == self.chooses['doctor']:
                    embed.title = f'의사가 {target.name}>(을)를 살려냈습니다.'
                    kill = False
            if kill:
                embed.title = f'{target.name}님이 사망했습니다.\n'
                k = random.randint(0, 10)
                if k == 0:
                    embed.description = '침실에서 납탄이 머리를 관통한 상태로 발견 됐습니다.'
                elif k == 1:
                    embed.description = '집 안 욕조에서 질식사한 상태로 발견 됐습니다.'
                elif k == 2:
                    embed.description = '집으로 부터 3km 떨어진 곳에서 과다출혈로 사망한 상태로 발견 됐습니다.'
                elif k == 3:
                    embed.description = '약물과다복용으로 인하여 쇼크사한 상태로 발견 되었습니다.'
                elif k == 4:
                    embed.description = '많은 총탄으로 인해 형체를 알아볼 수 없는 시체로 발견 되었습니다.'
                elif k == 5:
                    embed.description = '침실에서 목을 메인 상태로 발견 되었습니다.'
                elif k == 6:
                    embed.description = '해변에 떠내려온 드럼통 내에서 변사체로 발견되었습니다.'
                elif k == 7:
                    embed.description = '근처 산의 등산로에서 시체로 발견 되었습니다.'
                elif k == 8:
                    embed.description = '폭파된 자택에서 발견 되었습니다. 유골은 찾지 못 했습니다.'
                elif k == 9:
                    embed.description = '집 앞 도로에서 경골골절 및 장기부전으로 사망했습니다. '
                else:
                    embed.title = f'{target.nmae}님이 행방불명 됐습니다.'
                target.live = False
                await target.user.edit(reason='For mafia', mute=False, deafen=False)
        else:
            embed.title = '낮이 밝았습니다. 아무일도 일어나지 않았습니다.'
        embed.description += '\n생존자들: '
        k = -1
        for player in self.players:
            k += 1
            if player.live:
                if k > 0:
                    embed.description += ', '
                embed.description += player.name
        await self.broadcast(embed=embed)
        self.chooses = {}
        self.busy = False

    async def night_begin(self):
        while self.busy:
            await asyncio.sleep(0.05)
        self.busy = True
        self.mode = '밤'

        votes = {}
        for vote in self.chooses.values():
            if vote not in votes:
                votes[vote] = 1
            else:
                votes[vote] += 1
        votes = [[pk, value] for pk, value in sorted(votes.items(), key=lambda item: item[1])]

        if len(votes) > 0:
            await self.broadcast(f'>>> 지금부터 투표결과를 알려드리겠습니다.')
            for pair in votes:
                await asyncio.sleep(1)
                await self.broadcast(f'>>> {self.players[pair[0]].name}')
                await asyncio.sleep(1)
                await self.broadcast(f'>>> **{pair[1]}표**')
                await asyncio.sleep(1)

            is_draw = False
            if len(votes) > 1:
                if votes[-1][1] == votes[-2][1]:
                    is_draw = True
            if is_draw:
                await self.broadcast(f'>>> 최다득표자가 1명이 넘기 때문에 투표는 무효가 됩니다.')
            else:
                target = self.players[votes[-1][0]]
                target.live = False
                await target.user.edit(reason='For mafia', mute=False, deafen=False)

                embed = discord.Embed()
                embed.set_author(name=target.name, icon_url=target.user.avatar_url)
                embed.title = f'{target.name}는 민주적 절차에 따라 사형되었습니다.'

                await self.broadcast(embed=embed)
                await asyncio.sleep(1)
                if target.role == 'mafia':
                    await self.broadcast('>>> 그는 마피아로 밝혀졌습니다.')
                else:
                    await self.broadcast('>>> 그는 선량한 시민으로 밝혀졌습니다.')
        await asyncio.sleep(1)
        await self.broadcast('>>> ...해가 저뭅니다')
        await self.daily_alarm()
        self.chooses = {}
        self.busy = False

    async def listener(self, channel: GameChannel, bot: static.DiscordBot, msg: discord.Message):
        while self.busy:
            await asyncio.sleep(0.05)
        self.busy = True

        if not self.run:
            self.busy = False
            return
        if self != channel.running_game:
            self.busy = False
            return

        actor = self.get_user_by_id(msg.author)

        if actor is None:
            self.busy = False

            return

        if not actor.live:
            self.busy = False
            return

        if msg.content.find('ㄱ조사 ') == 0:
            query = msg.content[4:].strip()
            if query not in self.nick_to_id:
                self.busy = False
                return
            target = self.players[self.nick_to_id[query]]
            await self.search(channel, actor, target, msg)
        elif msg.content.find('ㄱ공격 ') == 0:
            query = msg.content[4:].strip()
            if query not in self.nick_to_id:
                self.busy = False
                return
            target = self.players[self.nick_to_id[query]]
            await self.attack(channel, actor, target, msg)
        elif msg.content.find('ㄱ투표 ') == 0:
            query = msg.content[4:].strip()
            if query not in self.nick_to_id:
                self.busy = False
                return
            target = self.players[self.nick_to_id[query]]
            await self.vote(channel, actor, target, msg)
        elif msg.content.find('ㄱ보호 ') == 0:
            query = msg.content[4:].strip()
            if query not in self.nick_to_id:
                self.busy = False
                return
            target = self.players[self.nick_to_id[query]]
            await self.heal(channel, actor, target, msg)
        elif msg.content.find('ㄱ') == 0:
            self.busy = False
            raise Exception('없는 명령어 입니다.')
        else:
            if self.mode == '낮':
                await self.send_message_for_everyone(actor, msg.content)
            elif self.mode == '밤' and actor.role == 'mafia':
                await self.send_message_for_mafia(actor, msg.content)
        self.busy = False

    async def vote(self, channel: GameChannel, actor: MafiaUser, target: MafiaUser, msg: discord.Message):
        if self.mode != '낮':
            await msg.channel.send('>>> 낮에만 투표할 수 있습니다.')
            return

        if actor.pk in self.chooses:
            await msg.channel.send('>>> 이미 투표했습니다.')
            return

        if not target.live:
            await msg.channel.send('>>> 죽은 사람을 투표 대상으로 삼을 수 없습니다.')
            return

        self.chooses[actor.pk] = target.pk
        await msg.add_reaction(emoji='👌')
        await self.send_message_for_everyone(actor, f'{target.name}에게 1표를 주었습니다.')

    async def search(self, channel: GameChannel, actor: MafiaUser, target: MafiaUser, msg: discord.Message):
        if self.mode != '밤':
            await msg.channel.send('>>> 밤에만 조사할 수 있습니다.')
            return

        if actor.role != 'police':
            await msg.channel.send('>>> ㄱ조사 명령어는 경찰만 사용 가능합니다.')
            return

        if 'police' in self.chooses:
            await msg.channel.send('>>> 이미 조사했습니다.')
            return

        if not target.live:
            await msg.channel.send('>>> 죽은 사람을 조사 대상으로 삼을 수 없습니다.')
            return

        self.chooses['police'] = target.pk
        if target.role == 'mafia':
            await msg.channel.send('>>> 조사한 결과 그는 마피아입니다.')
        else:
            await msg.channel.send('>>> 조사한 결과 그는 마피아가 아닙니다.')

    async def attack(self, channel: GameChannel, actor: MafiaUser, target: MafiaUser, msg: discord.Message):
        if self.mode != '밤':
            await msg.channel.send('>>> 밤에만 공격할 수 있습니다.')
            return

        if actor.role != 'mafia':
            await msg.channel.send('>>> ㄱ공격 명령어는 마피아만 사용 가능합니다.')
            return

        if not target.live:
            await msg.channel.send('>>> 죽은 사람을 공격 대상으로 삼을 수 없습니다.')
            return

        self.chooses['mafia'] = target.pk
        await msg.add_reaction(emoji='👌')

    async def heal(self, channel: GameChannel, actor: MafiaUser, target: MafiaUser, msg: discord.Message):
        if self.mode != '밤':
            await msg.channel.send('>>> 밤에만 보호할 수 있습니다.')
            return

        if actor.role != 'doctor':
            await msg.channel.send('>>> ㄱ보호 명령어는 의사만 사용 가능합니다.')
            return

        if not target.live:
            await msg.channel.send('>>> 죽은 사람을 보호 대상으로 삼을 수 없습니다.')
            return

        self.chooses['doctor'] = target.pk
        await msg.add_reaction(emoji='👌')

    async def end_game(self, channel: GameChannel = None, query: list = None, msg: discord.Message = None):
        while self.busy:
            await asyncio.sleep(0.05)
        self.busy = True

        if channel is not None:
            if self != channel.running_game:
                self.busy = False
                return
        for player in self.players:
            await player.user.edit(reason='For mafia', mute=False, deafen=False)

        self.run = False
        self.users = {}
        self.nick_to_id = {}
        self.players = []
        await self.broadcast(f'>>> {self.TITLE}을 종료했습니다.')
        await self.game_channel.channel.send(f'>>> {self.TITLE}을 종료했습니다.')
        self.game_channel.running_game = None
        self.busy = False


game_manager.games['마피아'] = MafiaGame
