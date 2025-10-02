"""Manage Channel view/hide and regeneration"""
import logging

import discord
from discord.ext import commands
import na_alliances_discord_bot.util as util


class ManageChannels(commands.Cog):
    """Command Cog for managing channels via / commands
    
    Hide Reset channels
    Hide team channels
    Regenerate channels
    Show Team Channels"""

    def __init__(self, bot: discord.ext.commands.Bot):
        self.bot = bot
        self.config = bot.config
        super().__init__()

    async def cog_load(self):
        """Configure the cog on startup"""
        log = logging.getLogger("channels.ManageChannels")
        log.info("Manage Channel cog online")

    async def manage_team_channels(self, channel_filter: list[str],
                                   perms: discord.PermissionOverwrite,
                                   regenerate: bool=False):
        """
        Change visibility of team channels.
        
        TODO: move regeneration out to its own command

        :param channel_filter: A list of substrings to look for in channel names
        :param perms: a Permission Overwrite object to modify found channels with
        :param regenerate: Boolean to enable or disable regnerating channels
        """
        log = logging.getLogger("channels.ManageChannels.manage_team_channels")
        channels = []
        categories = set()
        for guild in self.bot.guilds:
            if guild.name not in self.config['regenerate_channels']:
                continue
            for channel in await guild.fetch_channels():
                if any(x for x in channel_filter if x in channel.name):
                    log.debug("Work on %s", channel.name)
                    channels.append(channel)
                    categories.add(channel.category)
        for channel in channels:
            if regenerate:
                log.debug("regenerating %s", channel.name)
                await channel.edit(name=f"{channel.name}-rename")
                await channel.clone(name=channel.name,
                                    category=channel.category,
                                    reason="Rebuilding Team Channels")
                await channel.delete()
        for category in list(categories):
            log.debug("%s - %s", category.name,
                      [x.name for x in channel.guild.roles])
            role = discord.utils.get(channel.guild.roles, name=category.name)
            category.set_permissions(role, overwrite=perms)
            for cat_channel in category.channels:
                if any(x for x in channel_filter if x in cat_channel.name):
                    log.info("Change perms on %s for %s",
                             cat_channel.name, role.name)
                    await cat_channel.set_permissions(role, overwrite=perms)
        return channels

    @discord.app_commands.command(
            name="lock_team_channels",
            description="Lock Out NA Alliance Server Team Channels")
    @discord.app_commands.check(util.has_role)
    async def lock_team_channels(self, interaction: discord.Interaction):
        """Lock out team channels"""
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
        await self.manage_team_channels(channel_filter, perms, regenerate=True)
        log.info("Locking Team Channels Complete")
        await interaction.edit_original_response(
                content="Locking Team Channels... Complete")

    @discord.app_commands.command(
            name="lock_reset_channels",
            description="Lock NA Alliance Reset Channels for all teams")
    @discord.app_commands.check(util.has_role)
    async def lock_reset_channels(self, interaction: discord.Interaction):
        """Lock the Reset Team Channels"""
        log = logging.getLogger("channels.ManageChannels.lock_reset_channels")
        log.info("Locking Reset Channels")
        await interaction.response.send_message("Locking Reset Channels")
        perms = discord.PermissionOverwrite()
        perms.view_channel = False
        channel_filter = ['-reset']
        await self.manage_team_channels(channel_filter, perms)
        log.info("Locking Reset Channels Complete")
        await interaction.edit_original_response(
                content="Locking Reset Channels... Complete")

    @discord.app_commands.command(
            name="unlock_team_channels",
            description="Unlock NA Alliance Team Channels (including Reset)")
    @discord.app_commands.check(util.has_role)
    async def unlock_team_channels(self, interaction: discord.Interaction):
        """Unlock all Team Channels"""
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
        await interaction.edit_original_response(
                content="Unlocking Team Channels... Complete")
