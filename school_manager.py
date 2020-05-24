import datetime
import traceback

import discord
from discord.ext import tasks

import config
import static
import requests_async as req
import json
import os


class SchoolManager:
    last_run_date = datetime.datetime.now().date()
    last_run_time = datetime.datetime.now().time()
    alarm_channel = None
    first_channel = None
    second_channel = None
    third_channel = None
    allowed_channels = None

    apart_code = os.getenv('OPEN_NEIS_APART_CODE')
    school_code = os.getenv('OPEN_NEIS_SCHOOL_CODE')
    open_neis_token = os.getenv('OPEN_NEIS_TOKEN')

    bias_for_school_clock = datetime.timedelta(seconds=0)
    class_cached_data = {}
    event_cached_data = {}
    meal_cached_data = {}
    weekday_in_korean = {0: '월', 1: '화', 2: '수', 3: '목', 4: '금', 5: '토', 6: '일'}
    grade_event_attribute_names = ['ONE_GRADE_EVENT_YN', 'TW_GRADE_EVENT_YN', 'THREE_GRADE_EVENT_YN',
                                   'FR_GRADE_EVENT_YN', 'FIV_GRADE_EVENT_YN', 'SIX_GRADE_EVENT_YN']
    meal_names = {1: '아침', 2: '점심', 3: '저녁'}

    @tasks.loop(seconds=1.0)
    async def scheduler_loop(self):
        try:
            await self.heartbeat()
        except Exception as e:
            print(traceback.format_exc(), e)

    async def cache_class_data(self, year, month, day):
        url = 'https://open.neis.go.kr/hub/hisTimetable?Type=json&' + \
              f'KEY={self.open_neis_token}&' + \
              f'ATPT_OFCDC_SC_CODE={self.apart_code}&' + \
              f'SD_SCHUL_CODE={self.school_code}&' + \
              'TI_FROM_YMD={0:04d}{1:02d}{2:02d}&'.format(year, month, day) + \
              'TI_TO_YMD={0:04d}{1:02d}{2:02d}'.format(year, month, day)
        res = await req.get(url)
        assert res.status_code == 200
        data = json.loads(res.content)

        cached_data = {}
        for row in data['hisTimetable'][1]['row']:
            index = f"{row['GRADE']}-{row['CLRM_NM']}"
            if index not in cached_data:
                cached_data[index] = {}
            cached_data[index][int(row['PERIO'])] = row['ITRT_CNTNT']
        cached_data = {key: cached_data[key] for key in sorted(cached_data.keys())}
        self.class_cached_data[f'{month}/{day}/{year}'] = cached_data

    async def cache_event_data(self, year, month, day):
        url = 'https://open.neis.go.kr/hub/SchoolSchedule?Type=json&' + \
              f'KEY={self.open_neis_token}&' + \
              f'ATPT_OFCDC_SC_CODE={self.apart_code}&' + \
              f'SD_SCHUL_CODE={self.school_code}&' + \
              'AA_YMD={0:04d}{1:02d}{2:02d}&'.format(year, month, day)
        res = await req.get(url)
        assert res.status_code == 200
        data = json.loads(res.content)

        cached_data = []
        for row in data['SchoolSchedule'][1]['row']:
            target = []
            for k, grade_attribute_name in enumerate(self.grade_event_attribute_names, 1):
                if row[grade_attribute_name] == 'Y':
                    target.append(k)
            cached_data.append({'type': row['BTR_DD_SC_NM'], 'name': row['EVENT_NM'], 'target': target})
        self.event_cached_data[f'{month}/{day}/{year}'] = cached_data

    async def cache_meal_data(self, year, month, day):
        url = 'https://open.neis.go.kr/hub/mealServiceDietInfo?Type=json&' + \
              f'KEY={self.open_neis_token}&' + \
              f'ATPT_OFCDC_SC_CODE={self.apart_code}&' + \
              f'SD_SCHUL_CODE={self.school_code}&' + \
              'MLSV_YMD={0:04d}{1:02d}{2:02d}&'.format(year, month, day)
        res = await req.get(url)
        assert res.status_code == 200
        data = json.loads(res.content)

        cached_data = {}
        for row in data['mealServiceDietInfo'][1]['row']:
            cached_data[int(row['MMEAL_SC_CODE'])] = row['DDISH_NM']
        self.meal_cached_data[f'{month}/{day}/{year}'] = cached_data

    async def request_class_data(self, query: list, msg: discord.Message, **kwargs):
        grade = 3
        class_number = None
        day = 0
        for k in config.learn_class_info:
            for role in [role.name for role in msg.author.roles]:
                if role == f'3학년 {k}반':
                    class_number = k
            if f'{k}반' in query:
                class_number = k
        assert class_number is not None

        if '내일' in query:
            day += 1
        if '모레' in query:
            day += 2
        if '글피' in query:
            day += 3
        if '다음주' in query:
            day += 7
        if '다다음주' in query:
            day += 14
        if '저번주' in query:
            day -= 7
        if '저저번주' in query:
            day -= 14
        if '저저저번주' in query:
            day -= 21
            
        for k in range(1, 365):
            if (f'{k}일후' in query) or (f'{k}일 후' in query) or (f'{k}일뒤' in query) or (f'{k}일 뒤' in query):
                day = k

        date = datetime.datetime.now().date()

        for weekday_index in self.weekday_in_korean:
            weekday_name = self.weekday_in_korean[weekday_index]
            if (weekday_name in query) or (f'{weekday_name}요일' in query):
                day += weekday_index - date.weekday()

        date += datetime.timedelta(days=day)
        await msg.channel.send(embed=await self.build_class_embed(date, grade, class_number))

    async def request_event_data(self, query: list, msg: discord.Message, **kwargs):
        grade = 3
        day = 0

        if '내일' in query:
            day += 1
        if '모레' in query:
            day += 2
        if '글피' in query:
            day += 3
        if '다음주' in query:
            day += 7
        if '다다음주' in query:
            day += 14
        for k in range(1, 365):
            if (f'{k}일후' in query) or (f'{k}일 후' in query) or (f'{k}일뒤' in query) or (f'{k}일 뒤' in query):
                day = k

        date = datetime.datetime.now().date()

        for weekday_index in self.weekday_in_korean:
            weekday_name = self.weekday_in_korean[weekday_index]
            if (weekday_name in query) or (f'{weekday_name}요일' in query):
                day += weekday_index - date.weekday()

        date += datetime.timedelta(days=day)
        await msg.channel.send(embed=await self.build_event_embed(date, grade))

    async def request_meal_data(self, query: list, msg: discord.Message, **kwargs):
        time = datetime.datetime.now().time()
        day = 0
        meal_code = None

        if '아침' in query or ('조식' in query):
            meal_code = 1
        elif '점심' in query or ('중식' in query):
            meal_code = 2
        elif ('저녁' in query) or ('석식' in query):
            meal_code = 3

        if '내일' in query:
            day += 1
        if '모레' in query:
            day += 2
        if '글피' in query:
            day += 3
        if '다음주' in query:
            day += 7
        if '다다음주' in query:
            day += 14
        for k in range(1, 365):
            if (f'{k}일후' in query) or (f'{k}일 후' in query) or (f'{k}일뒤' in query) or (f'{k}일 뒤' in query):
                day = k

        date = datetime.datetime.now().date()

        for weekday_index in self.weekday_in_korean:
            weekday_name = self.weekday_in_korean[weekday_index]
            if (weekday_name in query) or (f'{weekday_name}요일' in query):
                day += weekday_index - date.weekday()

        if day == 0:
            if meal_code is None:
                if time < datetime.time(hour=7, minute=45):
                    meal_code = 1
                elif time < datetime.time(hour=13, minute=20):
                    meal_code = 2
                elif time < datetime.time(hour=19, minute=10):
                    meal_code = 3
                else:
                    meal_code = 1
                    day = 1

        date += datetime.timedelta(days=day)
        if meal_code is None:
            for meal_code in [1, 2, 3]:
                await msg.channel.send(embed=await self.build_meal_embed(date, meal_code))
        else:
            await msg.channel.send(embed=await self.build_meal_embed(date, meal_code))

    async def build_class_embed(self, date: datetime.date, grade: int, class_number: int) -> discord.Embed:
        index = f'{date.month}/{date.day}/{date.year}'
        title = f'>>> {date.year}년 {date.month}월 {date.day}일({self.weekday_in_korean[date.weekday()]}) ' + \
                f'{grade}학년 {class_number}반 시간표\n'
        if index not in self.class_cached_data:
            try:
                await self.cache_class_data(date.year, date.month, date.day)
            except:
                desc = '>>> NEIS에 등록되지 않은 일자입니다.'
                return discord.Embed(title=title, description=desc)
        desc = ''
        for item in self.class_cached_data[index][f'{grade}-{class_number}'].items():
            desc += f'** {item[0]}교시  **{item[1]}\n'

        return discord.Embed(title=title, description=desc)

    async def build_event_embed(self, date: datetime.date, grade: int) -> discord.Embed:
        index = f'{date.month}/{date.day}/{date.year}'
        title = f'{date.year}년 {date.month}월 {date.day}일({self.weekday_in_korean[date.weekday()]}) 일정'
        if index not in self.event_cached_data:
            try:
                await self.cache_event_data(date.year, date.month, date.day)
            except:
                desc = '>>> NEIS에 등록되지 않은 일자입니다.'
                return discord.Embed(title=title, description=desc)

        events = [item for item in self.event_cached_data[index] if grade in item['target']]
        if len(events) == 0:
            desc = '>>> 평일입니다.'
        else:
            desc = ''
            for event in events:
                text = event['name']
                if text != '토요휴업일':
                    if event['type'] != '해당없음':
                        text += f"({event['type']})"
                text += '{text}입니다.'
                if len(desc) > 0:
                    desc += '\n'
                desc += text
        return discord.Embed(title=title, description=desc)

    async def build_meal_embed(self, date: datetime.date, meal_code: int) -> discord.Embed:
        index = f'{date.month}/{date.day}/{date.year}'

        title = f'{date.year}년 {date.month}월 {date.day}일({self.weekday_in_korean[date.weekday()]}) {self.meal_names[meal_code]}식사'
        if index not in self.meal_cached_data:
            try:
                await self.cache_meal_data(date.year, date.month, date.day)
            except:
                desc = '>>> NEIS에 등록되지 않은 일자입니다.'
                return discord.Embed(title=title, description=desc)

        if meal_code not in self.meal_cached_data[index]:
            desc = '>>> NEIS에 등록되지 않은 식사입니다.'
        else:
            desc = self.meal_cached_data[index][meal_code].replace('<br/>', '\n')
        return discord.Embed(title=title, description=desc)

    async def heartbeat(self):
        try:
            now_datetime = datetime.datetime.now() + self.bias_for_school_clock
            now_date = now_datetime
            now_time = now_datetime.time()
            # date = date_time.date()

            if self.last_run_date != datetime.datetime.now().date():
                self.last_run_date = datetime.datetime.now().date()
                self.last_run_time = now_time

            if self.last_run_time < datetime.time(hour=7, minute=0) <= now_time:
                roles_id = {1: config.discord_info["1st class role id"], 2: config.discord_info["2nd class role id"],
                            3: config.discord_info["3rd class role id"]}
                channels = {1: self.first_channel, 2: self.second_channel, 3: self.third_channel}
                for class_number in config.learn_class_info:
                    embed = await self.build_class_embed(now_date, 3, class_number)
                    embed.description += f'\n<@&{roles_id[class_number]}>'
                    await channels[class_number].send(embed=embed)
                await self.alarm_channel.send(embed=await self.build_event_embed(now_date, 3))
                await self.alarm_channel.send(embed=await self.build_meal_embed(now_date, 1))

            for the_class in config.schedule_info:
                if self.last_run_time < the_class['begin'] <= now_time:
                    desc = ''
                    index = f'{now_date.month}/{now_date.day}/{now_date.year}'
                    if index not in self.class_cached_data:
                        try:
                            await self.cache_class_data(now_date.year, now_date.month, now_date.day)
                        except:
                            desc = 'NEIS에 등록되지 않은 일자입니다.'
                    if index in self.class_cached_data:
                        the_day_data = self.class_cached_data[index]
                        for class_number in config.learn_class_info:
                            if the_class['index'] not in the_day_data[f'3-{class_number}']:
                                desc += f'{class_number}반 [해당없음]\n'
                            else:
                                desc += f'{class_number}반 ' + the_day_data[f'3-{class_number}'][
                                    the_class['index']] + '\n'
                    desc += '\n@everyone'
                    desc = desc.replace('\n\n', '\n')
                    await self.alarm_channel.send(
                        embed=discord.Embed(
                            title=f'{the_class["index"]}교시 시작',
                            description=desc))
                elif self.last_run_time < the_class['end'] <= now_time:
                    await self.alarm_channel.send(embed=discord.Embed(title=f'{the_class["index"]}교시 끝\n@everyone'))
                    if the_class["index"] == 4:
                        await self.alarm_channel.send(embed=await self.build_meal_embed(now_date, 2))
                    if the_class["index"] == 9:
                        await self.alarm_channel.send(embed=await self.build_meal_embed(now_date, 3))
            self.last_run_time = now_time
        except Exception as e:
            print(traceback.format_exc(), e)


school_manager = SchoolManager()


@static.DiscordModule.assign_onready(school_manager)
async def on_ready(discord_bot: static.DiscordBot, self: SchoolManager):
    self.alarm_channel = discord_bot.client.get_channel(config.discord_info['alarm channel id'])
    self.first_channel = discord_bot.client.get_channel(config.discord_info['1st class channel id'])
    self.second_channel = discord_bot.client.get_channel(config.discord_info['2nd class channel id'])
    self.third_channel = discord_bot.client.get_channel(config.discord_info['3rd class channel id'])
    self.allowed_channels = [self.first_channel, self.second_channel, self.third_channel]

    self.scheduler_loop.start()

    static.CommandBinding.assign_command('시간표', self.allowed_channels)(school_manager.request_class_data)
    static.CommandBinding.assign_command('일정', self.allowed_channels)(school_manager.request_event_data)
    static.CommandBinding.assign_command('밥', self.allowed_channels)(school_manager.request_meal_data)
    static.CommandBinding.assign_command('급식', self.allowed_channels)(school_manager.request_meal_data)
