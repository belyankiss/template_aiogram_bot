import asyncio

from bot_setting import BotDefault
from log_settings import logger
from settings import settings

bot = BotDefault(settings.BOT_TOKEN)

if __name__ == '__main__':
    try:
        logger.info("Бот запущен успешно!")
        asyncio.run(bot.start())
    except KeyboardInterrupt:
        logger.info("Бот остановлен!")
