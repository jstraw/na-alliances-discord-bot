import datetime
import io
import json
import logging

import discord
from discord.ext import tasks, commands
import na_alliances_discord_bot.util as util


class ManageChannels(commands.Cog):
    def __init__(self, bot: discord.ext.commands.Bot):
        self.bot = bot
        self.config = bot.config
        super().__init__()

    async def cog_load(self):
        log = logging.getLogger("channels.ManageChannels")
        log.info("Manage Channel cog online")

    async def manage_team_channels(self, channel_filter: list[str], perms: discord.PermissionOverwrite,
                                   regenerate=False):
        log = logging.getLogger("channels.ManageChannels.manage_team_channels")
        channels = []
        categories = set()
        for guild in self.bot.guilds:
            if guild.name not in self.config['regenerate_channels']:
                continue
            for channel in await guild.fetch_channels():
                if any(x for x in channel_filter if x in channel.name):
                    log.debug(f"Work on {channel.name}")
                    channels.append(channel)
                    categories.add(channel.category)
        for channel in channels:
            if regenerate:
                log.debug(f"regenerating {channel.name}")
                await channel.edit(name=f"{channel.name}-rename")
                await channel.clone(name=channel.name, category=channel.category,
                                    reason="Rebuilding Team Channels")
                await channel.delete()
        for category in list(categories):
            log.debug(f"{category.name} - {[x.name for x in channel.guiild.roles]}")
            role = discord.utils.get(channel.guild.roles, name=category.name)
            for cat_channel in category.channels:
                if any(x for x in channel_filter if x in cat_channel.name):
                    log.info(f"Change perms on {cat_channel.name} for {role.name}")
                    await cat_channel.set_permissions(role, overwrite=perms)
        return channels

    @discord.app_commands.command(name="lock_team_channels", description="Lock Out NA Alliance Server Team Channels")
    @discord.app_commands.check(util.has_role)
    async def lock_team_channels(self, interaction: discord.Interaction):
        log = logging.getLogger("channels.ManageChannels.lock_team_channels")
        log.info("Locking Team Channels")
        await interaction.response.send_message("Locking Team Channels")
        perms = discord.PermissionOverwrite()
        perms.view_channel = False
        channel_filter = [
            "-general",
            "-raid-alerts",
            "-schedules",
        ]
        channels = await self.manage_team_channels(channel_filter, perms, regenerate=True)
        log.info("Locking Team Channels Complete")
        await interaction.edit_original_response(content="Locking Team Channels... Complete")

    @discord.app_commands.command(name="lock_reset_channels", description="Lock NA Alliance Reset Channels for all teams")
    @discord.app_commands.check(util.has_role)
    async def lock_reset_channels(self, interaction: discord.Interaction):
        log = logging.getLogger("channels.ManageChannels.lock_reset_channels")
        log.info("Locking Reset Channels")
        await interaction.response.send_message("Locking Reset Channels")
        perms = discord.PermissionOverwrite()
        perms.view_channel = False
        channel_filter = ['-reset']
        channels = await self.manage_team_channels(channel_filter, perms)
        log.info("Locking Reset Channels Complete")
        await interaction.edit_original_response(content="Locking Reset Channels... Complete")


    @discord.app_commands.command(name="unlock_team_channels", description="Unlock NA Alliance Team Channels (including Reset)")
    @discord.app_commands.check(util.has_role)
    async def unlock_team_channels(self, interaction: discord.Interaction):
        log = logging.getLogger("channels.ManageChannels.unlock_team_channels")
        log.info("Unlocking Channels")
        await interaction.response.send_message("Unlocking Team Channels")
        perms = discord.PermissionOverwrite()
        perms.view_channel = True
        channel_filter = [
            "-general",
            "-raid-alerts",
            "-schedules",
            "-reset",
        ]
        await self.manage_team_channels(channel_filter, perms)
        log.info("Unlocking Channels Complete")
        await interaction.edit_original_response(content="Unlocking Team Channels... Complete")
