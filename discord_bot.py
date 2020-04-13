
import discord
import asyncio
from band import Band

from discord.ext import tasks

client = discord.Client()
channel = None

band = Band()

@client.event
async def on_ready():
    print('Logged in as')
    print(client.user.name)
    print(client.user.id)
    print('------')
    slow_count.start()

@client.event
async def on_message(message):
    global channel
    channel = message.channel
    if message.content.startswith('!start'):
        await channel.send('Start!')

@tasks.loop(seconds=3600.0)
async def slow_count():
    if channel != None:
        for i in band.getPost():
            await channel.send(embed=getEmbed(i))
            for j in i['photos']:
                await channel.send(j['url'])


def getEmbed(data):
    embed = discord.Embed(
        description=data['content']
    )
    embed.add_field(name="작성자", value=data['author']['name'], inline=True)
    return embed

client.run('Njk3NjQ3MjM3MTAyMzA1MzUx.XpHGaA.mIJwqpNWWAuXp1ktr4z0d7mzpD4')