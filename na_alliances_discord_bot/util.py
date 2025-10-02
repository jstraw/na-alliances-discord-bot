"""Utility Functions/Classes"""

import logging

import aiohttp
import aiosqlite
import discord

class LoggingClientSession(aiohttp.ClientSession):
    """Configure Logging of aiohttp requests as needed"""
    async def _request(self, method, str_or_url, **kwargs):
        logging.debug('Starting request <%s %r>', method, str_or_url)
        return await super()._request(method, str_or_url, **kwargs)

async def get_channels(bot, config):
    """
    Get channels that match a pattern from a list of guilds.
    
    In Config set a dictionary key to a format like below and pass that dict in:
    {"servername": ["pat1", "pat2"], "server2": "pattern"}
    
    :param bot: The discord.commands.bot we use to access discord
    :param config: Hash of the servers to look up
    :returns: The list of discord.GuildChannel to work on
    """
    log = logging.getLogger("util.get_channels")
    log.info("Looking up channels for %s", config)
    channels = []
    for guild in bot.guilds:
        log.debug('looking for %s', guild)
        if guild.name not in config:
            continue
        for channel in await guild.fetch_channels():
            log.debug('looking in %s at %s against %s',
                      guild, channel.name, config[guild.name])
            if isinstance(config[guild.name], list) and channel.name in config[guild.name]:
                log.debug('append channel')
                channels.append(channel)
            elif isinstance(config[guild.name], str) and channel.name == config[guild.name]:
                log.debug('append channel')
                channels.append(channel)
    log.warning("returning %s", channels)
    return channels


async def db_connection(config):
    """
    Create the Database tables and connection
    
    :param config: The global config (that contains a db parameter)
    :returns: A aiosqlite database connection"""
    db = await aiosqlite.connect(config['db'])
    await db.execute("""CREATE TABLE IF NOT EXISTS messages (
                storage_name VARCHAR(20) unique,
                last_updated CHARACTER(20),
                storage_id INTEGER unique
                );""")
    await db.commit()
    await db.execute("""CREATE TABLE IF NOT EXISTS outputs (
                guild text,
                channel text,
                server text,
                last_updated CHARACTER(20),
                storage_id INTEGER unique
                );""")
    await db.commit()
    # c.execute("""CREATE TABLE IF NOT EXISTS alliances (
    #         updated_at CHARACTER(20),
    #         name TEXT,
    #         guilds BLOB,
    #         ap INTEGER,
    #         dmp INTEGER,
    #         dot INTEGER,
    #         dt INTEGER,
    #         hoj INTEGER,
    #         lk INTEGER,
    #         lc INTEGER,
    #         mc INTEGER,
    #         moogooloo INTEGER,
    #         mw INTEGER,
    #         rr INTEGER,
    #         cob INTEGER,
    #         throb INTEGER,
    #         tod INTEGER,
    #         yh INTEGER,
    #         )""")
    # c.execute("""CREATE TABLE IF NOT EXISTS sologuilds (
    #         updated_at CHARACTER(20),
    #         name TEXT,
    #         ap INTEGER,
    #         dmp INTEGER,
    #         dot INTEGER,
    #         dt INTEGER,
    #         hoj INTEGER,
    #         lk INTEGER,
    #         lc INTEGER,
    #         mc INTEGER,
    #         moogooloo INTEGER,
    #         mw INTEGER,
    #         rr INTEGER,
    #         cob INTEGER,
    #         throb INTEGER,
    #         tod INTEGER,
    #         yh INTEGER,
    #         )""")
    # res = await db.execute("select name from sqlite_master order by name;")
    # r = await res.fetchall()
    # if 'alliances' not in r or 'sologuilds' not in r:
    #     raise aiosqlite.DatabaseError('Could not build sqlite db')
    return db

async def has_role(interaction: discord.Interaction):
    """Confirm that the user requesting to do a / command is an Admin on their server
    Or in the Admin List in config (for private messages)
    
    :param interaction: Discord request that triggered the role check
    :returns: True => continue to process, False => check failed"""
    log = logging.getLogger("util.has_role")
    log.info("Checking for user in admin list")
    log.debug(interaction.user.roles)
    if any(x for x in interaction.user.roles if 'Admin' == x.name):
        log.info("Found %s in Admin Role", interaction.user.name)
        return True
    if interaction.user.id in interaction.client.config[
            'allowed_admins'].values():
        log.info("Found %s in Admin ID list", interaction.user.name)
        return True
    else:
        interaction.response.send_message("Permission Denied")
        return False
