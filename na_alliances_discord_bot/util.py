import logging

import aiohttp
import aiosqlite
import discord

class LoggingClientSession(aiohttp.ClientSession):
    async def _request(self, method, url, **kwargs):
        logging.debug('Starting request <%s %r>', method, url)
        return await super()._request(method, url, **kwargs)
    
async def get_channels(bot, config):
    log = logging.getLogger("util.get_channels")
    channels = []
    for guild in bot.guilds:
        log.info(f'looking for {guild}')
        for channel in await guild.fetch_channels():
            log.info(f'looking in {guild} at {channel.name} against {config[guild.name]}')
            if channel.name in config[guild.name]:
                log.debug('append channel')
                channels.append(channel)
    log.warning(f"returning {channels}")
    return channels

async def db_connection(config):
    db = await aiosqlite.connect(config['db'])
    await db.execute("""CREATE TABLE IF NOT EXISTS messages (
                storage_name VARCHAR(20) unique,
                last_updated CHARACTER(20),
                storage_id INTEGER unique
                );""")
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