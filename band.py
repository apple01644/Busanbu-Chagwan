import html
import json
import traceback

import discord
import requests_async  as req
from discord.ext import tasks

import config
import static


class Band:
    urls = {
        'band': 'https://openapi.band.us/v2.1/bands',
        'posts': 'https://openapi.band.us/v2/band/posts'
    }
    band_channel = None

    def __init__(self):
        self.key = json.load(open('band_api.json', 'r'))
        self.param_for_get_band = {'access_token': self.key['access_token']}
        self.param_for_get_post = {'access_token': self.key['access_token'],
                                   'band_key': 'AADe-67DagLFl4xgYFYmMm0r',
                                   'locale': 'ko_KR'}
        self.last_refresh_time = 0

    async def get_post(self):
        response = await req.get(self.urls['posts'], params=self.param_for_get_post)
        assert response.status_code == 200
        posts = json.loads(response.text)
        assert posts["result_code"] == 1
        result = [item for item in posts['result_data']['items'] if item['created_at'] > self.last_refresh_time]
        self.last_refresh_time = max([item['created_at'] for item in result] + [self.last_refresh_time])
        return result

    @staticmethod
    def get_embed_from_band_data(data: dict):
        embed = discord.Embed(title='2018 대구SW고(3학년)', description=html.unescape(data['content']).replace('~', ''))
        embed.set_author(name=data['author']['name'], icon_url=data['author']['profile_image_url'])
        return embed

    @tasks.loop(seconds=3600.0)
    async def band_parse_loop(self):
        try:
            if self.last_refresh_time == 0:
                await self.get_post()
                return

            posts = await self.get_post()
            for post in posts:
                await self.band_channel.send(embed=self.get_embed_from_band_data(post))
                for photo in post['photos']:
                    await self.band_channel.send(photo['url'])
        except Exception as e:
            print(traceback.format_exc(), e)


band = Band()


@static.DiscordModule.assign_onready(band)
async def on_ready(discord_bot: static.DiscordBot, self: Band):
    self.band_channel = discord_bot.client.get_channel(config.discord_info['alarm channel id'])
    self.band_parse_loop.start()
