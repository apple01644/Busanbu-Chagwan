import html
import random

import discord
from discord.ext import tasks

import scheduler
import spreadsheet
from band import band

global channel, guild, body
client = discord.Client()
channel = None
guild = None
body = {}
discord_token = open('discord_bot_token', 'r').read()


def get_embed_from_band_data(data):
    embed = discord.Embed(title='2018 대구SW고(3학년)', description=html.unescape(data['content']).replace('~', ''))
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
    global channel, guild
    print('Start Process')
    channel = client.get_channel(699239553789067285)
    guild = client.get_guild(696585228906528881)
    band_parse_loop.start()
    scheduler.alarm_channel = channel
    scheduler.first_channel = client.get_channel(705953156294639746)
    scheduler.second_channel = client.get_channel(705953050040205412)
    scheduler.first_channel = client.get_channel(705953120341065818)
    scheduler.class_loop.start()


@client.event
async def on_message(msg: discord.Message):
    global channel, guild, body
    print(msg)
    print(msg.content)
    if msg.content[0] == 'ㄱ' and (not msg.author.bot) and len(msg.content) > 1:
        if msg.channel.id in [705953156294639746, 705953050040205412, 705953120341065818]:
            if msg.content.find('ㄱ시간표') == 0:
                result = spreadsheet.run_command(msg.content, [role.name for role in msg.author.roles])
                if result['status'] == 200:
                    data = spreadsheet.command_data_to_description(result)
                    await msg.channel.send(embed=discord.Embed(title=data['title'], description=data['description']))
                elif result:
                    await msg.channel.send(result['body'])
                else:
                    await msg.channel.send('예외 발생')
        elif msg.channel.id in [696585229347061843]:
            if msg.content.find('ㄱ탄창비우기') == 0:
                if 'russian_roulette' not in body:
                    body['russian_roulette'] = []
                body['russian_roulette'] = []
            elif msg.content.find('ㄱ장전') == 0:
                if 'russian_roulette' not in body:
                    body['russian_roulette'] = []
                for query in msg.content[4:].split(','):
                    query = query.strip()
                    if len(query) > 0:
                        user = None
                        for member in guild.members:
                            if member.nick is not None:
                                if member.nick.find(query) != -1:
                                    user = member
                                    break
                            else:
                                if member.name.find(query) != -1:
                                    user = member
                                    break
                        if user is not None:
                            body['russian_roulette'].append(user)
                size = len(body['russian_roulette'])
                if size == 0:
                    await msg.add_reaction(emoji='0️⃣')
                elif size == 1:
                    await msg.add_reaction(emoji='1️⃣')
                elif size == 2:
                    await msg.add_reaction(emoji='2️⃣')
                elif size == 3:
                    await msg.add_reaction(emoji='3️⃣')
                elif size == 4:
                    await msg.add_reaction(emoji='4️⃣')
                elif size == 5:
                    await msg.add_reaction(emoji='5️⃣')
                elif size == 6:
                    await msg.add_reaction(emoji='6️⃣')
                elif size == 7:
                    await msg.add_reaction(emoji='7️⃣')
                elif size == 8:
                    await msg.add_reaction(emoji='8️⃣')
                elif size == 9:
                    await msg.add_reaction(emoji='9️⃣')
                elif size == 10:
                    await msg.add_reaction(emoji='🔟')
                else:
                    await msg.add_reaction(emoji='🔢')
            elif msg.content.find('ㄱ발사') == 0:
                if 'russian_roulette' not in body:
                    body['russian_roulette'] = []
                if len(body['russian_roulette']) == 0:
                    await msg.channel.send('총열이 비어있습니다.')
                    return
                index = random.randint(0, len(body['russian_roulette']) - 1)
                died = body['russian_roulette'][index]
                if died.nick is None:
                    await msg.channel.send(f'{died.name}(이)가 총을 맞았습니다.')
                else:
                    await msg.channel.send(f'{died.nick}(이)가 총을 맞았습니다.')
                body['russian_roulette'] = []


client.run(discord_token)
