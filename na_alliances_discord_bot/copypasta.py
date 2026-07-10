"""Manage Channel view/hide and regeneration"""
import logging

import aiohttp
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
        log.info(f"Welcome Guild Leader {gl.name}")
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
        
    @discord.app_commands.command(
            name="welcome_commander",
            description="Welcome a Commander")
    @discord.app_commands.default_permissions(ban_members=True)
    @discord.app_commands.checks.has_role("Admin")
    async def welcome_commander(self, interaction: discord.Interaction,
                                   cmdr: discord.Member = None):
        """Welcome a Commander"""
        log = logging.getLogger("copypasta.copyPasta.welcome.cmdr")
        log.info(f"Welcome Commander {cmdr.name}")
        embed = discord.Embed(
            title="We've added your new role!",
            timestamp=discord.utils.utcnow(),
            description="""
* Make sure that you have registered a **full** API key with Aleeva, to identify your current and upcoming World vs. World teams.
* You can now send pings in your team channel using either the @ here or @ [teamname] command. Please ping responsibly.
* You can now interact with the reset bot in your team channel, which goes live every Thursday around noon eastern. Let your other commanders and teammates know which map you'll be taking your squad to on Fridays, if you play during reset.
* You can use your team-specific voice comms on this server, or you can link to your own Discord server for comms. You can drag users that have not completed API verification into your team-specific voice channels.
            """
        )
        await interaction.response.send_message(f"Welcome {cmdr.mention or ""}",
                                                embed=embed)
        
    @discord.app_commands.command(
            name="lockout_reminder",
            description="Post a Reminder about Lockout to this channel")
    @discord.app_commands.default_permissions(ban_members=True)
    @discord.app_commands.checks.has_role("Admin")
    async def lockout_reminder(self, interaction: discord.Integration,
                               ping: discord.Role = None):
        "Announce next Lockout date/time"
        log = logging.getLogger("copypasta.copyPasta.lockout")
        now = discord.utils.utcnow()
        on = None
        async with aiohttp.ClientSession() as sess:
            async with session.get("https://api.guildwars2.com/v2/wvw/timers/lockout") as resp:
                on = discord.utils.parse_time(await resp.json()['na'])
        log.info(f"{interaction.user.name} Announcing lockout to {interaction.channel.guild}-{interaction.channel.name} for {on}")
        embed = discord.Embed(
            title="Upcoming NA Lockout",
            timestamp=now,
            description=f"""
Hello {ping.mention}!

Lockout is on {discord.utils.format_dt(on, 'F')} / {discord.utils.format_dt(on, 'R')}. 
Please confirm your WvW guild by checking for the castle icon in the guild list.  If you need to update your guild:
* In the guild tab, represent the guild you are choosing
* Go to the World vs World window in game
* Select the last tab on the left
* Confirm the guild you want to represent is shown and click "Select Battle Guild"."""
        )
        await interaction.response.send_message("", embed=embed)
    )