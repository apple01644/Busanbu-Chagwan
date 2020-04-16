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


bookmarks = {}


def run_command(content):
    times = ['08:40~09:30', '09:40~10:30', '10:40~11:30', '11:40~12:30', '13:20~14:10', '14:20~15:10', '15:20~16:10', ]
    if content == 'ㄱ도움':
        return {'status': 400, 'body': 'ㄱ시간표 사용 예시\nㄱ시간표 1반 내일\n'}
        # 'ㄱ시간표 1반 3주차\n'\
    try:
        group = re.findall(regex, content, re.MULTILINE)[0]
    except:
        if content.find('ㄱ시간표') != -1:
            return {'status': 400, 'body': 'ㄱ시간표 사용 예시\nㄱ시간표 1반 내일\n'}
            # 'ㄱ시간표 1반 3주차\n'\

    if not (group[0] in ['1', '2', '3']):
        return {'status': 400, 'body': '반이 유효하지 않습니다.'}

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
            return {'status': 400, 'body': '계획이 없는 일자 입니다.'}

        class_number = group[0]
        data = read_spreadsheet(f'data/spreadsheets/{class_number}반-{week}주차.txt')[weekday]
        text = ''

        result = {'헤더': {}, 'status': 200}
        result['헤더']['date'] = date
        result['헤더']['class_number'] = class_number

        k = -1
        for pair in data:
            k += 1
            text += times[k] + ' :: '
            class_name = pair["과목"]
            class_data = None
            teachers = []
            objective = ''

            if pair["담당교사"]:
                teachers = pair["담당교사"] \
                    .replace('\r', '') \
                    .replace('\n', ',') \
                    .replace('\t', '') \
                    .replace('\f', '') \
                    .replace('\v', '') \
                    .replace(' ', '') \
                    .split(',')

            if pair["학습방법"]:
                objective = pair['학습방법']

            for bookmark_key in bookmarks[class_number]:
                bookmark = bookmarks[class_number][bookmark_key]
                if class_name == bookmark['shorten name']:
                    class_name = bookmark_key
                    class_data = bookmark
                    break

            result_key = f'{k + 1} 교시'
            result[result_key] = {'raw_data': pair, 'class_name': class_name, 'class_data': class_data,
                                  'time': times[k], 'teachers': teachers, 'objective': objective}

        return result


bookmarks['1'] = {
    "진로": {
        "shorten name": "진로",
        "link": "https://classroom.google.com/u/1/c/NjgxMTgyNTU3NDNa"
    },
    "프로젝트실습": {
        "shorten name": "프로",
        "link": "https://classroom.google.com/u/1/c/NjY0NTc1ODQ2NDla"
    },
    "모바일웹프로그래밍": {
        "shorten name": "모프",
        "link": "https://classroom.google.com/u/1/c/NjY0NDc4MDU2Mzha"
    },
    "웹프로그래밍": {
        "shorten name": "웹실",
        "link": "https://classroom.google.com/u/1/c/NjgxMDU5NDM4ODla"
    },
    "성공적인직업생활": {
        "shorten name": "성직",
        "link": "https://classroom.google.com/u/1/c/NjY0NTYyMDU0ODVa"
    },
    "알림방": {
        "shorten name": None,
        "link": "https://classroom.google.com/u/1/c/NjY1MzMzNTQxMTha"
    }
}

bookmarks['2'] = {
    "진로": {
        "shorten name": "진로",
        "link": "https://classroom.google.com/u/1/c/NjgxMTQzNjE4Njla"
    },
    "프로젝트실습": {
        "shorten name": "프로",
        "link": "https://classroom.google.com/u/1/c/NjY0NTc1ODQ2NjNa"
    },
    "모바일웹프로그래밍": {
        "shorten name": "모프",
        "link": "https://classroom.google.com/u/1/c/Njc3MzY3NDMzMjJa"
    },
    "웹프로그래밍": {
        "shorten name": "웹실",
        "link": "https://classroom.google.com/u/1/c/NjgxMDU5NDM5MTBa"
    },
    "성공적인직업생활": {
        "shorten name": "성직",
        "link": "https://classroom.google.com/u/1/c/NjY0NjI1Njg3NjNa"
    },
    "알림방": {
        "shorten name": None,
        "link": "https://classroom.google.com/u/1/c/NjY1MzMzNTQxNDRa"
    }
}

bookmarks['3'] = {
    "진로": {
        "shorten name": "진로",
        "link": "https://classroom.google.com/u/1/c/NjgxMTQzNjE4ODRa"
    },
    "프로젝트실습": {
        "shorten name": "프로",
        "link": "https://classroom.google.com/u/1/c/NjY0NTMxNDk0NzRa"
    },
    "모바일플랫폼": {
        "shorten name": "모플",
        "link": "https://classroom.google.com/u/1/c/NjY0NTMxNDk0NjBa"
    },
    "임베디드리눅스": {
        "shorten name": "임리",
        "link": "https://classroom.google.com/u/1/c/NjY0NDMxMzQ5MDFa"
    },
    "임베디드시스템": {
        "shorten name": "임시",
        "link": "https://classroom.google.com/u/1/c/Njg1MjI5MDE4MTZa"
    },
    "성공적인직업생활": {
        "shorten name": "성직",
        "link": "https://classroom.google.com/u/1/c/NjY0NjI1Njg3ODBa"
    },
    "알림방": {
        "shorten name": None,
        "link": "https://classroom.google.com/u/1/c/NjY1MzMzNTQxNTRa"
    }
}
