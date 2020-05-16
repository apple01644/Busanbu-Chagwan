import asyncio
import io
import json
import os
import random

import discord

import static


class Person:
    __slots__ = ['grade', 'month', 'week', 'money', 'health', 'iq', 'coding', 'lol', 'politic', 'library', 'english',
                 'economy',
                 'traits', 'goodness']

    def __init__(self):
        self.grade = 1
        self.month = 3
        self.week = 1
        self.money = 10
        self.health = 10

        self.iq = 100
        self.coding = 2
        self.lol = 30
        self.politic = 0
        self.library = 30
        self.english = 30
        self.economy = 10
        self.traits = []
        self.goodness = 0

    @staticmethod
    def eval(obj):
        self = Person()
        for key in obj:
            setattr(self, key, obj[key])
        return self

    def dict(self):
        obj = {}
        for key in self.__slots__:
            obj[key] = getattr(self, key, None)
        return obj

    def in_1st_period(self, grade: int):
        return grade == self.grade and 3 <= self.month <= 8

    def in_2nd_period(self, grade: int):
        return grade == self.grade and 9 <= self.month <= 2


class Option:
    def __init__(self):
        self.name = ''
        self.effect = None


class Event:
    def __init__(self):
        self.description = ''
        self.options = []
        self.condition = None
        self.priority = 0

    def assign_condition(self, function):
        self.condition = function

    def assign_option(self, name):
        def assign(function):
            option = Option()
            option.name = name
            option.effect = function
            self.options.append(option)

        return assign


class TrpgManager:
    emote_to_reaction_map = {'1️⃣': 1, '2️⃣': 2, '3️⃣': 3, '4️⃣': 4, '5️⃣': 5, '6️⃣': 6, '7️⃣': 7, '8️⃣': 8,
                             '9️⃣': 9, '🔟': 10}
    number_to_emote_map = {1: '1️⃣', 2: '2️⃣', 3: '3️⃣', 4: '4️⃣', 5: '5️⃣', 6: '6️⃣', 7: '7️⃣', 8: '8️⃣',
                           9: '9️⃣', 10: '🔟', 'other': '🔢'}
    discord_bot = None
    events = []
    busy = {}
    cwd = os.getcwd()

    def load_person(self, pk: int):
        path = os.path.join(self.cwd, f'.data/trpg/{pk}.json')
        if os.path.isfile(path):
            with io.open(path, 'r', encoding='utf-8') as file:
                return Person.eval(json.loads(file.read(), encoding='utf-8'))
        else:
            return Person()

    def store_person(self, pk: int, person: Person):
        path = os.path.join(self.cwd, f'.data/trpg/{pk}.json')
        with io.open(path, 'w', encoding='utf-8') as file:
            file.write(json.dumps(person.dict(), ensure_ascii=False))

    def get_event(self, person: Person):
        events = []
        for event in self.events:
            if event.condition is None:
                events.append(event)
            elif event.condition(person):
                events.append(event)
        if len(events) > 0:
            random.shuffle(events)
            events.sort(key=lambda item: item.priority, reverse=True)
            return events[0]
        return None

    async def run_command(self, command_name: str, query: list, msg: discord.Message):
        pk = msg.author.id
        if pk in self.busy:
            while self.busy[pk]:
                await asyncio.sleep(0.05)
        self.busy[pk] = True
        if command_name == '시작':
            await msg.channel.send('>>> 김윤수는 3개월의 공부 끝에 부산SW마이스터고등학교에 입학했습니다!\n앞으로 어떤 사건을 겪을수 있을까요?')
            person = self.load_person(pk)
            self.store_person(pk, person)
            while True:
                event = self.get_event(person)
                if event is None:
                    await msg.channel.send('>>> 게임오버')
                    break
                text = '>>> ' + event.description + '\n'
                for k, option in enumerate(event.options, 1):
                    text += f'{self.number_to_emote_map[k]} [{option.name}]    '
                bot_msg = await msg.channel.send(text)
                for k in range(len(event.options)):
                    await bot_msg.add_reaction(self.number_to_emote_map[k + 1])
                option_index = -1
                for k in range(490):
                    if option_index != - 1:
                        break
                    msgs = await msg.channel.history(limit=10).flatten()
                    matches = [item for item in msgs if item.id == bot_msg.id]
                    if len(matches) == 0:
                        await msg.add_reaction('❌')
                    else:
                        match = matches[0]
                        for react in match.reactions:
                            if react.emoji not in self.emote_to_reaction_map:
                                continue
                            if self.emote_to_reaction_map[react.emoji] - 1 >= len(event.options):
                                continue
                            users = await react.users().flatten()
                            match = [user.id for user in users if user.id != bot_msg.author.id]# if user.id == pk]
                            if len(match) > 0:
                                option_index = self.emote_to_reaction_map[react.emoji] - 1
                                break
                    await asyncio.sleep(0.05)
                if option_index != -1:
                    await event.options[option_index].effect(msg, person)
                    person.week += 1
                    if person.week == 5:
                        person.week = 1
                        person.month += 1
                        if person.month == 13:
                            person.month = 1
                        if person.month == 3:
                            person.grade += 1
                    self.store_person(pk, person)
                else:
                    break
        else:
            pass
        self.busy[pk] = False

    async def help(self, msg: discord.Message):
        description = '```'
        description += '\n==== 김윤수 키우기 ===='
        description += '\n이 게임은 부산SW마이스터고등학교에 입학한 김윤수를 배경으로 하는 게임입니다.'
        description += '```'
        await msg.channel.send(description)

    def assign_event(self, function):
        event = Event()
        function(event)
        self.events.append(event)


manager = TrpgManager()


@static.DiscordModule.assign_onready(manager)
async def on_ready(discord_bot: static.DiscordBot, self: TrpgManager):
    free_channel = discord_bot.client.get_channel(705958096077324299)
    manager.discord_bot = discord_bot

    @static.CommandBinding.assign_command(discord_bot, '윤수', [free_channel])
    async def get_timetable(bot: static.DiscordBot, query: list, msg: discord.Message):
        if len(query) == 0:
            await self.help(msg)
        else:
            await self.run_command(query[0], query[1:], msg)
