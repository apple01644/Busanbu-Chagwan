import datetime
import io
import re

regex = r"ㄱ\s*시간표\s*(?P<Class>\d)\s*반\s*((?P<Days>오늘|내일|모레))?"


def get_week(date: datetime.date):
    if datetime.date(2020, 4, 6) <= date <= datetime.date(2020, 4, 10):
        return 1
    if datetime.date(2020, 4, 13) <= date <= datetime.date(2020, 4, 17):
        return 2
    if datetime.date(2020, 4, 20) <= date <= datetime.date(2020, 4, 24):
        return 3
    return None


def read_spreadsheet(path):
    tags = ['과목', '담당교사', '차시', '주제', '학습방법', 'ZOOM ID', '클래스룸']
    with io.open(path, 'r', encoding='utf-8') as file:
        buf = ''
        rows = []
        table = []
        string = False
        for char in file.read():
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
                for tag in tags:
                    # print(table[j])
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

        # print(len(data))
        # print(len(data[0]))
        # print(data[0])
        return data


def run_command(content):
    times = ['08:40~09:30', '09:40~10:30', '10:40~11:30', '11:40~12:30', '13:20~14:10', '14:20~15:10', '15:20~16:10', ]
    if content == 'ㄱ도움':
        return 'ㄱ시간표 사용 예시\n' \
               'ㄱ시간표 1반 내일\n'
        # 'ㄱ시간표 1반 3주차\n'\
    try:
        group = re.findall(regex, content, re.MULTILINE)[0]
    except:
        if content.find('ㄱ시간표') != -1:
            return 'ㄱ시간표 사용 예시\n' \
                   'ㄱ시간표 1반 내일\n'
            # 'ㄱ시간표 1반 3주차\n'\

    if not (group[0] in ['1', '2', '3']):
        return '반이 유효하지 않습니다.'

    else:
        day = 0
        if group[2] == '내일':
            day = 1
        if group[2] == '모레':
            day = 2
        date = datetime.datetime.now().date()
        date += datetime.timedelta(days=day)
        week = get_week(date)
        weekday = date.weekday()
        if week is None:
            return '계획이 없는 일자 입니다.'

        data = read_spreadsheet(f'{group[0]}반-{week}주차.txt')[weekday]
        text = ''
        # print(data)
        i = -1
        for pair in data:
            i += 1
            text += times[i] + ' :: '
            text += pair["과목"]

            if pair["담당교사"]:
                teachers = pair["담당교사"].replace("\n", ", ")
                text += '%-12s' % f'({teachers})'

            if pair['학습방법']:
                text += ' --- ' + pair['학습방법'].replace("\n", "")
            text += '\n'

        return "```" + text + "```"
