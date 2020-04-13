
import discord
import asyncio
from band import Band

from discord.ext import tasks

client = discord.Client()
channel = None
discord_token = open('id.txt', 'r').read()

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
    if message.content.startswith('!start'):
        channel = message.channel
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

client.run(discord_token)