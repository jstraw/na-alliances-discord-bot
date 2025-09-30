# import json
import asyncio
import logging

import audioop
import discord
import discord.ext.commands

from util import LoggingClientSession, get_channels, has_role
from timers import UpdateSheet
from channels import ManageChannels
import embed

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
        for x, y in bot.cogs.items():
            await y.bot.tree.sync()
        await bot.tree.sync()
        await interaction.edit_original_response(content="Syncing commands... Complete")
    else:
        await interaction.response.send_message("Permisson Denied")


@bot.event
async def on_ready():
    bot.session = LoggingClientSession('https://worldvs.world/alliances/')
    bot.logger.info(f"Logged on as {bot.user} to {bot.guilds}")
    await bot.add_cog(UpdateSheet(bot))
    await bot.add_cog(ManageChannels(bot))
    bot.logger.warning(f"Cogs {bot.cogs}")
        