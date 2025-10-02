import logging

import aiohttp
import aiosqlite
import discord

class LoggingClientSession(aiohttp.ClientSession):
    async def _request(self, method, str_or_url, **kwargs):
        logging.debug('Starting request <%s %r>', method, str_or_url)
        return await super()._request(method, str_or_url, **kwargs)

async def get_channels(bot, config):
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
