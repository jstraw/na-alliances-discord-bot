import datetime
import io
import json
import logging

import aiosqlite
import discord
from discord.ext import tasks, commands
import gspread
import na_alliances_discord_bot.embed as embed
import na_alliances_discord_bot.naspreadsheet as naspreadsheet
import na_alliances_discord_bot.util as util


class UpdateSheet(commands.Cog):
    # self.db => sqlite database
    # self.storage_channel => channel with the full data/update time
    # self.storage_message => message id of the stored data
    # self.current_data => message with the data (from self.storage_message)
    # self.last_updated => timestamp of last update datetime.datetime
    # self.json_data => actual stored data
    # self.gspread => google spreadsheet connector
    # self.sheet => internal interface for getting data from spreadsheet
    def __init__(self, bot: discord.ext.commands.Bot):
        self.bot = bot
        self.config = bot.config
        super().__init__()

    @discord.app_commands.command(name="update_embeds")
    async def update(self, interaction: discord.Interaction):
        await interaction.response.send_message(f"Pushing Embeds")
        await self.push_embeds()
        

        
    async def cog_unload(self):
        self.check_for_updates.cancel()

    async def cog_load(self):
        log = logging.getLogger(__name__)
        self.db = await util.db_connection(self.config)
        log.debug("DB Connection online")
        self.storage_channel = list(await util.get_channels(self.bot, self.config['storage_channel']))[0]
        async with self.db.execute('select * from messages where storage_name = "data"') as resp:
            row = await resp.fetchone()
            log.debug(f'storage: {row}')
            if row:
                log.debug('storing data on row')
                storage_name, self.last_updated, self.storage_message = row
            else:
                self.last_updated = None
                message = await self.storage_channel.send(
                    json.dumps({"last_updated": datetime.datetime.now().isoformat()}),
                    file=discord.File(io.StringIO("{}"), filename='data.json'))
                self.storage_message = message.id
                log.info(message)
                await self.db.execute(f'''insert into messages 
                                (storage_name, last_updated, storage_id)
                                values ("data", 0, {self.storage_message})''')
                await self.db.commit()
                assert self.db.total_changes > 0
        log.debug("Got message id from db (or Wrote initial)")
        self.current_data = await self.storage_channel.fetch_message(self.storage_message)
        self.last_updated = datetime.datetime.fromisoformat(json.loads(self.current_data.content)['last_updated'])
        self.json_data = json.loads(await self.current_data.attachments[0].read()) # This is as secure as the discord it saves to
        log.debug("Got current last update/json")
        
        self.gspread = gspread.service_account_from_dict(self.config['google_service_account'])
        self.sheet = naspreadsheet.NAGuildSpreadSheet(self.gspread, self.config['google_spreadsheet_id'])
        log.debug("Connected to Google Sheet!")
        self.check_for_updates.start()


    def added_or_removed(self, new, old, added, removed, alliance=None):
        logging.getLogger("timers.added_or_removed").debug(f"Generating changes {added}/{removed}")
        ret = []
        to_add = new - old
        to_remove = old - new
        for x in list(to_add):
            ret.append(added.format(guild=x, alliance=alliance))
        for x in list(to_remove):
            ret.append(removed.format(guild=x, alliance=alliance))
        return ret

    async def write_update(self, data, now):
        self.last_updated = now
        self.json_data = data
        await self.current_data.edit(
            content=json.dumps({'last_updated': now}),
            attachments=[discord.File(
                io.StringIO(json.dumps(data, indent=2)), 
                filename="data.json")]
        )
        await self.db.execute(f'update messages set last_updated = "{now}", storage_id = {self.storage_message}')
        await self.db.commit()

    @tasks.loop(minutes=5)
    async def check_for_updates(self):
        log = logging.getLogger("timer.UpdateSheet.check_for_updates")
        log.info("Starting Sheet Update")
        now = datetime.datetime.now().isoformat()
        newdata = self.sheet.get_sheet_data()
        if self.json_data == {}:
            await self.write_update(newdata, now)
            return
        changelog = []
        #
        # Determine what alliances are new/gone
        new_alliances = [x['Alliance:'] for x in newdata['Alliances']]
        old_alliances = [x['Alliance:'] for x in self.json_data['Alliances']]
        log.debug(f"{type(new_alliances)} {new_alliances}")
        log.debug(f"{type(old_alliances)} {old_alliances}")
        changelog.extend(self.added_or_removed(
            set(new_alliances),
            set(old_alliances),
            "* New Alliance: {guild}",
            "* Alliance Disbanded: {guild}"
        ))
        log.debug(changelog)
        #
        # Generate Changes for Each Alliance
        if 'Alliances' in self.json_data:
            for n in newdata['Alliances']:
                for o in self.json_data['Alliances']:
                    if n['Alliance:'] != o['Alliance:']: # Confirm on name
                        continue
                    if n != o:
                        logging.debug(f'Changes to {n['Alliance:']} detected')
                        alliance_changes = [f"Changes to {n['Alliance:']}: "]
                        if n['Guilds'] != o['Guilds']:
                            new_guilds = set(n['Guilds'].split('\n'))
                            old_guilds = set(o['Guilds'].split('\n'))
                            alliance_changes.extend(self.added_or_removed(
                                new_guilds,
                                old_guilds,
                                "Joined {alliance}: {guild}",
                                "Left {alliance}: {guild}",
                                alliance = n['Alliance:']
                            ))
                        new_server = [x for x in n.keys() if n[x] == True][0]
                        old_server = [x for x in o.keys() if o[x] == True][0]
                        if new_server != old_server:
                            alliance_changes.append(f"Moved: {bot.config[old_server]} => {bot.config[new_server]}")
                        if len(alliance_changes) == 1:
                            alliance_changes.append(f"(Notes) {n['Notes:']}")
                        changelog.append(f"* {' '.join(alliance_changes)}")
                    break
        log.debug(changelog)
        #
        # Determine Guild Movements
        new_guilds = set([x['Solo Guilds'] for x in newdata['SoloGuilds']])
        old_guilds = set([x['Solo Guilds'] for x in self.json_data['SoloGuilds']])
        changelog.extend(self.added_or_removed(
            new_guilds,
            old_guilds,
            "* New Guild (or Left Alliance): {guild}",
            "* Guild Joined Alliance?: {guild}"
        ))
        log.debug(changelog)
        #
        # Generate Changes for existing guilds
        if 'SoloGuilds' in self.json_data:
            for n in newdata['SoloGuilds']:
                for o in self.json_data['SoloGuilds']:
                    if n['Solo Guilds'] != o['Solo Guilds']: # Confirm on name
                        continue
                    if n != o:
                        logging.debug(f'Changes to {n['Solo Guilds']} detected')
                        new_server = []
                        old_server = []
                        for x in bot.config['servers'].keys():
                            if n[x] == True: new_server = x
                            if o[x] == True: old_server = x
                        if len(new_server) and len(old_server):
                            changelog.append(f"* Changes to {n['Solo Guilds']}: {old_server} => {new_server}")
        
        # Output
        if not changelog:
            log.warning("No Changes")
            return
        elif len(changelog) < 100:
            log.warning("Smallish Changes")
            await self.storage_channel.send('\n'.join(changelog))
            log.debug("Sent")
        else:
            log.warning("Large Changes")
            await self.storage_channel.send("Large Changelog", file=io.StringIO('\n'.join(changelog)))
            log.debug("Sent")
        await self.write_update(newdata, now)
        self.json_data = newdata
        self.last_updated = now
        await self.push_embeds()

    @check_for_updates.before_loop
    async def before_check_for_updates(self):
        logging.info("Waiting to start update check")
        await self.bot.wait_until_ready()
        logging.info("Start update check")

    async def push_embeds(self):
        channels = await util.get_channels(self.bot, self.config['channels'])
        servers = {}
        for channel in channels:
            for abbr, name in self.config['servers'].items():
                msg_embed = embed.make_server_embed(self.json_data, abbr)
                servers[abbr] = {"name": name}
                async with self.db.execute(f"""select * from outputs where 
                                           guild = "{channel.guild.name}" and 
                                           channel = "{channel.name}" and
                                           server = "{abbr}";""") as cur:
                    rows = await cur.fetchall()
                if not len(rows):
                    # Setup the message
                    message = await channel.send(f'# {name} Guild List', 
                                            embeds=msg_embed)
                    await self.db.execute(f"""INSERT INTO outputs 
                                            (guild, channel, server, last_updated, storage_id)
                                            VALUES ('{channel.guild.name}', 
                                            '{channel.name}', 
                                            '{abbr}',
                                            '{self.last_updated}', 
                                            '{message.id}');""")
                    await self.db.commit()
                else:
                    logging.debug(f"row: {rows}")
                    g, c, s, lu, mid = rows[0]
                    message = await channel.fetch_message(mid)
                await message.edit(content=f'# {name} Guild List', embeds=msg_embed)
                await self.db.execute(f"""UPDATE outputs set last_updated = '{self.last_updated}' where storage_id = {mid}""")
                await self.db.commit()
                    