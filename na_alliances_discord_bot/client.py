# import json
import asyncio
import logging

import audioop
import discord
import discord.ext.commands

from util import LoggingClientSession, get_channels
from timers import UpdateSheet
import embed

class AlliancesBot(discord.ext.commands.Bot):
    def __init__(self, command_prefix, intents: discord.Intents):
        super().__init__(command_prefix, intents=intents)
        self.logger = logging.getLogger("alliancesBot")




# intents.message_content = True  # This isn't needed for my own messages
bot = AlliancesBot(
    "#na#",
    intents=discord.Intents.default())



@bot.event
async def on_ready():
    bot.session = LoggingClientSession('https://worldvs.world/alliances/')
    bot.logger.info(f"Logged on as {bot.user} to {bot.guilds}")
    await bot.add_cog(UpdateSheet(bot))
    bot.logger.warning(f"Cogs {bot.cogs}")
    for x, y in bot.cogs.items():
        await y.bot.tree.sync()
    synced = await bot.tree.sync()
    bot.logger.warning(f"Synced {synced} commands.")


async def passedover():
    # ch = bot.get_channel(734863531480186891)  # Set this to a private reconnect notification channel
    # await ch.send("direct whee")
    bot.send_channels = await get_channels(bot, bot.config['channels'])
    async with bot.session.get('na/data.json') as resp:
        assert resp.status < 300
        logging.debug("Got http response")
        content = await resp.json()
        logging.debug("content retrieved")
    logging.info(f"Sending Embed for YH to {bot.send_channels}")
    embeds = embed.make_server_embed(content, 'YH')
    for ch in bot.send_channels:
        d = await ch.send('# Yohlon Haven Guild List',
                        embeds=embeds)
        bot.logger.info("presleep")
        await asyncio.sleep(5)
        bot.logger.info("postsleep")
        await d.edit(content="# Yohlon Haven Guild List test", embeds=embeds)



    for gw2server in bot.config['servers'].keys():
        async with bot.session.get(f'na/{gw2server}.md.txt') as resp:
            content = await resp.text()
        bot.logger.debug(content)
        for ch in bot.send_channels:
            await ch.send(content)
    
        