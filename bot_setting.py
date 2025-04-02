import asyncio
from typing import Literal

from aiohttp import web
from loguru import logger

from aiogram import Bot, Dispatcher, Router, BaseMiddleware
from aiogram.client.default import DefaultBotProperties
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.webhook.aiohttp_server import SimpleRequestHandler, setup_application

from exceptions import WebhookError
from log_settings import set_log
from webhook_settings import Webhook



class BotDefault:
    def __init__(
            self,
            token: str,
            logging: bool = True,
            storage=None
    ) -> None:

        self.bot = Bot(token=token, default=DefaultBotProperties(parse_mode="HTML"))
        self.dispatcher = Dispatcher(storage=storage or MemoryStorage())

        if logging:
            set_log()

    def add_router(self, *routers: Router) -> None:
        """
        Метод добавления роутеров.
        :param routers: *Router
        :return: None
        """
        self.dispatcher.include_routers(*routers)

    async def delete_webhook(self) -> None:
        """
        Удаление старых updates
        :return: None
        """
        await self.bot.delete_webhook(drop_pending_updates=True)

    async def add_middleware(
            self,
            middleware: BaseMiddleware,
            message: bool = True,
            callback_query: bool = True
    ) -> None:
        """
        Добавление middlewares.
        :param middleware: BaseMiddleware
        :param message: bool - middleware будет работать на сообщениях
        :param callback_query: bool - middleware будет работать на callback
        :return: None
        """
        if message:
            self.dispatcher.message.middleware(middleware)
        if callback_query:
            self.dispatcher.callback_query.middleware(middleware)

    async def _long_polling(self, delete_webhook: bool = True):
        """
        Запуск бота в режиме long polling
        :param delete_webhook:
        :return:
        """
        try:
            if delete_webhook:
                await self.delete_webhook()
            logger.info("Бот запущен в режиме long polling")
            await self.dispatcher.start_polling(self.bot)
        finally:
            await self.bot.session.close()

    async def _webhook(self, webhook: Webhook):
        """
        Запуск бота в режиме webhook.
        :return:
        """
        webhook_info = await self.bot.get_webhook_info()

        if webhook_info.url != webhook.url:
            await self.bot.set_webhook(url=webhook.url)
            logger.info(f"Webhook установлен на {webhook.url}")
        else:
            logger.info("Webhook уже установлен")

        app = web.Application()

        webhook_handler = SimpleRequestHandler(
            dispatcher=self.dispatcher,
            bot=self.bot
        )
        webhook_handler.register(app, path=webhook.path)
        setup_application(app, self.dispatcher, bot=self.bot)

        runner = web.AppRunner(app)
        await runner.setup()

        try:
            site = web.TCPSite(runner, host="0.0.0.0", port=webhook.port)
            logger.info("Бот запущен в режиме webhook.")
            await site.start()
            await asyncio.Event().wait()  # Ожидаем завершения
        except Exception as e:
            logger.error(f"{e}")
        finally:
            await self._shutdown_webhook()

    async def _shutdown_webhook(self):
        try:
            webhook_info = await self.bot.get_webhook_info()
            if webhook_info.url:
                await self.bot.delete_webhook()
                logger.info("Webhook удален")
        except Exception as e:
            logger.error(f"Ошибка при удалении webhook: {e}")

    async def start(
            self,
            regime: Literal["long_polling", "webhook"] = "long_polling",
            delete_webhook: bool = True,
            webhook: Webhook = None
    ) -> None:
        """
        Запуск бота!
        :param regime: Literal - выбор режима для запуска бота. По умолчанию long polling
        :param delete_webhook: bool - вызывает метод удаления старых updates
        :param webhook: Webhook - параметры настройки webhook
        :return: None
        """
        if regime == "long_polling":
            await self._long_polling(delete_webhook)
        else:
            if not webhook:
                raise WebhookError("Не передан параметр webhook -> Webhook()")
            await self._webhook(webhook)
