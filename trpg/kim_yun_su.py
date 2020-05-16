import random

import discord

from . import manager, Event, Person


@manager.assign_event
def event_start(event: Event):
    event.description = '낮선 기숙사에 짐을 풀었습니다. 기숙사를 도착해보니 처음보는 얼굴이 있습니다.\n그의 이름은 무엇인가요?'
    event.priority = 255

    @event.assign_condition
    def condition(person: Person):
        if 'start' not in person.traits:
            return False
        return 'start_dorm' not in person.traits

    @event.assign_option('이동우')
    async def option_sleep(msg: discord.Message, person: Person):
        person.traits.append('start_dorm')
        person.traits.append('room_with_lee')
        await msg.channel.send('>>> 이동우와 같은 방이 되었습니다.\n')

    @event.assign_option('윤재상')
    async def option_sleep(msg: discord.Message, person: Person):
        person.traits.append('start_dorm')
        person.traits.append('room_with_yun')
        await msg.channel.send('>>> 윤재상과 같은 방이 되었습니다.\n')

    @event.assign_option('문재인')
    async def option_sleep(msg: discord.Message, person: Person):
        person.traits.append('start_dorm')
        person.traits.append('room_with_moon')
        await msg.channel.send('>>> 문재인과 같은 방이 되었습니다.\n')


@manager.assign_event
def event_start(event: Event):
    event.description = ('고대하던 입학식날이 되었습니다. 교장선생님이 연설을 하십니다.' +
                         '\n그러나 너무 지루해서 눈이 감깁니다. 어떡게 할까요?')
    event.priority = 255

    @event.assign_condition
    def condition(person: Person):
        return 'start' not in person.traits

    @event.assign_option('잔다')
    async def option_sleep(msg: discord.Message, person: Person):
        person.traits.append('start')
        await msg.channel.send('>>> 자고 일어나니 입학식이 끝났습니다.\n++건강')
        person.health += 5

    @event.assign_option('개소리 집어쳐!')
    async def option_shut_up(msg: discord.Message, person: Person):
        person.traits.append('start')
        await msg.channel.send('>>> 교장선생님은 당신의 패기를 보고 물러섰습니다.\n++정치, --양심')
        person.goodness -= 10
        person.politic += 10

    @event.assign_option('그래도 듣는다')
    async def option_listen(msg: discord.Message, person: Person):
        person.traits.append('start')
        await msg.channel.send('>>> 연설을 듣고 있다보니 머리가 멍해지는 느낌이 듭니다.\n--IQ, ++양심')
        person.iq -= 10
        person.goodness += 10


@manager.assign_event
def event_start(event: Event):
    event.description = '학급 반장 선거 입후보가 시작되었습니다!'
    event.priority = 255

    @event.assign_condition
    def condition(person: Person):
        if 'start_dorm' not in person.traits:
            return False
        return person.grade == 1 and person.month == 3 and person.week == 3

    @event.assign_option('반장 선거에 입후보한다')
    async def option_sleep(msg: discord.Message, person: Person):
        if random.randint(0, 30) + person.politic > 15:
            await msg.channel.send('>>> 반장선거에세 당선 되었습니다.\n++정치')
            person.traits.append('1st class president')
            person.politic += 6
        else:
            await msg.channel.send('>>> 반장선거에서 낙선 되었습니다.\n+정치')
            person.politic += 3

    @event.assign_option('입후보하지 않는다')
    async def option_listen(msg: discord.Message, person: Person):
        pass


@manager.assign_event
def event_start(event: Event):
    event.description = '학생부회장 선거 입후보가 시작되었습니다!'
    event.priority = 255

    @event.assign_condition
    def condition(person: Person):
        if 'start_dorm' not in person.traits:
            return False
        if not (person.month == 4 and person.week == 1):
            return False
        if person.grade == 1:
            return '1st class president' not in person.traits
        elif person.grade == 2:
            return '2nd class president' not in person.traits
        return False

    @event.assign_option('학생 부회장 선거에 입후보한다')
    async def option_sleep(msg: discord.Message, person: Person):
        if random.randint(0, 30) + person.politic > 15:
            await msg.channel.send('>>> 부회장선거에세 당선 되었습니다.\n+++정치')
            if person.grade == 1:
                person.traits.append('1st secondary president')
            elif person.grade == 2:
                person.traits.append('2nd secondary president')
            person.politic += 36
        else:
            await msg.channel.send('>>> 부회장선거에서 낙선 되었습니다.\n++정치')
            person.politic += 12

    @event.assign_option('입후보하지 않는다')
    async def option_listen(msg: discord.Message, person: Person):
        pass


@manager.assign_event
def event_start(event: Event):
    event.description = '다음주에 영어듣기 평가가 있습니다. 어떡할까요?'
    event.priority = 255

    @event.assign_condition
    def condition(person: Person):
        if 'start_dorm' not in person.traits:
            return False
        if not ((person.month == 4 or person.month == 9) and person.week == 2):
            return False
        return person.grade <= 2

    @event.assign_option('많이 공부한다')
    async def option_listen(msg: discord.Message, person: Person):
        await msg.channel.send('>>> 머리가 아파오지만 준비는 충분히 한것 같습니다.\n++영어 -건강')
        person.english += 12
        person.health += 4

    @event.assign_option('조금 공부한다')
    async def option_listen(msg: discord.Message, person: Person):
        await msg.channel.send('>>> 이정도 공부면 충분한것 같습니다.\n+영어 -건강')
        person.english += 6
        person.health += 2

    @event.assign_option('안 한다')
    async def option_listen(msg: discord.Message, person: Person):
        pass


@manager.assign_event
def event_start(event: Event):
    event.description = '영어듣기 평가를 쳤습니다!'
    event.priority = 255

    @event.assign_condition
    def condition(person: Person):
        if 'start_dorm' not in person.traits:
            return False
        if not ((person.month == 4 or person.month == 9) and person.week == 3):
            return False
        return person.grade <= 2

    @event.assign_option('점수는?')
    async def option_listen(msg: discord.Message, person: Person):
        score = person.english + random.randint(-20, 20)
        if score < 0:
            score = 0
        if score > 100:
            score = 100
        score = round(score / 4) * 4

        await msg.channel.send(f'>>> 영어듣기 평가에서 {score}점을 얻었습니다.')


@manager.assign_event
def event_start(event: Event):
    event.description = '소프트웨어 축제가 시작되었습니다. 정치인 시뮬레이터를 만들자는 제의가 왔습니다.'
    event.priority = 255

    @event.assign_condition
    def condition(person: Person):
        if 'start_dorm' not in person.traits:
            return False
        return person.grade == 1 and person.month == 6 and person.week == 1

    @event.assign_option('제의를 받아들인다')
    async def option_sleep(msg: discord.Message, person: Person):
        await msg.channel.send('>>> 정치인 시뮬레이터 개발에 참가했습니다.\n--건강 ++코딩 +정치')
        person.coding += 6
        person.health -= 7
        person.politic += 3

    @event.assign_option('받아들이지 않는다')
    async def option_listen(msg: discord.Message, person: Person):
        pass


@manager.assign_event
def event_start(event: Event):
    event.description = '해양수련회를 갈 준비를 합니다.'
    event.priority = 255

    @event.assign_condition
    def condition(person: Person):
        if 'start_dorm' not in person.traits:
            return False
        if not (person.month == 6 and person.week == 3):
            return False
        return person.grade == 1

    @event.assign_option('갑시다')
    async def option_listen(msg: discord.Message, person: Person):
        await msg.channel.send(f'>>> 수련회를 갔다오면서 몸이 건강해진것 같습니다.\n++건강')
        person.health += 7


@manager.assign_event
def event_start(event: Event):
    event.description = '야구 관람을 갈 준비를 합니다.'
    event.priority = 255

    @event.assign_condition
    def condition(person: Person):
        if 'start_dorm' not in person.traits:
            return False
        if not (person.month == 9 and person.week == 2):
            return False
        return person.grade <= 2

    @event.assign_option('갑시다')
    async def option_listen(msg: discord.Message, person: Person):
        await msg.channel.send(f'>>> 야구체험을 갔다왔습니다.\n+건강 -돈')
        person.health += 3
        person.month -= 2


@manager.assign_event
def event_start(event: Event):
    event.description = '졸업을 했습니다. 졸업을 한 윤수는 어떻게 되었을가요?'
    event.priority = 255

    @event.assign_condition
    def condition(person: Person):
        if 'start_dorm' not in person.traits:
            return False
        return person.grade == 2 and person.month == 2 and person.week == 4

    @event.assign_option('그러게요')
    async def option_listen(msg: discord.Message, person: Person):
        person.traits.append('game over')
        if person.iq > 160:
            await msg.channel.send(f'>>> 김윤수는 IQ {person.iq}로 멘사에 들어갔습니다.')
        elif person.iq > 150 and person.library > 70:
            await msg.channel.send(f'>>> 김윤수는 {person.iq}로 서울대 국문학과에 들어갔습니다.')
        elif person.iq > 150 and person.politic > 70:
            await msg.channel.send(f'>>> 김윤수는 {person.iq}로 서울대 정치외교과에 들어갔습니다.')
        elif person.iq > 150 and person.economy > 70:
            await msg.channel.send(f'>>> 김윤수는 {person.iq}로 서울대 경제학과에 들어갔습니다.')
        elif person.iq > 150 and person.english > 70:
            await msg.channel.send(f'>>> 김윤수는 {person.iq}로 서울대 영어영문학과에 들어갔습니다.')
        elif person.iq > 150 and person.coding > 70:
            await msg.channel.send(f'>>> 김윤수는 {person.iq}로 서울대 컴퓨터공학과에 들어갔습니다.')
        elif person.coding > 70 and person.english > 70 and person.iq > 130:
            await msg.channel.send(f'>>> 김윤수는 삼성에 입사하였습니다.')
        elif person.coding > 70 and person.english > 70:
            await msg.channel.send(f'>>> 김윤수는 해외취업을 하였습니다.')
        elif person.coding > 70 and person.library > 70:
            await msg.channel.send(f'>>> 김윤수는 창업을 하여 CEO가 되었습니다.')
        elif person.lol > 70:
            await msg.channel.send(f'>>> 김윤수는 리그오브레전드 유튜버가 되었습니다.')
        elif person.coding > 50:
            await msg.channel.send(f'>>> 김윤수는 중견기업에 취업했습니다.')
        elif person.coding > 30:
            await msg.channel.send(f'>>> 김윤수는 SI기업에 취업했습니다.')
        elif person.iq > 100 and person.library > 70:
            await msg.channel.send(f'>>> 김윤수는 지잡대에 들어갔습니다.')
        elif person.iq > 100 and person.politic > 70:
            await msg.channel.send(f'>>> 김윤수는 정치인이 되었습니다.')
        elif person.iq > 100 and person.economy > 70:
            await msg.channel.send(f'>>> 김윤수는 경제학을 공부하면서 투자를 하다가 한강물에 들어갔습니다.')
        elif person.iq > 100 and person.english > 70:
            await msg.channel.send(f'>>> 김윤수는 {person.iq}로 영어학원 강사가 되었습니다.')
        else:
            await msg.channel.send(f'>>> 김윤수는 무직고졸백수가 되었습니다.')


'''
SI엔딩
중견기업취업엔딩
무직고졸백수엔딩
'''
