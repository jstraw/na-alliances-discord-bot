import argparse
import json
import logging
import logging.handlers

import client

global configs
### Configure Logging
logger = logging.getLogger()
logger.setLevel(logging.DEBUG)
logging.getLogger('discord.http').setLevel(logging.INFO)
logging.getLogger('asyncio').setLevel(logging.INFO)
logging.getLogger('aiohttp').setLevel(logging.DEBUG)
logging.getLogger('aiosqlite').setLevel(logging.INFO)
logging.getLogger('na_alliances_discord_bot.naspreadsheet').setLevel(logging.INFO)

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


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--config', default='config.json', required=False)
    args = parser.parse_args()
    with open(args.config, 'r') as fd:
        config = json.load(fd)

    
    client.bot.config = config
    client.bot.run(config['token'])
    logger.warning("Shutting Down")