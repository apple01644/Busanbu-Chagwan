import static
import config
import discord


@static.DiscordModule.assign_onready(None)
async def on_ready(discord_bot: static.DiscordBot, none):
    user = discord_bot.client.get_user(config.discord_info['admin user id'])
    dm_channel = user.dm_channel
    if dm_channel is None:
        dm_channel = await user.create_dm()
    channel = discord_bot.client.get_channel(config.discord_info['free channel id'])
    allowed_channels = [dm_channel]

    await dm_channel.send('안녕하세요')

    @static.CommandBinding.assign_command('조국', allowed_channels)
    async def parrot(query: list, msg: discord.Message, **kwargs):
        await channel.send(msg.content[4:])
