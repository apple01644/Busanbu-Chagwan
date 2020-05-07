import datetime
import io

import discord

import config
import static


class SpreadSheet:
    tags = ['과목', '담당교사', '차시', '주제', '학습방법', 'ZOOM ID', '클래스룸']

    @staticmethod
    def get_week(date: datetime.date):
        if datetime.date(2020, 4, 6) <= date <= datetime.date(2020, 4, 10):
            return 1
        if datetime.date(2020, 4, 13) <= date <= datetime.date(2020, 4, 17):
            return 2
        if datetime.date(2020, 4, 20) <= date <= datetime.date(2020, 4, 24):
            return 3
        if datetime.date(2020, 4, 27) <= date <= datetime.date(2020, 5, 1):
            return 4
        if datetime.date(2020, 5, 4) <= date <= datetime.date(2020, 5, 8):
            return 5
        return None

    @classmethod
    def read_spreadsheet(cls, path):
        with io.open(path, 'r', encoding='utf-8') as file:
            buf = ''
            rows = []
            table = []
            string = False
            for char in file.read().replace('\r\n\r\n', '\r\n').replace('\n\n', '\n'):
                if string:
                    if char == '"':
                        string = False
                    else:
                        buf += char
                else:
                    if char == '\n':
                        rows.append(buf)
                        buf = ''
                        table.append(rows)
                        rows = []
                    elif char == '\t':
                        rows.append(buf)
                        buf = ''
                    elif char == '"':
                        string = True
                    else:
                        buf += char
            rows.append(buf)
            table.append(rows)
            data = [[] for x in range(5)]
            for i in range(7):
                j = 0
                for k in range(5):
                    pair = {}
                    for tag in cls.tags:
                        try:
                            pair[tag] = table[j][2 + i]
                            if pair[tag] == '-' or pair[tag] == '':
                                pair[tag] = None
                        except IndexError as e:
                            pair[tag] = None
                        j += 1
                    if pair['과목'] in ['──', '─▷']:
                        pair['과목'] = data[k][i - 1]['과목']
                        pair['담당교사'] = data[k][i - 1]['담당교사']
                    data[k].append(pair)
            return data

    @classmethod
    def run_command(cls, content, roles=[]):
        class_number = None

        for k in config.learn_class_info:
            for role in roles:
                if role == f'3학년 {k}반':
                    class_number = k

            if content.find(f'{k}반') != -1:
                class_number = k

        if class_number is None:
            return {'status': 400, 'body': '반이 유효하지 않습니다.'}

        day = 0
        if content.find('내일') != -1:
            day = 1
        if content.find('모레') != -1:
            day = 2

        date = datetime.datetime.now().date()
        date += datetime.timedelta(days=day)
        week = cls.get_week(date)
        weekday = date.weekday()
        is_template = False
        if week is None:
            if weekday in [5, 6]:
                return {'status': 400, 'body': '계획이 없는 일자 입니다.'}
            else:
                week = 5
                is_template = True

        data = cls.read_spreadsheet(f'data/spreadsheets/{class_number}반-{week}주차.txt')[weekday]

        result = {'헤더': {'date': date, 'class_number': class_number, 'is_template': is_template}, 'status': 200}

        k = -1
        for pair in data:
            k += 1
            class_name = pair["과목"]
            class_data = None
            teachers = []
            teacher_desc = ''
            objective = ''

            if pair["담당교사"]:
                for teacher_shorten_name in pair["담당교사"] \
                        .replace('\r', '') \
                        .replace('\n', ',') \
                        .replace('\t', '') \
                        .replace('\f', '') \
                        .replace('\v', '') \
                        .replace(' ', '') \
                        .split(','):
                    name = teacher_shorten_name
                    for fullname in config.teachers_fullname:
                        if fullname[:2] == teacher_shorten_name:
                            name = fullname
                            break
                    teachers.append(name)

                for i, teacher in enumerate(teachers):
                    if i > 0:
                        teacher_desc += ', '

                    teacher_desc += name

            if pair["학습방법"]:
                objective = pair['학습방법']

            for bookmark_key in config.learn_class_info[class_number]['bookmark']:
                bookmark = config.learn_class_info[class_number]['bookmark'][bookmark_key]
                if class_name == bookmark['shorten name']:
                    class_name = bookmark_key
                    class_data = bookmark
                    break

            result_key = f'{k + 1} 교시'
            result[result_key] = {'raw_data': pair,
                                  'class_name': class_name,
                                  'class_data': class_data,
                                  'time': config.schedule_info[k]['duration'],
                                  'teachers': teachers,
                                  'teacher_desc': teacher_desc,
                                  'objective': objective}

        return result

    @classmethod
    def command_data_to_description(cls, data):
        title = "%02d월 %02d일 %1s반 시간표" % (data['헤더']['date'].month, data['헤더']['date'].day, data['헤더']['class_number'])
        text = ''
        for k in range(7):
            class_data = data[f'{k + 1} 교시']
            class_datetime = datetime.datetime.combine(data['헤더']['date'], config.schedule_info[k]['end'])
            if datetime.datetime.now() < class_datetime:
                text += f'** {class_data["class_name"]} ({k + 1} 교시 {class_data["time"]}) **'
            else:
                text += f'~~ {class_data["class_name"]} ({k + 1} 교시 {class_data["time"]}) ~~'
            if class_data['class_data']:
                if class_data['class_data']['link']:
                    text += f" || {class_data['class_data']['link']} ||"

            text += '\n'

            if class_data['teacher_desc'] != '':
                text += f'> ** {class_data["teacher_desc"]} **\n'

                if not data['헤더']['is_template']:
                    if class_data['objective'] != '':
                        text += f"> ** {class_data['objective']} **\n"

                text += '\n'

        return {'title': title, 'description': text}


spreadsheet = SpreadSheet()


@static.DiscordModule.assign_onready(spreadsheet)
async def on_ready(discord_bot: static.DiscordBot, self: SpreadSheet):
    first_class_channel = discord_bot.client.get_channel(config.discord_info['1st class channel id'])
    second_class_channel = discord_bot.client.get_channel(config.discord_info['2nd class channel id'])
    third_class_channel = discord_bot.client.get_channel(config.discord_info['3rd class channel id'])

    @static.CommandBinding.assign_command(
        discord_bot, '시간표', [first_class_channel, second_class_channel, third_class_channel])
    async def get_timetable(bot: static.DiscordBot, query: list, msg: discord.Message):
        result = self.run_command(msg.content, [role.name for role in msg.author.roles])
        if result['status'] == 200:
            data = self.command_data_to_description(result)
            await msg.channel.send(embed=discord.Embed(title=data['title'], description=data['description']))
        elif result:
            await msg.channel.send(result['body'])
        else:
            await msg.channel.send('예외 발생')


if __name__ == '__main__':
    for __role__ in ['3학년 1반', '3학년 2반', '3학년 3반']:
        print(spreadsheet.run_command('ㄱ시간표', roles=[__role__]))
