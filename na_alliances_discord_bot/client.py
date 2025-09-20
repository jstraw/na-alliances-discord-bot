# import json
import asyncio
import logging

import aiohttp
import audioop
import discord

import embed

class LoggingClientSession(aiohttp.ClientSession):
    async def _request(self, method, url, **kwargs):
        logging.debug('Starting request <%s %r>', method, url)
        return await super()._request(method, url, **kwargs)

class AlliancesClient(discord.Client):
    def __init__(self, intents: discord.Intents):
        super().__init__(intents=intents)
        self.tree = discord.app_commands.CommandTree(self)
        self.logger = logging.getLogger("alliancesClient")


intents = discord.Intents.default()

# intents.message_content = True  # This isn't needed for my own messages
client = AlliancesClient(intents=intents)


@client.event
async def on_ready():
    client.session = LoggingClientSession('https://worldvs.world/alliances/')
    client.logger.info(f"Logged on as {client.user} to {client.guilds}")
    # ch = client.get_channel(734863531480186891)  # Set this to a private reconnect notification channel
    # await ch.send("direct whee")
    client.send_channels = []
    for guild in client.guilds:
        for channel in guild.channels:
            if channel.name in client.config['channels'][guild.name]:
                client.send_channels.append(channel)
    async with client.session.get('na/data.json') as resp:
        content = await resp.json()
    embeds = embed.make_server_embed(content, 'YH')
    for ch in client.send_channels:
            d = await ch.send('# Yohlon Haven Guild List',
                          embeds=embeds)
    client.logger.info("presleep")
    await asyncio.sleep(5)
    client.logger.info("postsleep)")
    await d.edit(content="# Yohlon Haven Guild List test", embeds=embeds)


async def passedover():
    for gw2server in client.config['servers'].keys():
        async with client.session.get(f'na/{gw2server}.md.txt') as resp:
            content = await resp.text()
        client.logger.debug(content)
        for ch in client.send_channels:
            await ch.send(content)
    
        