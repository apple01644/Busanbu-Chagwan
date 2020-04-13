import discord
from discord.ext import tasks

import spreadsheet
from band import band

client = discord.Client()
channel = client.get_channel(696585229347061843)
discord_token = open('discord_bot_token', 'r').read()


def get_embed_from_band_data(data):
    embed = discord.Embed(title='2018 대구SW고(3학년)', description=data['content'])
    embed.set_author(name=data['author']['name'], icon_url=data['author']['profile_image_url'])
    return embed


@tasks.loop(seconds=60.0)
async def band_parse_loop():
    for item in band.get_post():
        await channel.send(embed=get_embed_from_band_data(item))
        for photo in item['photos']:
            await channel.send(photo['url'])


@client.event
async def on_ready():
    print('Start Process')
    band_parse_loop.start()


@client.event
async def on_message(msg: discord.Message):
    print(msg)
    if msg.channel.id == 696585229347061843 and (not msg.author.bot):
        if msg.content[0] == 'ㄱ':
            result = spreadsheet.run_command(msg.content)
            if result:
                await msg.channel.send(result)
            else:
                print(result)


client.run(discord_token)
