import argparse
import json
import logging
import logging.handlers

import na_alliances_discord_bot.client as client

### Configure Logging
logger = logging.getLogger()
logger.setLevel(logging.DEBUG)
logging.getLogger('aiohttp').setLevel(logging.DEBUG)


handler = logging.handlers.RotatingFileHandler(
    filename='discord.log',
    encoding='utf-8',
    maxBytes=32 * 1024 * 1024,  # 32 MiB
    backupCount=5,  # Rotate through 5 files
)
console = logging.StreamHandler()
DT_FMT = '%Y-%m-%d %H:%M:%S'
formatter = logging.Formatter('[{asctime}] [{levelname:<8}] {name}: {message}', DT_FMT, style='{')
console.setFormatter(formatter)
#handler.setFormatter(formatter)
# logger.addHandler(handler)
#logger.addHandler(console)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--config', default='config.json', required=False)
    args = parser.parse_args()
    with open(args.config, 'r', encoding="UTF-8") as fd:
        config = json.load(fd)
    for x in config['info_loggers']:
        logging.getLogger(x).setLevel(logging.INFO)


    client.bot.config = config
    client.bot.run(config['token'], log_handler=console, root_logger=True, log_level=logging.DEBUG)
    logger.warning("Shutting Down")
