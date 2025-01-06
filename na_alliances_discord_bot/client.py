# import json
import logging

import discord

class AlliancesClient(discord.Client):
    async def on_ready(self):
        self.logger = logging.getLogger(__name__)
        logging.info(f"Logged on as {self.user}")
    
    
        