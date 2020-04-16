import html

import discord
from discord.ext import tasks

import spreadsheet
from band import band

global channel
client = discord.Client()
channel = None
discord_token = open('discord_bot_token', 'r').read()


def get_embed_from_command_data(data):
    teachers_fullname = ['권오석', '이석우', '조수연', '변강순', '우효림', '장창수', '박종대', '김완태', '김경호', '박정열', '배명호', '김한기', '김소영',
                         '박성', '하태효']

    title = "%02d월 %02d일 %1s반 시간표" % (data['헤더']['date'].month, data['헤더']['date'].day, data['헤더']['class_number'])
    text = ''
    for k in range(5):
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

        text += f'** {class_data["class_name"]} {k + 1} 교시 {class_data["time"]} **'

        if class_data['raw_data']['클래스룸']:
            text += f" || {class_data['class_data']['link']} ||"

        text += '\n'

        if teacher_list != '':
            text += f'> ** {teacher_list} **\n'

        if class_data['objective'] != '':
            text += f"> ** {class_data['objective']} **\n"

        text += '\n'

    embed = discord.Embed(title=title, description=text)
    return embed


def get_embed_from_band_data(data):
    embed = discord.Embed(title='2018 대구SW고(3학년)', description=html.unescape(data['content']))
    embed.set_author(name=data['author']['name'], icon_url=data['author']['profile_image_url'])
    return embed


@tasks.loop(seconds=3600.0)
async def band_parse_loop():
    global channel
    for item in band.get_post():
        print(item)
        await channel.send(embed=get_embed_from_band_data(item))
        for photo in item['photos']:
            await channel.send(photo['url'])


@client.event
async def on_ready():
    global channel
    print('Start Process')
    channel = client.get_channel(699239553789067285)
    band_parse_loop.start()


@client.event
async def on_message(msg: discord.Message):
    print(msg)
    if msg.channel.id == 696585229347061843 and (not msg.author.bot):
        if msg.content[0] == 'ㄱ':
            result = spreadsheet.run_command(msg.content)
            if result['status'] == 200:
                get_embed_from_command_data(result)
                await channel.send(embed=result)
            elif result:
                await msg.channel.send(result)
            else:
                print(result)


client.run(discord_token)
