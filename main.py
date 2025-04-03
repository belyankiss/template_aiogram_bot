import asyncio

from aiogram_sender.middleware import WindowMiddleware
from bot_setting import BotDefault
from database.connection import Database
from handlers.start import start

from log_settings import logger
from middlewares.session_middleware import SessionMiddleware
from settings import settings

database = Database(db_type="aiosqlite", create_database=True)

bot = BotDefault(settings.BOT_TOKEN)

bot.add_middleware(SessionMiddleware(database))
bot.add_middleware(WindowMiddleware())
bot.add_router(start)

if __name__ == '__main__':
    try:
        logger.info("Бот запущен успешно!")
        asyncio.run(database.create_tables(is_delete=True))
        asyncio.run(bot.start())
    except KeyboardInterrupt:
        logger.info("Бот остановлен!")
