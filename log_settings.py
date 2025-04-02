import logging
from loguru import logger

class InterceptHandler(logging.Handler):
    def emit(self, record):
        # Перенаправляем в loguru
        logger_opt = logger.opt(depth=6, exception=record.exc_info)
        logger_opt.log(record.levelno, record.getMessage())

def set_log():
    # Настраиваем логирование
    logging.basicConfig(handlers=[InterceptHandler()], level=logging.INFO)

    # Перенаправляем aiogram-логгеры в Loguru
    for logger_name in (["aiogram.dispatcher"]):
        logging.getLogger(logger_name).handlers = [InterceptHandler()]

    logger.remove()  # Удаляем дефолтный handler
    logger.add("errors.log", level="ERROR", format="{time} {level} {message}", rotation="1 day")
    logger.add(lambda msg: print(msg, end=""), colorize=True, format="<green>{time}</green> | <level>{level}</level> | <cyan>{message}</cyan>")
