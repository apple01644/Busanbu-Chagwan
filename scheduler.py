import datetime
import traceback

import discord
from discord.ext import tasks

import config
import static
from spreadsheet import spreadsheet


class Scheduler:
    last_run_date = datetime.datetime.now().date()
    last_run_time = datetime.datetime.now().time()
    alarm_channel = None
    first_channel = None
    second_channel = None
    third_channel = None
    bias = datetime.timedelta(seconds=-60)

    @tasks.loop(seconds=1.0)
    async def scheduler_loop(self):
        try:
            await self.heartbeat()
        except Exception as e:
            print(traceback.format_exc(), e)

    async def heartbeat(self):
        date_time = datetime.datetime.now() + self.bias
        now = date_time.time()
        date = date_time.date()

        if self.last_run_date != datetime.datetime.now().date():
            self.last_run_date = datetime.datetime.now().date()
            self.last_run_time = now

        if date.weekday() in [5, 6]:
            return

        if self.last_run_time < datetime.time(hour=8, minute=20) <= now:
            title = '%02d월 %02d일 알람방' % (self.last_run_date.month, self.last_run_date.day)
            desc = '바로가기: https://classroom.google.com/u/1/a/not-turned-in/all\n'
            for k in [1, 2, 3]:
                desc += f'{k}반 알림방: ' + config.learn_class_info[k]['bookmark']['알림방']["link"] + '\n'
            desc += '\n다음 시간'
            for k in [1, 2, 3]:
                raw_data = spreadsheet.run_command(f'ㄱ시간표 {k}반')
                class_data = raw_data['1 교시']
                desc += f'> {k}반 {class_data["class_name"]}\n'
                if class_data["teacher_desc"]:
                    desc += f'> {class_data["teacher_desc"]}\n'
                if not raw_data['헤더']['is_template']:
                    if class_data["objective"]:
                        desc += f'> {class_data["objective"]}\n'
                if class_data["class_data"]:
                    if class_data["class_data"]["link"]:
                        desc += f'> {class_data["class_data"]["link"]}\n'
            desc += '\n**학생건강상태 조사**에 응답해주세요.'
            desc += '\n@everyone'
            await self.alarm_channel.send(embed=discord.Embed(title=title, description=desc))

            result = spreadsheet.run_command('ㄱ시간표', ['3학년 1반'])
            if result['status'] == 200:
                data = spreadsheet.command_data_to_description(result)
                await self.first_channel.send(embed=discord.Embed(
                    title=data['title'],
                    description=data['description'] + f'\n<@&{static.discord_info["1st class role id"]}>'))

            result = spreadsheet.run_command('ㄱ시간표', ['3학년 2반'])
            if result['status'] == 200:
                data = spreadsheet.command_data_to_description(result)
                await self.second_channel.send(embed=discord.Embed(
                    title=data['title'],
                    description=data['description'] + f'\n<@&{static.discord_info["2nd class role id"]}>'))

            result = spreadsheet.run_command('ㄱ시간표', ['3학년 3반'])
            if result['status'] == 200:
                data = spreadsheet.command_data_to_description(result)
                await self.third_channel.send(embed=discord.Embed(
                    title=data['title'],
                    description=data['description'] + f'\n<@&{static.discord_info["3rd class role id"]}>'))

        for the_class in config.schedule_info:
            if self.last_run_time < the_class['begin'] <= now:
                desc = '바로가기: https://classroom.google.com/u/1/a/not-turned-in/all\n\n'
                for k in range(3):
                    raw_data = spreadsheet.run_command(f'ㄱ시간표 {k + 1}반')
                    class_data = raw_data[f'{the_class["index"]} 교시']

                    desc += f'> {k + 1}반 {class_data["class_name"]}\n'
                    if class_data["teacher_desc"]:
                        desc += f'> {class_data["teacher_desc"]}\n'
                    if not raw_data['헤더']['is_template']:
                        if class_data["objective"]:
                            desc += f'> {class_data["objective"]}\n'
                    if class_data["class_data"]:
                        if class_data["class_data"]["link"]:
                            desc += f'> {class_data["class_data"]["link"]}\n'
                    desc += '\n'
                await self.alarm_channel.send(
                    embed=discord.Embed(
                        title=f'{the_class["index"]}교시 시작',
                        description=desc))
            elif self.last_run_time < the_class['end'] <= now:
                await self.alarm_channel.send(embed=discord.Embed(title=f'{the_class["index"]}교시 끝\n@everyone'))
        self.last_run_time = now


scheduler = Scheduler()


@static.DiscordModule.assign_onready(scheduler)
async def on_ready(discord_bot: static.DiscordBot, self: Scheduler):
    self.alarm_channel = discord_bot.client.get_channel(config.discord_info['alarm channel id'])
    self.first_channel = discord_bot.client.get_channel(config.discord_info['1st class channel id'])
    self.second_channel = discord_bot.client.get_channel(config.discord_info['2nd class channel id'])
    self.third_channel = discord_bot.client.get_channel(config.discord_info['3rd class channel id'])

    self.scheduler_loop.start()
