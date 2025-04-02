import asyncio

from bot_setting import BotDefault
from database.connection import Database, create_database
from handlers.start import start

from log_settings import logger
from middlewares.session_middleware import SessionMiddleware
from settings import settings

database = Database(db_type="aiosqlite")

bot = BotDefault(settings.BOT_TOKEN)

bot.add_middleware(SessionMiddleware(database))
bot.add_router(start)

if __name__ == '__main__':
    try:
        logger.info("Бот запущен успешно!")
        asyncio.run(create_database())
        asyncio.run(bot.start())
    except KeyboardInterrupt:
        logger.info("Бот остановлен!")
