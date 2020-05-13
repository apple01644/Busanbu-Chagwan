import asyncio
import random

import discord

import static
from . import GameInterface, GameChannel, game_manager


class MafiaUser:
    def __init__(self, pk, user, name, role='citizen', live=True):
        self.pk = pk
        self.user = user
        self.role = role
        self.live = live
        self.name = name
        self.dm_channel = None
        self.mute_by_pol = False
        self.report_count = 0
        self.armor_count = 1
        self.give_life_count = 0
        self.embargo_count = 0
        self.terror_target = -1
        self.gamble_count = 0

    async def get_dm_channel(self):
        self.dm_channel = self.user.dm_channel
        if self.dm_channel is None:
            self.dm_channel = await self.user.create_dm()

    async def permission_edit(self, mute: bool, deafen: bool):
        try:
            await self.user.edit(reason='For mafia', mute=mute, deafen=deafen)
        except discord.HTTPException as he:
            repr(he)


class MafiaGame(GameInterface):
    TITLE = '마피아'
    MIN_USER = 4
    MAX_USER = 8
    police = 'police'
    doctor = 'doctor'
    mafia = 'mafia'
    terrorist = 'terrorist'
    politician = 'politician'
    reporter = 'reporter'
    leader = 'leader'
    shaman = 'shaman'
    miner = 'miner'
    gambler = 'gambler'

    def __init__(self):
        GameInterface.__init__(self)
        self.COMMANDS = {'종료': self.end_game}
        self.LISTENER = self.listener

        self.MAFIA_TYPE_A_COMMANDS = {'계엄령': self.toggle_martial_law, '찬성': self.add_yes_count, '반대': self.add_no_count}
        self.MAFIA_TYPE_B_COMMANDS = {'조사': self.search, '공격': self.attack, '투표': self.vote, '보호': self.heal,
                                      '특종작성': self.write_report, '목표설정': self.set_terror_target, '입막음': self.embargo,
                                      '성불': self.give_life, '승부': self.begin_gamble}
        self.busy = False
        self.players = []
        self.nick_to_id = {}
        self.mode = 'unknown'
        self.chooses = {}
        self.is_active_boolean_chooses = False
        self.boolean_chooses = {}
        self.day = 0
        self.run = False
        self.martial_law = False
        self.gamble_law = None
        self.gamble_chooses = {}

    async def start(self):
        await self.acquire_mutex()
        self.day = 0
        self.run = True
        self.martial_law = False

        dices = [k for k in range(len(self.users))]
        random.shuffle(dices)
        self.players = [MafiaUser(pk=k, user=self.users[username], name=username) for k, username in
                        enumerate(self.users)]
        self.nick_to_id = {nick: k for k, nick in enumerate(self.users)}

        for player in self.players:
            await player.get_dm_channel()

        self.players[dices[0]].role = self.mafia
        self.players[dices[1]].role = self.doctor
        self.players[dices[2]].role = 'police'
        if len(self.players) >= 6:
            self.players[dices[3]].role = self.mafia
            await self.send_message_for_mafia(self.players[dices[0]], '뭘 그렇게 보쇼? 나 마피아요')
            await self.send_message_for_mafia(self.players[dices[3]], '뭘 그렇게 보쇼? 나 마피아요')
            special_role_list = [self.shaman, self.reporter, self.politician, self.terrorist, self.leader, self.miner,
                                 self.gambler]
            random.shuffle(special_role_list)
            for k in range(len(self.players) - 4):
                self.players[dices[4 + k]].role = special_role_list[k]

        for player in self.players:
            embed = self.get_role_embed(player.role)
            embed.set_author(name=player.name, icon_url=player.user.avatar_url)
            await player.dm_channel.send(embed=embed)
            await player.permission_edit(mute=True, deafen=True)

        self.busy = False
        self.mode = '밤'
        await self.broadcast('>>> 40초 뒤 해가 뜹니다.')
        await self.delay(10)
        while self.run:
            await self.broadcast('>>> 30초 뒤 해가 뜹니다.')
            await self.delay(20)
            await self.broadcast('>>> 10초 뒤 해가 뜹니다.')
            await self.delay(7)
            await self.broadcast('>>> 3초 뒤 해가 뜹니다.')
            await self.delay(1)
            await self.broadcast('>>> 2초 뒤 해가 뜹니다.')
            await self.delay(1)
            await self.broadcast('>>> 1초 뒤 해가 뜹니다.')
            await self.delay(1)
            if not self.run:
                break
            await self.day_begin()
            if not self.run:
                break
            for player in self.players:
                if player.live:
                    await player.permission_edit(mute=False, deafen=False)
                else:
                    await player.permission_edit(mute=True, deafen=False)
            if self.is_game_finished() != '':
                break

            await self.broadcast('>>> 60초 뒤 해가 저뭅니다.')
            await self.delay(30)
            await self.broadcast('>>> 30초 뒤 해가 저뭅니다.')
            await self.delay(20)
            await self.broadcast('>>> 10초 뒤 해가 저뭅니다.')
            await self.delay(7)
            await self.broadcast('>>> 3초 뒤 해가 저뭅니다.')
            await self.delay(1)
            await self.broadcast('>>> 2초 뒤 해가 저뭅니다.')
            await self.delay(1)
            await self.broadcast('>>> 1초 뒤 해가 저뭅니다.')
            await self.delay(1)
            if not self.run:
                break
            await self.night_begin()
            if not self.run:
                break
            if self.is_game_finished() != '':
                break
            for player in self.players:
                if player.live:
                    await player.permission_edit(mute=True, deafen=True)
                else:
                    await player.permission_edit(mute=False, deafen=False)

        await self.end_game()

    async def delay(self, seconds: int):
        if self.mode == '낮':
            for k in range(seconds * 10):
                while self.gamble_law is not None:
                    await asyncio.sleep(0.1)
                if self.is_vote_finished() or (not self.run):
                    break
                await asyncio.sleep(0.1)
        else:
            for k in range(seconds * 10):
                if not self.run:
                    break
                await asyncio.sleep(0.1)

    def get_role_embed(self, role: str):
        embed = discord.Embed()
        embed.title = f'당신은 시민입니다.'
        embed.description = 'ㄱ투표 홍길동 : 이 명령어로 낮에 죽일 사람을 결정할 수 있습니다.'

        if role == self.doctor:
            embed.title = f'당신은 의사입니다.'
            embed.description += '\nㄱ보호 홍길동 : 이 명령어로 매일 밤 마다 마피아로부터 지킬 사람을 결정할 수 있습니다.'
            embed.description += '\n당신은 의사입니다. 경찰/시민과 협력해서 시민팀을 승리로 이끄세요.'
        elif role == self.mafia:
            embed.title = f'당신은 마피아입니다.'
            embed.description += '\nㄱ공격 홍길동 : 이 명령어로 마피아들은 매일 밤 마다 죽일 사람을 1명 결정할 수 있습니다.'
            embed.description += '\n당신은 마피아입니다. 시민들을 기망하고 경찰/의사를 사칭하여 마피아팀을 승리로 이끄세요.'
        elif role == 'police':
            embed.title = f'당신은 경찰입니다.'
            embed.description += '\nㄱ조사 홍길동 : 이 명령어로 매일 밤 마다 사람을 조사할 수 있습니다.(즉발)'
            embed.description += '\n당신은 경찰입니다. 진실을 알리고 마피아를 찾아내 시민팀을 승리로 이끄세요.'
        elif role == self.reporter:
            embed.title = f'당신은 기자입니다.'
            embed.description += '\nㄱ특종작성 홍길동 : 이 명령어로 밤에 특종 작성하여 다음날 그 사람을 직업을 공표 할 수 있습니다.(1회용)'
            embed.description += '\n당신은 기자입니다. 주목받는 특종을 내십시요.'
        elif role == self.politician:
            embed.title = f'당신은 정치인입니다.'
            embed.description += '\n지지자: 정치인은 지지자덕분에 투표 할 때 1표를 더 가집니다.'
            embed.description += '\n불체포특권: 정치인은 투표로 죽지 않습니다.'
            embed.description += '\nㄱ입막음: 해당하는 인물을 하루동안 낮에 입 막음을 합니다.(1회용/즉발)'
            embed.description += '\n당신은 정치인입니다. 다른 사람들이 당신은 뜻을 따르도록 하세요.'
        elif role == self.terrorist:
            embed.title = f'당신은 테러리스트입니다.'
            embed.description += '\n폭사 : 투표로 죽게되면 대상으로 정한 사람을 같이 죽입니다.'
            embed.description += '\nㄱ목표설정 홍길동 : 이 명령어로 폭사할 때 죽일 사람을 정할 수 있습니다.(즉발)'
            embed.description += '\n당신은 테러리스트입니다. 당신은 능력으로 세상을 공포 속으로 빠트리세요.'
        elif role == self.leader:
            embed.title = f'당신은 장군입니다.'
            embed.description += '\n방탄복: 마피아의 공격을 버틸 수 있습니다.(1회용)'
            embed.description += '\nㄱ계엄렴 : 이 명령어로 낮에 투표를 활성화/비활성화 할 수 있습니다.(방탄복 비활성 시/즉발)'
            embed.description += '\n당신은 장군입니다. 시민들이 혼란에 빠지지 않도록 하세요.'
        elif role == self.shaman:
            embed.title = f'당신은 무당입니다.'
            embed.description += '\n신내림: 밤에 죽은 혼들을 불러 대화할 수 있습니다.'
            embed.description += '\nㄱ성불: 이 명령어로 밤에 부활 시킬사람을 결정합니다.(즉발/1회용)'
            embed.description += '\n당신은 무당입니다. 억울하게 죽은 사람들의 원한을 풀어주세요.'
        elif role == self.miner:
            embed.title = f'당신은 도굴꾼입니다.'
            embed.description += '\n도굴: 첫날 밤에 죽은 사람의 직업을 얻습니다.'
            embed.description += '\n당신은 도굴꾼입니다. 당신의 잠재적인 능력을 믿으세요.'
        elif role == self.gambler:
            embed.title = f'당신은 승부사입니다.'
            embed.description += '\nㄱ승부: 낮에 다른 사람에게 승부를 겁니다. 승부에서 패배한 쪽은 즉사합니다.(하루 1번)'
            embed.description += '\n당신은 승부사입니다. 가장 위험한 도전을 하여 가장 달콤한 승리를 쟁취하세요.'
        return embed

    async def broadcast_report(self, actor: MafiaUser, target: MafiaUser):
        embed = discord.Embed()
        embed.set_author(name=f'기자 {actor.name}', icon_url=actor.user.avatar_url)
        if random.randint(0, 2) == 0:
            embed.title = '[단독] '
        elif random.randint(0, 1) == 0:
            embed.title = '[속보] '
        else:
            embed.title = '[뉴스] '

        if target.role == self.mafia:
            embed.title += f'{target.name}은 마피아로 밝혀졌습니다!!!'
        elif target.role == self.police:
            embed.title += f'{target.name}은 경찰로 밝혀졌습니다!!!'
        elif target.role == self.doctor:
            embed.title += f'{target.name}은 의사로 밝혀졌습니다!!!'
        elif target.role == self.reporter:
            embed.title += f'{target.name}은 기자로 밝혀졌습니다!!!'
        elif target.role == self.politician:
            embed.title += f'{target.name}은 정치인으로 밝혀졌습니다!!!'
        elif target.role == self.terrorist:
            embed.title += f'{target.name}은 테러리스트로 밝혀졌습니다!!!'
        elif target.role == self.leader:
            embed.title += f'{target.name}은 장군으로 밝혀졌습니다!!!'
        elif target.role == self.shaman:
            embed.title += f'{target.name}은 무당으로 밝혀졌습니다!!!'
        elif target.role == self.miner:
            embed.title += f'{target.name}은 도굴꾼으로 밝혀졌습니다!!!'
        else:
            embed.title += f'{target.name}은 무직고졸백수로 밝혀졌습니다!!!'
        await self.broadcast(embed=embed)

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

    async def acquire_mutex(self):
        while self.busy:
            await asyncio.sleep(0.05)
        self.busy = True

    def is_game_finished(self):
        mafia_count = 0
        citizen_count = 0
        for player in self.players:
            if player.live:
                if player.role == self.mafia:
                    mafia_count += 1
                else:
                    citizen_count += 1
        if mafia_count == 0:
            return 'citizen_win'
        elif citizen_count == mafia_count:
            return 'mafia_win'
        else:
            return ''

    def is_vote_finished(self):
        for player in self.players:
            if player.live:
                if player.pk not in self.chooses:
                    return False
        return True

    async def broadcast(self, content=None, embed=None):
        for player in self.players:
            await player.dm_channel.send(content=content, embed=embed)

    async def send_message_for_everyone(self, target: MafiaUser, content: str):
        embed = discord.Embed()
        embed.set_author(name=target.name, icon_url=target.user.avatar_url)
        embed.description = content
        for player in self.players:
            if player.pk != target.pk:
                await player.dm_channel.send(embed=embed)

    async def send_message_for_mafia(self, target: MafiaUser, content: str):
        embed = discord.Embed()
        embed.set_author(name=target.name, icon_url=target.user.avatar_url)
        embed.description = content
        for player in self.players:
            if player.pk != target.pk:
                if player.live and player.role == self.mafia:
                    await player.dm_channel.send(embed=embed)

    async def send_message_for_afterlives(self, target: MafiaUser, content: str):
        embed = discord.Embed()
        embed.set_author(name=target.name, icon_url=target.user.avatar_url)
        embed.description = content
        for player in self.players:
            if player.pk != target.pk:
                if (not player.live) or player.role == self.shaman:
                    await player.dm_channel.send(embed=embed)

    def get_user_by_id(self, user: discord.User):
        for player in self.players:
            if player.user.id == user.id:
                return player
        return None

    async def day_begin(self):
        await self.acquire_mutex()
        self.mode = '낮'
        self.day += 1
        embed = discord.Embed()
        embed.description = ''

        if self.mafia in self.chooses:
            target = self.players[self.chooses[self.mafia]]
            embed.set_author(name=f'{self.day}일차 낮입니다.', icon_url=target.user.avatar_url)
            kill = True

            if self.doctor in self.chooses:
                if target.pk == self.chooses[self.doctor]:
                    embed.title = f'의사가 {target.name}(을)를 살려냈습니다.'
                    kill = False
            if kill:
                if target.role == self.leader:
                    if target.armor_count > 0:
                        target.armor_count -= 1
                        embed.title = f'장군 {target.name}(이)가 신변의 위협을 받았으나 가벼운 총상만 입었습니다.'
                        kill = False
            if kill:
                if target.role == self.leader:
                    if self.martial_law:
                        self.martial_law = False
                        martial_law_embed = discord.Embed()
                        martial_law_embed.set_author(name=f'장군 {target.name}', icon_url=target.user.avatar_url)
                        martial_law_embed.title = '지금부터 계엄령을 해제합니다.'
                        await self.broadcast(embed=martial_law_embed)

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
                    embed.title = f'{target.name}님이 행방불명 됐습니다.'
                target.live = False
                await target.permission_edit(mute=False, deafen=False)

                for player in self.players:
                    if player.role == self.miner:
                        if self.day == 1:
                            player.role = target.role
                            miner_embed = self.get_role_embed(player.role)
                            miner_embed.set_author(name=player.name, icon_url=player.user.avatar_url)
                            await player.dm_channel.send(embed=miner_embed)
                    elif player.role == self.gambler:
                        player.gamble_count = 0
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

        if self.shaman in self.chooses:
            actor = self.players[self.chooses[self.shaman][0]]
            actor.give_life_count += 1

            target = self.players[self.chooses[self.shaman][1]]
            embed = discord.Embed()
            embed.set_author(name=f'{target.name}', icon_url=target.user.avatar_url)
            embed.title = '당신은 긴 잠에서 깨어났습니다.'
            embed.description = '당신이 죽었다고 생각하였으나 그저 기분나쁜 꿈이였나 봅니다. 그러나 다른 생존자들은 아직 당신이 살았다는것을 모릅니다.'
            target.live = True
            await target.dm_channel.send(embed=embed)
            await target.permission_edit(mute=False, deafen=False)

        if self.reporter in self.chooses:
            actor = self.players[self.chooses[self.reporter][0]]
            actor.report_count += 1

            target = self.players[self.chooses[self.reporter][1]]
            await self.broadcast_report(actor, target)

        self.chooses = {}
        self.busy = False

    async def night_begin(self):
        await self.acquire_mutex()
        votes = {}
        for vote in self.chooses.values():
            if vote not in votes:
                votes[vote] = 1
            else:
                votes[vote] += 1
        votes = [[pk, value] for pk, value in sorted(votes.items(), key=lambda item: item[1])]
        if self.martial_law:
            await self.broadcast(f'>>> 계엄령으로 인해 투표는 무산 되었습니다.')
        elif len(votes) > 0:
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
                await self.broadcast(f'>>> 최다득표자가 1명이 넘습니다.')
            elif self.players[votes[-1][0]].role == self.politician:
                await self.broadcast(
                    f'>>> 그러나 피선거자인 {self.players[votes[-1][0]].name}(은)는 국회의원은 헌법 44조'
                    '"현행범인 경우를 제외하고는 회기중 국회의 동의 없이 체포 또는 구금되지 아니한다." 에 의거하여 사형이 불가합니다./')
            else:
                target = self.players[votes[-1][0]]
                self.boolean_chooses = {}
                self.is_active_boolean_chooses = True
                await self.broadcast(f'>>> {target.name}를 사형 할 것입니까?\nㄱ찬성 or ㄱ반대')
                self.busy = False
                await self.broadcast(f'>>> 20초 후 찬성/반대 투표가 끝납니다.')
                await self.delay(10)
                await self.broadcast(f'>>> 10초 후 찬성/반대 투표가 끝납니다.')
                await self.delay(7)
                await self.broadcast(f'>>> 3초 후 찬성/반대 투표가 끝납니다.')
                await self.delay(1)
                await self.broadcast(f'>>> 2초 후 찬성/반대 투표가 끝납니다.')
                await self.delay(1)
                await self.broadcast(f'>>> 1초 후 찬성/반대 투표가 끝납니다.')
                await self.delay(1)

                await self.acquire_mutex()
                self.is_active_boolean_chooses = False
                yes_count = 0
                no_count = 0
                for boolean in self.boolean_chooses.values():
                    if boolean:
                        yes_count += 1
                    else:
                        no_count += 1

                await self.broadcast(f'>>> 개표 결과 찬성 {yes_count}표, 반대 {no_count}표 입니다.')
                if yes_count > no_count:
                    target.live = False
                    await target.permission_edit(mute=False, deafen=False)

                    embed = discord.Embed()
                    embed.set_author(name=target.name, icon_url=target.user.avatar_url)
                    embed.title = f'{target.name}는 민주적 절차에 따라 사형되었습니다.'

                    await self.broadcast(embed=embed)
                    await asyncio.sleep(1)
                    if target.role == self.mafia:
                        await self.broadcast('>>> 그는 마피아로 밝혀졌습니다.')
                    elif target.role == self.terrorist:
                        await self.broadcast('>>> 그는 테러리스트로 밝혀졌습니다.')
                        if target.terror_target != -1:
                            await asyncio.sleep(1)
                            terror_target = self.players[target.terror_target]
                            if terror_target.live:
                                terror_target.live = False
                                await self.broadcast(f'>>> {terror_target.name}가 집에 들어가는 순간 폭발과 함께 사라졌습니다.')
                                await terror_target.permission_edit(mute=False, deafen=False)

                            else:
                                await self.broadcast(f'>>> {terror_target.name}의 집에서 폭발음이 들었습니다.')
                    else:
                        await self.broadcast('>>> 그는 선량한 시민으로 밝혀졌습니다.')
        await asyncio.sleep(1)
        await self.broadcast('>>> ...해가 저뭅니다')
        await self.daily_alarm()
        self.mode = '밤'
        self.chooses = {}

        for player in self.players:
            if player.role == self.shaman:
                await self.send_message_for_afterlives(player, '무당이 죽은 혼들을 부르고 있습니다...')
            elif player.mute_by_pol:
                player.mute_by_pol = False

        self.busy = False

    async def listener(self, channel: GameChannel, bot: static.DiscordBot, msg: discord.Message):
        await self.acquire_mutex()
        repr(bot)

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

        matched = False
        while True:
            for command in self.MAFIA_TYPE_A_COMMANDS:
                if msg.content.strip() == f'ㄱ{command}':
                    await self.MAFIA_TYPE_A_COMMANDS[command](actor, msg)
                    matched = True
                    break
            if matched:
                break
            for command in self.MAFIA_TYPE_B_COMMANDS:
                if msg.content.find(f'ㄱ{command} ') == 0:
                    query = msg.content[len(command) + 2:].strip()
                    if query not in self.nick_to_id:
                        self.busy = False
                        return
                    target = self.players[self.nick_to_id[query]]
                    await self.MAFIA_TYPE_B_COMMANDS[command](actor, target, msg)
                    matched = True
                    break
            if matched:
                break
            if msg.content.find('ㄱ') == 0:
                await msg.add_reaction(emoji='🛑')
            else:
                if actor.live and self.mode == '낮' and (not actor.mute_by_pol):
                    await self.send_message_for_everyone(actor, msg.content)
                elif self.mode == '밤':
                    if actor.live and actor.role == self.mafia:
                        await self.send_message_for_mafia(actor, msg.content)
                    elif (not actor.live) or actor.role == self.shaman:
                        await self.send_message_for_afterlives(actor, msg.content)
            break

        self.busy = False

    async def vote(self, actor: MafiaUser, target: MafiaUser, msg: discord.Message):
        if not actor.live:
            await msg.add_reaction(emoji='💀')
            return

        if self.mode != '낮':
            await msg.channel.send('>>> 낮에만 투표할 수 있습니다.')
            return

        if self.martial_law:
            await self.broadcast(f'>>> 계엄령으로 인해 투표를 진행할 수 없습니다.')

        if actor.pk in self.chooses:
            await msg.channel.send('>>> 이미 투표했습니다.')
            return

        if not target.live:
            await msg.channel.send('>>> 죽은 사람을 투표 대상으로 삼을 수 없습니다.')
            return

        self.chooses[actor.pk] = target.pk

        await msg.add_reaction(emoji='👌')
        await self.send_message_for_everyone(actor, f'{target.name}에게 1표를 주었습니다.')

        if actor.role == self.politician:
            self.chooses[f'pol_clone'] = target.pk
            await self.send_message_for_everyone(actor, f'{actor.name}의 지지자가 1표를 주었습니다.')

    async def search(self, actor: MafiaUser, target: MafiaUser, msg: discord.Message):
        if not actor.live:
            await msg.add_reaction(emoji='💀')
            return

        if self.mode != '밤':
            await msg.channel.send('>>> 밤에만 조사할 수 있습니다.')
            return

        if actor.role != self.police:
            await msg.channel.send('>>> ㄱ조사 명령어는 경찰만 사용 가능합니다.')
            return

        if actor.pk == target.pk:
            await msg.channel.send('>>> 자기 자신을 조사할 수 없습니다.')
            return

        if self.police in self.chooses:
            await msg.channel.send('>>> 이미 조사했습니다.')
            return

        if not target.live:
            await msg.channel.send('>>> 죽은 사람을 조사 대상으로 삼을 수 없습니다.')
            return

        self.chooses[self.police] = target.pk
        if target.role == self.mafia:
            await msg.channel.send('>>> 조사한 결과 그는 마피아입니다.')
        else:
            await msg.channel.send('>>> 조사한 결과 그는 마피아가 아닙니다.')

    async def attack(self, actor: MafiaUser, target: MafiaUser, msg: discord.Message):
        if not actor.live:
            await msg.add_reaction(emoji='💀')
            return

        if self.mode != '밤':
            await msg.channel.send('>>> 밤에만 공격할 수 있습니다.')
            return

        if actor.role != self.mafia:
            await msg.channel.send('>>> ㄱ공격 명령어는 마피아만 사용 가능합니다.')
            return

        if actor.pk == target.pk:
            await msg.channel.send('>>> 자기 자신을 공격 할 수 없습니다.')
            return

        if not target.live:
            await msg.channel.send('>>> 죽은 사람을 공격 대상으로 삼을 수 없습니다.')
            return

        await self.send_message_for_mafia(actor, f'{target.name}를 공격 대상으로 삼았습니다.')

        self.chooses[self.mafia] = target.pk
        await msg.add_reaction(emoji='👌')

    async def heal(self, actor: MafiaUser, target: MafiaUser, msg: discord.Message):
        if not actor.live:
            await msg.add_reaction(emoji='💀')
            return

        if self.mode != '밤':
            await msg.channel.send('>>> 밤에만 보호할 수 있습니다.')
            return

        if actor.role != self.doctor:
            await msg.channel.send('>>> ㄱ보호 명령어는 의사만 사용 가능합니다.')
            return

        if not target.live:
            await msg.channel.send('>>> 죽은 사람을 보호 대상으로 삼을 수 없습니다.')
            return

        self.chooses[self.doctor] = target.pk
        await msg.add_reaction(emoji='👌')

    async def write_report(self, actor: MafiaUser, target: MafiaUser, msg: discord.Message):
        if not actor.live:
            await msg.add_reaction(emoji='💀')
            return

        if self.mode != '밤':
            await msg.channel.send('>>> 밤에만 특종을 낼 수 있습니다.')
            return

        if actor.role != self.reporter:
            await msg.channel.send('>>> ㄱ특종 명령어는 기자만 사용 가능합니다.')
            return

        if actor.report_count > 0:
            await msg.channel.send('>>> 이미 특종을 냈습니다.')
            return

        self.chooses[self.reporter] = [actor.pk, target.pk]

    async def set_terror_target(self, actor: MafiaUser, target: MafiaUser, msg: discord.Message):
        if not actor.live:
            await msg.add_reaction(emoji='💀')
            return

        if actor.role != self.terrorist:
            await msg.channel.send('>>> ㄱ목표설정 명령어는 테러리스트만 사용 가능합니다.')
            return

        if actor.pk != target.pk:
            await msg.channel.send('>>> 스스로를 인질로 삼을수 없습니다.')
            return

        actor.terror_target = target.pk
        await target.dm_channel.send('>>> 테러리스트가 당신을 인질로 설정했습니다.')
        await msg.add_reaction(emoji='👌')

    async def toggle_martial_law(self, actor: MafiaUser, msg: discord.Message):
        if not actor.live:
            await msg.add_reaction(emoji='💀')
            return

        if self.mode != '낮':
            await msg.channel.send('>>> 낮에만 계엄령을 설정/해제 할 수 있습니다.')
            return

        if actor.role != self.leader:
            await msg.channel.send('>>> ㄱ계엄령 명령어는 장군만 사용 가능합니다.')
            return

        if actor.armor_count > 0:
            await msg.channel.send('>>> ㄱ계엄령 명령어는 장군이 신변의 위협을 받았을 때만 사용 가능합니다.')
            return

        embed = discord.Embed()
        embed.set_author(name=f'장군 {actor.name}', icon_url=actor.user.avatar_url)
        self.martial_law = not self.martial_law
        if self.martial_law:
            embed.title = '지금부터 계엄령을 선포합니다. 시민들은 거리로 나오지 말고 자택에서 대기하십시오.'
        else:
            embed.title = '지금부터 계엄령을 해제합니다.'
        await self.broadcast(embed=embed)

    async def give_life(self, actor: MafiaUser, target: MafiaUser, msg: discord.Message):
        if not actor.live:
            await msg.add_reaction(emoji='💀')
            return

        if self.mode != '밤':
            await msg.channel.send('>>> 밤에만 영혼을 성불 시킬 수 있습니다.')
            return

        if actor.role != self.shaman:
            await msg.channel.send('>>> ㄱ성불 명령어는 무당만 사용 가능합니다.')
            return

        if actor.give_life_count > 0:
            await msg.channel.send('>>> ㄱ성불은 1회만  사용가능합니다.')
            return

        if target.live:
            await msg.channel.send('>>> 생존자에게는 성불을 사용할 수 없습니다.')
            return

        self.chooses[self.shaman] = [actor.pk, target.pk]
        await msg.channel.send(f'>>> {target.name}에게 생명을 부여했습니다. 그는 다음날 기적처럼 돌아올것 입니다.')

    async def embargo(self, actor: MafiaUser, target: MafiaUser, msg: discord.Message):
        if not actor.live:
            await msg.add_reaction(emoji='💀')
            return

        if self.mode != '낮':
            await msg.channel.send('>>> 낮에만 입막음을 할 수 있습니다.')
            return

        if actor.role != self.politician:
            await msg.channel.send('>>> ㄱ입막음 명령어는 정치인만 사용 가능합니다.')
            return

        if actor.embargo_count > 0:
            await msg.channel.send('>>> ㄱ입막음 명렁어는 1회만  사용가능합니다.')
            return

        if actor.pk == target.pk:
            await msg.channel.send('>>> 자기 자신에게 입막음을 할 수 없습니다.')
            return

        if not target.live:
            await msg.channel.send('>>> 죽은 자의 입을 막을 수 없습니다.')

        target.mute_by_pol = True
        actor.embargo_count += 1
        embed = discord.Embed()
        embed.set_author(name=target.name, icon_url=target.user.avatar_url)
        embed.title = f'>>> {target.name}는 입막음 당했습니다.'
        embed.description = '당신들 누구야 읍읍!'
        await self.broadcast(embed=embed)
        await target.permission_edit(mute=True, deafen=False)

    async def add_yes_count(self, actor: MafiaUser, msg: discord.Message):
        if not actor.live:
            await msg.add_reaction(emoji='💀')
            return

        if self.is_active_boolean_chooses:
            await msg.channel.send('>>> 찬성/반대 투표 기간이 아닙니다.')
            return

        if actor.pk in self.boolean_chooses:
            await msg.channel.send('>>> 이미 투표 했습니다.')
            return

        self.boolean_chooses[actor.pk] = True
        await msg.add_reaction(emoji='👌')

    async def add_no_count(self, actor: MafiaUser, msg: discord.Message):
        if not actor.live:
            await msg.add_reaction(emoji='💀')
            return

        if self.is_active_boolean_chooses:
            await msg.channel.send('>>> 찬성/반대 투표 기간이 아닙니다.')
            return

        if actor.pk in self.boolean_chooses:
            await msg.channel.send('>>> 이미 투표 했습니다.')
            return

        self.boolean_chooses[actor.pk] = False
        await msg.add_reaction(emoji='👌')

    async def begin_gamble(self, actor: MafiaUser, target: MafiaUser, msg: discord.Message):
        if not actor.live:
            await msg.add_reaction(emoji='💀')
            return

        if not target.live:
            await msg.channel.send('>>> 죽은 자에겐 승부를 걸 수 없습니다.')

        if actor.role != self.gambler:
            await msg.channel.send('>>> ㄱ승부 명령어는 승부사만 사용 가능합니다.')
            return

        if self.mode != '낮':
            await msg.channel.send('>>> 낮에만 승부를 걸 수 있습니다.')
            return

        if actor.pk == target.pk:
            await msg.channel.send('>>> 자기 자신에겐 승부를 걸 수 없습니다.')
            return

        if actor.gamble_count > 0:
            await msg.channel.send('>>> 승부는 하루에 한번만 걸 수 있습니다.')
            return

        actor.gamble_count += 1

        self.gamble_law = [actor.pk, target.pk]
        await self.broadcast(f'>>> {actor.name}이 {target.name}에게 승부를 걸었습니다.\n패배자는 **사망**합니다.')
        text = 'ㄱ가위, ㄱ바위, ㄱ보 중 하나의 명령어를 사용하여 승부를 하십시오. 5초안에 내지 않으면 패배로 간주됩니다.'
        await actor.dm_channel.send(text)
        await target.dm_channel.send(text)
        while True:
            self.gamble_chooses = {}
            self.busy = False

            await self.delay(5)
            await self.acquire_mutex()
            actor_lose = False
            target_lose = False
            if actor.pk not in self.gamble_chooses:
                actor_lose = True
            if target.pk not in self.gamble_chooses:
                target_lose = True

            sign_actor = self.gamble_chooses[actor.pk]
            sign_target = self.gamble_chooses[target.pk]
            if sign_actor == sign_target:
                pass
            elif sign_actor == 'S' and sign_target == 'R':
                actor_lose = True
            elif sign_actor == 'R' and sign_target == 'P':
                actor_lose = True
            elif sign_actor == 'P' and sign_target == 'S':
                actor_lose = True
            else:
                target_lose = True

            if (actor_lose and target_lose) or (not (actor_lose or target_lose)):
                await msg.channel.send('>>> 무승부.')
            else:
                if actor_lose:
                    winner = target
                    loser = actor
                else:
                    winner = actor
                    loser = target
                embed = discord.Embed()
                embed.set_author(name=f'{winner.name}의 승리', icon_url=winner.user.avatar_url)
                embed.description = f'패자 {loser.name}은 죽었습니다.'
                await self.broadcast(embed=embed)
                loser.live = False
                await loser.permission_edit(mute=False, deafen=False)
                break

        self.gamble_law = None

    async def gamble_rock(self, actor: MafiaUser, msg: discord.Message):
        if not actor.live:
            await msg.add_reaction(emoji='💀')
            return

        if self.gamble_law is None:
            await msg.channel.send('>>> 승부 중이 아닙니다.')
            return

        if actor.pk in self.gamble_law:
            await msg.channel.send('>>> 승부 대상이 아닙니다.')
            return

        if actor.pk in self.gamble_chooses:
            await msg.channel.send('>>> 이미 결정했습니다.')
            return

        self.gamble_chooses[actor.pk] = 'R'
        await msg.add_reaction(emoji='👌')

    async def gamble_scissor(self, actor: MafiaUser, msg: discord.Message):
        if not actor.live:
            await msg.add_reaction(emoji='💀')
            return

        if self.gamble_law is None:
            await msg.channel.send('>>> 승부 중이 아닙니다.')
            return

        if actor.pk in self.gamble_law:
            await msg.channel.send('>>> 승부 대상이 아닙니다.')
            return

        if actor.pk in self.gamble_chooses:
            await msg.channel.send('>>> 이미 결정했습니다.')
            return

        self.gamble_chooses[actor.pk] = 'S'
        await msg.add_reaction(emoji='👌')

    async def gamble_paper(self, actor: MafiaUser, msg: discord.Message):
        if not actor.live:
            await msg.add_reaction(emoji='💀')
            return

        if self.gamble_law is None:
            await msg.channel.send('>>> 승부 중이 아닙니다.')
            return

        if actor.pk in self.gamble_law:
            await msg.channel.send('>>> 승부 대상이 아닙니다.')
            return

        if actor.pk in self.gamble_chooses:
            await msg.channel.send('>>> 이미 결정했습니다.')
            return

        self.gamble_chooses[actor.pk] = 'P'
        await msg.add_reaction(emoji='👌')

    async def end_game(self, channel: GameChannel = None, query: list = None, msg: discord.Message = None):
        await self.acquire_mutex()
        repr(query)
        repr(msg)

        if channel is not None:
            if self != channel.running_game:
                self.busy = False
                return
        for player in self.players:
            await player.permission_edit(mute=False, deafen=False)

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

        self.run = False
        self.users = {}
        self.nick_to_id = {}
        self.players = []
        await self.broadcast(f'>>> {self.TITLE}을 종료했습니다.')
        await self.game_channel.channel.send(f'>>> {self.TITLE}을 종료했습니다.')
        self.game_channel.running_game = None
        self.busy = False


game_manager.games['마피아'] = MafiaGame
