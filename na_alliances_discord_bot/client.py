# import json
import logging

import discord
import discord.ext.commands

from na_alliances_discord_bot.util import LoggingClientSession
from na_alliances_discord_bot.timers import UpdateSheet
from na_alliances_discord_bot.channels import ManageChannels

class AlliancesBot(discord.ext.commands.Bot):
    def __init__(self, command_prefix, intents: discord.Intents):
        super().__init__(command_prefix, intents=intents)
        self.logger = logging.getLogger("alliancesBot")




# intents.message_content = True  # This isn't needed for my own messages
bot = AlliancesBot(
    "#na#",
    intents=discord.Intents.default())

@bot.tree.command(name="sync",
                  description="Admin Only: Resync commands")
async def sync(interaction: discord.Integration):
    if interaction.user.id in bot.config['allowed_admins'].values():
        await interaction.response.send_message("Syncing commands")
        for _, y in bot.cogs.items():
            await y.bot.tree.sync()
        await bot.tree.sync()
        await interaction.edit_original_response(content="Syncing commands... Complete")
    else:
        await interaction.response.send_message("Permisson Denied")

@bot.event
async def on_message(message: discord.Message):
    log = logging.getLogger("bot.on_message")
    log.debug("was sent: %s", message)
    if message.content == '#sync#' and message.author.id in bot.config['allowed_admins'].values():
        log.info("Sync Requested by DM by %s", message.author)
        for _, y in bot.cogs.items():
            await y.bot.tree.sync()
        await bot.tree.sync()
        await message.reply("Synced.")
        

@bot.event
async def on_ready():
    bot.session = LoggingClientSession('https://worldvs.world/alliances/')  # pylint: disable=W0201
    bot.logger.info("Logged on as %s to %s", bot.user, bot.guilds)
    await bot.add_cog(UpdateSheet(bot))
    await bot.add_cog(ManageChannels(bot))
    bot.logger.warning("Cogs %s", bot.cogs)
        