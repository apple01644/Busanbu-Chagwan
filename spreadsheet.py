import datetime
import io


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


def run_command(content, roles=[]):
    times = ['08:40~09:30', '09:40~10:30', '10:40~11:30', '11:40~12:30', '13:20~14:10', '14:20~15:10', '15:20~16:10', ]
    if content == 'ㄱ도움':
        return {'status': 400, 'body': 'ㄱ시간표 사용 예시\nㄱ시간표 1반 내일\n'}
        # 'ㄱ시간표 1반 3주차\n'\
        
    class_number = None

    for role in roles:
        if role == '3학년 1반':
            class_number = '1'
        elif role == '3학년 2반':
            class_number = '2'
        elif role == '3학년 3반':
            class_number = '3'

    if content.find('1반') != -1:
        class_number = '1'
    if content.find('2반') != -1:
        class_number = '2'
    if content.find('3반') != -1:
        class_number = '3'

    if class_number is None:
        return {'status': 400, 'body': '반이 유효하지 않습니다.'}

    day = 0
    if content.find('내일') != -1:
        day = 1
    if content.find('모레') != -1:
        day = 2

    date = datetime.datetime.now().date()
    date += datetime.timedelta(days=day)
    week = get_week(date)
    weekday = date.weekday()
    template = False
    if week is None:
        if weekday in [5, 6]:
            return {'status': 400, 'body': '계획이 없는 일자 입니다.'}
        else:
            week = 3
            template = True

    data = read_spreadsheet(f'data/spreadsheets/{class_number}반-{week}주차.txt')[weekday]
    text = ''

    result = {'헤더': {}, 'status': 200}
    result['헤더']['date'] = date
    result['헤더']['class_number'] = class_number
    result['헤더']['is_template'] = template

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


def preprocess_command_data(data):
    teachers_fullname = ['권오석', '이석우', '조수연', '변강순', '우효림', '장창수', '박종대', '김완태', '김경호', '박정열', '배명호', '김한기', '김소현',
                         '박성', '하태효']

    for k in range(7):
        class_data = data[f'{k + 1} 교시']
        teacher_list = ''
        for i, teacher in enumerate(class_data['teachers']):
            if i > 0:
                teacher_list += ', '

            name = teacher
            for fullname in teachers_fullname:
                if fullname[:2] == teacher:
                    name = fullname
                    break
            teacher_list += name
        class_data['teacher_list'] = teacher_list
        data[f'{k + 1} 교시'] = class_data
    return data


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
        "shorten name": '알림방',
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
        "shorten name": '알림방',
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
        "shorten name": '알림방',
        "link": "https://classroom.google.com/u/1/c/NjY1MzMzNTQxNTRa"
    }
}

if __name__ == '__main__':
    for __role__ in ['3학년 1반', '3학년 2반', '3학년 3반']:
        print(run_command('ㄱ시간표', roles=[__role__]))