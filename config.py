import datetime

schedule_info = [
    {'index': 1,
     'begin': datetime.time(hour=8, minute=40),
     'end': datetime.time(hour=9, minute=30),
     'duration': '08:40~09:30'},
    {'index': 2,
     'begin': datetime.time(hour=9, minute=40),
     'end': datetime.time(hour=10, minute=30),
     'duration': '09:40~10:30'},
    {'index': 3,
     'begin': datetime.time(hour=10, minute=40),
     'end': datetime.time(hour=11, minute=30),
     'duration': '10:40~11:30'},
    {'index': 4,
     'begin': datetime.time(hour=11, minute=40),
     'end': datetime.time(hour=12, minute=30),
     'duration': '11:40~12:30'},
    {'index': 5,
     'begin': datetime.time(hour=13, minute=20),
     'end': datetime.time(hour=14, minute=10),
     'duration': '13:20~14:10'},
    {'index': 6,
     'begin': datetime.time(hour=14, minute=20),
     'end': datetime.time(hour=15, minute=10),
     'duration': '14:20~15:10'},
    {'index': 7,
     'begin': datetime.time(hour=15, minute=20),
     'end': datetime.time(hour=16, minute=10),
     'duration': '15:20~16:10'},
    {'index': 8,
     'begin': datetime.time(hour=16, minute=30),
     'end': datetime.time(hour=17, minute=20),
     'duration': '19:10~20:00'},
    {'index': 9,
     'begin': datetime.time(hour=17, minute=30),
     'end': datetime.time(hour=18, minute=20),
     'duration': '20:10~21:00'},
    {'index': 10,
     'begin': datetime.time(hour=19, minute=10),
     'end': datetime.time(hour=20, minute=00),
     'duration': '19:10~20:00'},
    {'index': 11,
     'begin': datetime.time(hour=20, minute=10),
     'end': datetime.time(hour=21, minute=00),
     'duration': '20:10~21:00'},
]

learn_class_info = {
    1: {
        "bookmark": {
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
    },
    2: {
        "bookmark": {
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
    },
    3: {
        "bookmark": {
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
    },
}

teachers_fullname = [
    '권오석', '이석우', '조수연', '변강순', '우효림', '장창수', '박종대', '김완태', '김경호', '박정열', '배명호', '김한기', '김소현',
    '박성', '하태효'
]

discord_info = {
    'alarm channel id': 699239553789067285,
    '1st class channel id': 705953156294639746,
    '2nd class channel id': 705953050040205412,
    '3rd class channel id': 705953120341065818,
    'free channel id': 696585229347061843,
    'black cow guild id': 696585228906528881,
    '1st class role id': 696586929873092639,
    '2nd class role id': 696586953415589940,
    '3rd class role id': 696586970910031923,
    'admin user id': 348066198983933954,
}
