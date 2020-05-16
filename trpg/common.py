import random

import discord

from . import manager, Event, Person


@manager.assign_event
def event_start(event: Event):
    event.description = 'C언어 시간이 되었습니다. 그러나 수업이 너무 어렵고 지루합니다. 어떡게 할까요?'
    event.priority = -1

    @event.assign_condition
    def condition(person: Person):
        if 'start_dorm' not in person.traits:
            return False
        return person.in_1st_period(1) and person.coding < 50

    @event.assign_option('잔다')
    async def option_sleep(msg: discord.Message, person: Person):
        await msg.channel.send('>>> 잠을 잤더니 훨씬 개운해졌습니다.\n-코딩 +건강')
        person.health += 5
        person.coding -= 5

    @event.assign_option('그래도 공부한다')
    async def option_sleep(msg: discord.Message, person: Person):
        await msg.channel.send('>>> 공부를 했더니 머리에 든게 많아진것 같습니다.\n+코딩')
        person.coding += 5


@manager.assign_event
def event_start(event: Event):
    event.description = '컴퓨터 구조 시간이 되었습니다. 그러나 수업이 너무 어렵고 지루합니다. 어떡게 할까요?'
    event.priority = -1

    @event.assign_condition
    def condition(person: Person):
        if 'start_dorm' not in person.traits:
            return False
        return person.in_1st_period(1) and person.coding < 50

    @event.assign_option('잔다')
    async def option_sleep(msg: discord.Message, person: Person):
        await msg.channel.send('>>> 잠을 잤더니 훨씬 개운해졌습니다.\n-코딩 +건강')
        person.health += 5
        person.coding -= 5

    @event.assign_option('그래도 공부한다')
    async def option_sleep(msg: discord.Message, person: Person):
        await msg.channel.send('>>> 공부를 했더니 머리에 든게 많아진것 같습니다.\n++코딩 -건강')
        person.health -= 5
        person.coding += 15


@manager.assign_event
def event_start(event: Event):
    event.description = '운영체제 시간이 되었습니다. 그러나 수업이 너무 어렵고 지루합니다. 어떡게 할까요?'
    event.priority = -1

    @event.assign_condition
    def condition(person: Person):
        if 'start_dorm' not in person.traits:
            return False
        return person.in_2nd_period(1) and person.coding < 70

    @event.assign_option('잔다')
    async def option_sleep(msg: discord.Message, person: Person):
        await msg.channel.send('>>> 잠을 잤더니 훨씬 개운해졌습니다.\n +건강')
        person.health += 3

    @event.assign_option('그래도 공부한다')
    async def option_sleep(msg: discord.Message, person: Person):
        if person.coding < 40 + random.randint(-10, 10):
            await msg.channel.send('>>> 선생님 말씀도 교과서의 글귀도, 그 어느것도 눈에 들어오지 않았습니다.\n--건강 -양심')
            person.health -= 9
            person.goodness -= 3
        else:
            await msg.channel.send('>>> 공부를 했더니 머리에 든게 많아진것 같습니다.\n++코딩 -건강')
            person.health -= 5
            person.coding += 7


@manager.assign_event
def event_start(event: Event):
    event.description = '자바 시간이 되었습니다. 그러나 수업이 너무 어렵고 지루합니다. 어떡게 할까요?'
    event.priority = -1

    @event.assign_condition
    def condition(person: Person):
        if 'start_dorm' not in person.traits:
            return False
        return person.in_2nd_period(1) and person.coding < 70

    @event.assign_option('잔다')
    async def option_sleep(msg: discord.Message, person: Person):
        await msg.channel.send('>>> 잠을 잤더니 훨씬 개운해졌습니다.\n +건강')
        person.health += 3

    @event.assign_option('딴짓한다')
    async def option_sleep(msg: discord.Message, person: Person):
        await msg.channel.send('>>> 딴짓을 했더니 훨씬 개운해졌습니다.\n +건강')
        person.health += 6

    @event.assign_option('그래도 공부한다')
    async def option_sleep(msg: discord.Message, person: Person):
        if person.coding < 40 + random.randint(-10, 10):
            await msg.channel.send('>>> ???!!! 이게 뭔소리야 ??? 이게 왜 안 돼.\n-건강 -코딩')
            person.health -= 3
            person.coding -= 5
        else:
            await msg.channel.send('>>> 공부를 했더니 머리에 든게 많아진것 같습니다.\n-코딩 -건강')
            person.health -= 5
            person.coding -= 3


@manager.assign_event
def event_start(event: Event):
    event.description = '네트워크 시간이 되었습니다. 그러나 수업이 너무 어렵고 지루합니다. 어떡게 할까요?'
    event.priority = -1

    @event.assign_condition
    def condition(person: Person):
        if 'start_dorm' not in person.traits:
            return False
        if 'sw_part' not in person.traits:
            return False
        return person.grade >= 2 and person.coding < 80

    @event.assign_option('잔다')
    async def option_sleep(msg: discord.Message, person: Person):
        await msg.channel.send('>>> 잠을 잤더니 훨씬 개운해졌습니다.\n +건강')
        person.health += 3

    @event.assign_option('그래도 공부한다')
    async def option_sleep(msg: discord.Message, person: Person):
        if person.coding < 50 + random.randint(-10, 10):
            await msg.channel.send('>>> 선생님 말씀도 교과서의 글귀도, 그 어느것도 눈에 들어오지 않았습니다.\n--건강 -양심')
            person.health -= 5
            person.goodness -= 2
        else:
            await msg.channel.send('>>> 공부를 했더니 머리에 든게 많아진것 같습니다.\n++코딩 -건강')
            person.health -= 4
            person.coding += 8


@manager.assign_event
def event_start(event: Event):
    event.description = '웹 프로그래밍 시간이 되었습니다. 그러나 수업이 너무 어렵고 지루합니다. 어떡게 할까요?'
    event.priority = -1

    @event.assign_condition
    def condition(person: Person):
        if 'start_dorm' not in person.traits:
            return False
        if 'sw_part' not in person.traits:
            return False
        return person.grade >= 2 and person.coding < 80

    @event.assign_option('잔다')
    async def option_sleep(msg: discord.Message, person: Person):
        await msg.channel.send('>>> 잠을 잤더니 훨씬 개운해졌습니다.\n +건강')
        person.health += 3

    @event.assign_option('그래도 공부한다')
    async def option_sleep(msg: discord.Message, person: Person):
        if person.coding < 50 + random.randint(-10, 10):
            await msg.channel.send('>>> 선생님 말씀도 교과서의 글귀도, 그 어느것도 눈에 들어오지 않았습니다.\n--건강 -양심')
            person.health -= 5
            person.goodness -= 2
        else:
            await msg.channel.send('>>> 공부를 했더니 머리에 든게 많아진것 같습니다.\n++코딩 -건강')
            person.health -= 4
            person.coding += 8


@manager.assign_event
def event_start(event: Event):
    event.description = 'RTOS 시간이 되었습니다. 그러나 수업이 너무 어렵고 지루합니다. 어떡게 할까요?'
    event.priority = -1

    @event.assign_condition
    def condition(person: Person):
        if 'start_dorm' not in person.traits:
            return False
        if 'embed_part' not in person.traits:
            return False
        return person.grade >= 2 and person.coding < 80

    @event.assign_option('잔다')
    async def option_sleep(msg: discord.Message, person: Person):
        await msg.channel.send('>>> 잠을 잤더니 훨씬 개운해졌습니다.\n +건강')
        person.health += 3

    @event.assign_option('딴 공부를 한다')
    async def option_sleep(msg: discord.Message, person: Person):
        await msg.channel.send('>>> 스스로 배우니 감회가 새롭습니다.\n +코딩 +건강')
        person.health += 3
        person.coding += 2

    @event.assign_option('그래도 공부한다')
    async def option_sleep(msg: discord.Message, person: Person):
        if person.coding < 80 + random.randint(-10, 10):
            await msg.channel.send('>>> 선생님 말씀도 교과서의 글귀도, 그 어느것도 눈에 들어오지 않았습니다.\n--건강 -양심')
            person.health -= 5
            person.goodness -= 2
        else:
            await msg.channel.send('>>> 공부를 했더니 머리에 든게 많아진것 같습니다.\n+++코딩 -건강')
            person.health -= 4
            person.coding += 12


@manager.assign_event
def event_start(event: Event):
    event.description = '하드웨어 플랫폼 시간이 되었습니다. 그러나 수업이 너무 어렵고 지루합니다. 어떡게 할까요?'
    event.priority = -1

    @event.assign_condition
    def condition(person: Person):
        if 'start_dorm' not in person.traits:
            return False
        if 'embed_part' not in person.traits:
            return False
        return person.grade >= 2 and person.coding < 80

    @event.assign_option('잔다')
    async def option_sleep(msg: discord.Message, person: Person):
        await msg.channel.send('>>> 잠을 잤더니 훨씬 개운해졌습니다.\n +건강')
        person.health += 3

    @event.assign_option('딴 공부를 한다')
    async def option_sleep(msg: discord.Message, person: Person):
        await msg.channel.send('>>> 스스로 배우니 감회가 새롭습니다.\n +코딩 +건강')
        person.health += 3
        person.coding += 2

    @event.assign_option('그래도 공부한다')
    async def option_sleep(msg: discord.Message, person: Person):
        if person.coding < 80 + random.randint(-10, 10):
            await msg.channel.send('>>> 선생님 말씀도 교과서의 글귀도, 그 어느것도 눈에 들어오지 않았습니다.\n--건강 -양심')
            person.health -= 5
            person.goodness -= 2
        else:
            await msg.channel.send('>>> 공부를 했더니 머리에 든게 많아진것 같습니다.\n+++코딩 -건강')
            person.health -= 4
            person.coding += 12


@manager.assign_event
def event_start(event: Event):
    event.description = '실무 프로그래밍 시간이 되었습니다. 그러나 수업이 너무 어렵고 지루합니다. 어떡게 할까요?'
    event.priority = -1

    @event.assign_condition
    def condition(person: Person):
        if 'start_dorm' not in person.traits:
            return False
        if 'embed_part' not in person.traits:
            return False
        return person.grade >= 2 and person.coding < 60

    @event.assign_option('잔다')
    async def option_sleep(msg: discord.Message, person: Person):
        await msg.channel.send('>>> 잠을 잤더니 훨씬 개운해졌습니다.\n +건강')
        person.health += 3
        if random.randint(0, 3) == 0:
            person.traits.append('punish_by_teacher')

    @event.assign_option('딴 공부를 한다')
    async def option_sleep(msg: discord.Message, person: Person):
        await msg.channel.send('>>> 스스로 배우니 감회가 새롭습니다.\n +코딩 +건강')
        person.health += 3
        person.coding += 2

    @event.assign_option('그래도 공부한다')
    async def option_sleep(msg: discord.Message, person: Person):

        if person.coding < 60 + random.randint(-10, 10):
            await msg.channel.send('>>> 선생님 말씀도 교과서의 글귀도, 그 어느것도 눈에 들어오지 않았습니다.\n-건강 -양심')
            person.health -= 3
            person.goodness -= 1
        else:
            await msg.channel.send('>>> 공부를 했더니 머리에 든게 많아진것 같습니다.\n++코딩 -건강')
            person.health -= 2
            person.coding += 8


@manager.assign_event
def event_start(event: Event):
    event.description = 'DB 시간이 되었습니다. 그러나 수업이 너무 어렵고 지루합니다. 어떡게 할까요?'
    event.priority = -1

    @event.assign_condition
    def condition(person: Person):
        if 'start_dorm' not in person.traits:
            return False
        return person.grade == 2 and person.coding < 8

    @event.assign_option('잔다')
    async def option_sleep(msg: discord.Message, person: Person):
        await msg.channel.send('>>> 잠을 잤더니 훨씬 개운해졌습니다.\n +건강')
        person.health += 3

    @event.assign_option('그래도 공부한다')
    async def option_sleep(msg: discord.Message, person: Person):
        if person.coding < 50 + random.randint(-10, 10):
            await msg.channel.send('>>> 선생님 말씀도 교과서의 글귀도, 그 어느것도 눈에 들어오지 않았습니다.\n--건강 -양심')
            person.health -= 5
            person.goodness -= 2
        else:
            await msg.channel.send('>>> 공부를 했더니 머리에 든게 많아진것 같습니다.\n++코딩 -건강')
            person.health -= 4
            person.coding += 8


@manager.assign_event
def event_start(event: Event):
    event.description = '아침운동 시간이 되었습니다. 택견을 해야하는데 너무 졸립니다.'
    event.priority = -1

    @event.assign_condition
    def condition(person: Person):
        if 'start_dorm' not in person.traits:
            return False
        return person.grade == 1 and person.coding < 70

    @event.assign_option('잔다')
    async def option_sleep(msg: discord.Message, person: Person):
        await msg.channel.send('>>> 잠을 잤더니 훨씬 개운해졌습니다.\n +건강')
        person.health += 3
        if random.randint(0, 3) == 0:
            person.traits.append('punish_by_teacher')

    @event.assign_option('택견을 열심히 한다')
    async def option_sleep(msg: discord.Message, person: Person):
        await msg.channel.send('>>> 택견을 했더니 몸이 단련됫건 같습니다.\n +건강')
        person.health += 9

    @event.assign_option('친구랑 논다')
    async def option_sleep(msg: discord.Message, person: Person):
        await msg.channel.send('>>> 친구랑 노니 정신이 말끔해진것 같습니다.\n +건강')
        person.health += 4


@manager.assign_event
def event_start(event: Event):
    event.description = '소프트웨어 공학 시간이 되었습니다. 코딩을 안 하는 전공과목이라니 희한한 과목입니다.'
    event.priority = -1

    @event.assign_condition
    def condition(person: Person):
        if 'start_dorm' not in person.traits:
            return False
        return person.in_2nd_period(1) and person.iq < 150

    @event.assign_option('잔다')
    async def option_sleep(msg: discord.Message, person: Person):
        await msg.channel.send('>>> 잠을 잤더니 훨씬 개운해졌습니다.\n+건강')
        person.health += 4

    @event.assign_option('논다')
    async def option_sleep(msg: discord.Message, person: Person):
        await msg.channel.send('>>> 노는 시간동안 즐거웠지만 죄책감이 듭니다.\n-양심')
        person.goodness -= 3

    @event.assign_option('그래도 공부한다')
    async def option_sleep(msg: discord.Message, person: Person):
        await msg.channel.send('>>> 공부를 했더니 머리에 든게 많아진것 같습니다.\n+IQ')
        person.iq += 3


@manager.assign_event
def event_start(event: Event):
    event.description = '교과 시간이 되었습니다. 중학교 때 와 비슷한 수업이라서 어렵지는 않은것 같습니다.'
    event.priority = -1

    @event.assign_condition
    def condition(person: Person):
        if 'start_dorm' not in person.traits:
            return False
        return True
        # return person.grade <= 2 and person.english < 50

    @event.assign_option('잔다')
    async def option_sleep(msg: discord.Message, person: Person):
        await msg.channel.send('>>> 잠을 잤더니 훨씬 개운해졌습니다.\n+건강')
        person.health += 4

    @event.assign_option('논다')
    async def option_sleep(msg: discord.Message, person: Person):
        await msg.channel.send('>>> 노는 시간동안 즐거웠지만 죄책감이 듭니다.\n-양심')
        if random.randint(0, 3) == 0:
            person.traits.append('punish_by_teacher')
        person.goodness -= 3

    @event.assign_option('그래도 공부한다')
    async def option_sleep(msg: discord.Message, person: Person):
        await msg.channel.send('>>> 공부를 했더니 머리에 든게 많아진것 같습니다.\n+IQ')
        person.iq += 3


@manager.assign_event
def event_start(event: Event):
    event.description = '선생님에게 혼이 났습니다. 어떡게 할까요?'
    event.priority = 1

    @event.assign_condition
    def condition(person: Person):
        if 'start_dorm' not in person.traits:
            return False
        if 'punish_by_teacher' not in person.traits:
            return False
        return person.politic < 40

    @event.assign_option('반성문을 쓴다')
    async def option_sleep(msg: discord.Message, person: Person):
        await msg.channel.send('>>> 죄책감은 덜었지만 반성문을 써서 피로합니다.\n -건강 +양심')
        person.health -= 3
        person.goodness += 5
        person.traits.remove('punish_by_teacher')

    @event.assign_option('선생님의 행동에 문제제기를 한다')
    async def option_sleep(msg: discord.Message, person: Person):
        if random.randint(-10, 10) + person.politic > 30:
            await msg.channel.send('>>> 선생님과 설전에서 이겼습니다. 난 잘 못 한게없다.\n +++양심 +++정치')
            person.goodness += 13
            person.politic += 17
            person.traits.remove('punish_by_teacher')
        else:
            await msg.channel.send('>>> 오히려 선생님에게 꾸중을 들었습니다.\n -건강 -양심 +정치')
            person.goodness -= 3
            person.health -= 2
            person.politic += 4


@manager.assign_event
def event_start(event: Event):
    event.description = '집을 가지않는 토요일이 왔습니다.'
    event.priority = -1

    @event.assign_option('잔다')
    async def option_sleep(msg: discord.Message, person: Person):
        await msg.channel.send('>>> 잠을 잤더니 훨씬 개운해졌습니다.\n++건강')
        person.health += 12

    @event.assign_option('운동한다')
    async def option_sleep(msg: discord.Message, person: Person):
        await msg.channel.send('>>> 운동을 했더니 건강해진것 같습니다.\n++건강')
        person.health += 12

    @event.assign_option('롤한다')
    async def option_sleep(msg: discord.Message, person: Person):
        await msg.channel.send('>>> 롤을 했더니 실력이 올라간것 같습니다.\n+게임')
        person.lol += 3

    @event.assign_option('공부한다')
    async def option_sleep(msg: discord.Message, person: Person):
        await msg.channel.send('>>> 공부를 했더니 머리에 든게 많아진것 같습니다.\n+IQ')
        person.iq += 5

    @event.assign_option('책을 읽는다')
    async def option_sleep(msg: discord.Message, person: Person):
        if random.randint(0, 5) == 0:
            await msg.channel.send('>>> 책을 읽었더니 머리에 든게 많아진것 같습니다.\n+IQ')
            person.iq += 4
        elif random.randint(0, 4) == 0:
            await msg.channel.send('>>> 전공책을 읽었더니 머리에 든게 많아진것 같습니다.\n+코딩')
            person.coding += 4
        elif random.randint(0, 3) == 0:
            await msg.channel.send('>>> 신문을 읽었더니 정치 감각이 좋아진것 같습니다.\n+정치')
            person.politic += 4
        elif random.randint(0, 2) == 0:
            await msg.channel.send('>>> 소설책을 읽었더니 즐겁습니다.\n+문학 +건강')
            person.library += 4
            person.health += 3
        elif random.randint(0, 1) == 0:
            await msg.channel.send('>>> 경제학 서적을 읽었더니 머리에 든게 많아진것 같습니다.\n+IQ')
            person.economy += 4
        else:
            await msg.channel.send('>>> 책의 내용을 이해하지 못 했습니다.')
