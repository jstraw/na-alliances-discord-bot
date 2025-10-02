import logging
import discord

def make_server_embed(content, server):
    log = logging.getLogger(__name__)
    log.info("Creating Server Embed for %s with %s Alliances and %s Guilds",
             server, len(content['Alliances']), len(content['SoloGuilds']))
    alliances = [alliance for alliance in content['Alliances']
                 if alliance[server] and '[' in alliance['Alliance:']]
    alliance_embed = discord.Embed(
        title="Alliances",
        # color=discord.colour.parse_hex_number('#FF0000'),
        timestamp=discord.utils.utcnow()
        )

    for alliance in alliances:
        guilds = [f'* {g}' for g in alliance['Guilds'].split('\n')]
        alliance_embed.add_field(
            name=alliance['Alliance:'],
            value='\n'.join(guilds),
            inline=False
        )

    guilds = [guild for guild in content['SoloGuilds']
                 if guild[server] and '[' in guild['Solo Guilds']]
    solos = [f'* {g['Solo Guilds']}' for g in guilds]
    guild_embed = discord.Embed(
        title="Guilds",
        # color=discord.colour.Color(0xFF0000),
        timestamp=discord.utils.utcnow(),
        description='\n'.join(solos)
        )
    return (alliance_embed, guild_embed)
