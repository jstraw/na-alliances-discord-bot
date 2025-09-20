import json
import logging
import logging.handlers

import client

### Configure Logging
logger = logging.getLogger()
logger.setLevel(logging.DEBUG)
logging.getLogger('discord.http').setLevel(logging.INFO)
logging.getLogger('asyncio').setLevel(logging.INFO)
logging.getLogger('aiohttp').setLevel(logging.DEBUG)

handler = logging.handlers.RotatingFileHandler(
    filename='discord.log',
    encoding='utf-8',
    maxBytes=32 * 1024 * 1024,  # 32 MiB
    backupCount=5,  # Rotate through 5 files
)
console = logging.StreamHandler()
dt_fmt = '%Y-%m-%d %H:%M:%S'
formatter = logging.Formatter('[{asctime}] [{levelname:<8}] {name}: {message}', dt_fmt, style='{')
console.setFormatter(formatter)
handler.setFormatter(formatter)
# logger.addHandler(handler)
logger.addHandler(console)

with open('config.json', 'r') as fd:
    config = json.load(fd)

client.client.config = config
client.client.run(config['token'])
logger.warning("Shutting Down")