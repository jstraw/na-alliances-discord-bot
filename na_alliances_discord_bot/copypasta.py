"""Manage Channel view/hide and regeneration"""
import logging

import discord
from discord.ext import commands
import na_alliances_discord_bot.util as util


class copyPasta(commands.Cog):
    """Command Cog for Copy/Paste 
    
    Guild Leader
    Commander
    Aleeva"""

    def __init__(self, bot: discord.ext.commands.Bot):
        self.bot = bot
        self.config = bot.config
        super().__init__()

    async def cog_load(self):
        """Configure the cog on startup"""
        log = logging.getLogger("copypasta.copyPasta")
        log.info("Copy/Paste cog online")

    @discord.app_commands.command(
            name="welcome_guild_leader",
            description="Welcome a Guild Leader")
    @discord.app_commands.default_permissions(ban_members=True)
    @discord.app_commands.checks.has_role("Admin")
    async def welcome_guild_leader(self, interaction: discord.Interaction,
                                   gl: discord.Member = None):
        """Welcome a Guild Leader"""
        log = logging.getLogger("copypasta.copyPasta.welcome.gl")
        log.info("Welcome Guild Leader")
        embed = discord.Embed(
            title="We've added your new role!",
            timestamp=discord.utils.utcnow(),
            description="""* <#1192589245462884443> is for guild leaders only. Skim the pins and general conversation there. We'll sometimes ask for guild leader input on structural changes to the server and feedback on function, so check in there from time to time.
* Make sure you register a full API key with Aleeva, not a Lite API key. The full API key is used to identify your upcoming World vs. World team for a team reshuffle, letting you use the reset bot early.
* Reset bot goes live every Thursday, so if your group runs on reset, let the rest of your team know where you're going so that they can plan accordingly.
* You can now post recruitment messages in <#1192582699953688708> .
* You can use the [at] teamname command to ping players on your team in order to announce your runs. Please do this responsibly. You can use the voice comms in this server, or you can link to your own Discord.
            """
        )
        await interaction.response.send_message(f"Welcome {gl.mention or ""}",
                                                embed=embed)
        