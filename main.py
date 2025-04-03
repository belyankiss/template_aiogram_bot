import asyncio

from aiogram_sender.middleware import WindowMiddleware
from bot_setting import BotDefault
from database.databases import AioSQLiteDatabase
from handlers.start import start

from log_settings import logger
from middlewares.session_middleware import SessionMiddleware
from settings import settings

database = AioSQLiteDatabase(db_path=settings.NAME_DATABASE)

bot = BotDefault(settings.BOT_TOKEN)

bot.add_middleware(SessionMiddleware(database))
bot.add_middleware(WindowMiddleware())
bot.add_router(start)

async def main(create_database: bool):
    if create_database:
        await database.build_db(is_delete=True)
    try:
        await bot.start()
    finally:
        await database.shutdown()


if __name__ == '__main__':
    try:
        logger.info("Бот запущен успешно!")
        asyncio.run(main(True))
    except KeyboardInterrupt:
        logger.info("Бот остановлен!")
