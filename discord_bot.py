import html

import discord
import datetime
from discord.ext import tasks

import spreadsheet
import scheduler
from band import band

global channel
client = discord.Client()
channel = None
discord_token = open('discord_bot_token', 'r').read()


def get_embed_from_band_data(data):
    embed = discord.Embed(title='2018 대구SW고(3학년)', description=html.unescape(data['content']).replace('~', ''))
    embed.set_author(name=data['author']['name'], icon_url=data['author']['profile_image_url'])
    return embed


def command_data_to_description(data):
    data = spreadsheet.preprocess_command_data(data)
    title = "%02d월 %02d일 %1s반 시간표" % (data['헤더']['date'].month, data['헤더']['date'].day, data['헤더']['class_number'])
    text = ''
    for k in range(7):
        class_data = data[f'{k + 1} 교시']
        class_datetime = datetime.datetime.combine(data['헤더']['date'], scheduler.classes[k]['end'])
        if datetime.datetime.now() < class_datetime:
            text += f'** {class_data["class_name"]} ({k + 1} 교시 {class_data["time"]}) **'
        else:
            text += f'~~ {class_data["class_name"]} ({k + 1} 교시 {class_data["time"]}) ~~'
        if class_data['class_data']:
            if class_data['class_data']['link']:
                text += f" || {class_data['class_data']['link']} ||"

        text += '\n'

        if class_data['teacher_list'] != '':
            text += f'> ** {class_data["teacher_list"]} **\n'

            if not data['헤더']['is_template']:
                if class_data['objective'] != '':
                    text += f"> ** {class_data['objective']} **\n"

            text += '\n'

    return {'title': title, 'description': text}


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
    scheduler.alarm_channel = channel
    scheduler.class_loop.start()


@client.event
async def on_message(msg: discord.Message):
    print(msg)
    if msg.channel.id == 696585229347061843 and (not msg.author.bot) and len(msg.content) > 3:
        if msg.content[0] == 'ㄱ':
            if msg.content.find('시간표') == 1:
                result = spreadsheet.run_command(msg.content, [role.name for role in msg.author.roles])
                if result['status'] == 200:
                    data = command_data_to_description(result)
                    await msg.channel.send(embed=discord.Embed(title=data['title'], description=data['description']))
                elif result:
                    await msg.channel.send(result['body'])
                else:
                    print(result)


client.run(discord_token)
