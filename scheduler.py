import datetime
import traceback
import discord
from discord.ext import tasks

import spreadsheet

global last_run_date, last_run_time
last_run_date = datetime.datetime.now().date()
last_run_time = datetime.datetime.now().time()
alarm_channel = None

classes = [
    {'index': 1, 'begin': datetime.time(hour=8, minute=40), 'end': datetime.time(hour=9, minute=30)},
    {'index': 2, 'begin': datetime.time(hour=9, minute=40), 'end': datetime.time(hour=10, minute=30)},
    {'index': 3, 'begin': datetime.time(hour=10, minute=40), 'end': datetime.time(hour=11, minute=30)},
    {'index': 4, 'begin': datetime.time(hour=11, minute=40), 'end': datetime.time(hour=12, minute=30)},
    {'index': 5, 'begin': datetime.time(hour=13, minute=20), 'end': datetime.time(hour=14, minute=10)},
    {'index': 6, 'begin': datetime.time(hour=14, minute=20), 'end': datetime.time(hour=15, minute=10)},
    {'index': 7, 'begin': datetime.time(hour=15, minute=20), 'end': datetime.time(hour=16, minute=10)},
]


@tasks.loop(seconds=1.0)
async def class_loop():
    global last_run_date, last_run_time
    try:
        now = datetime.datetime.now().time()
        date = datetime.datetime.now().date()
        title = None
        desc = None

        if last_run_date != datetime.datetime.now().date():
            last_run_date = datetime.datetime.now().date()
            last_run_time = now

        if last_run_time < datetime.time(hour=8, minute=20) <= now:
            last_run_time = now
            title = '%02d월 %02d일 알람방' % (last_run_date.month, last_run_date.day)
            desc = '바로가기: https://classroom.google.com/u/1/a/not-turned-in/all\n'
            for k in range(3):
                desc += f'{k + 1}반 알림방: ' + spreadsheet.bookmarks[f'{k + 1}']['알림방']["link"] + '\n'
        else:
            for the_class in classes:
                if last_run_time < the_class['begin'] <= now:
                    title = f'{the_class["index"]}교시 시작'
                    text = '바로가기: https://classroom.google.com/u/1/a/not-turned-in/all\n\n'
                    last_run_time = now
                    for k in range(3):
                        raw_data = spreadsheet.run_command(f'ㄱ시간표 {k + 1}반')
                        class_data = spreadsheet.preprocess_command_data(raw_data)[f'{the_class["index"]} 교시']

                        text += f'> {k + 1}반 {class_data["class_name"]}\n'
                        if class_data["teacher_list"]:
                            text += f'> {class_data["teacher_list"]}\n'
                        if not raw_data['헤더']['is_template']:
                            if class_data["objective"]:
                                text += f'> {class_data["objective"]}\n'
                        if class_data["class_data"]:
                            if class_data["class_data"]["link"]:
                                text += f'> {class_data["class_data"]["link"]}\n'
                        text += '\n'
                    desc = text
                    break
                if last_run_time < the_class['end'] <= now:
                    title = f'{the_class["index"]}교시 끝'
                    desc = None
                    last_run_time = now
                    break

        if title:
            if date.weekday() in [5, 6]:
                pass
            else:
                if desc in None:
                  desc = ''
                desc += '\n@everyone'
                await alarm_channel.send(embed=discord.Embed(title=title, description=desc))
    except Exception as e:
        print(traceback.format_exc(), e)


if __name__ == '__main__':
    client = discord.Client()


    @client.event
    async def on_ready():
        print('start')
        class_loop.start()


    discord_token = open('discord_bot_token', 'r').read()
    client.run(discord_token)
