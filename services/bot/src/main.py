import asyncio
import logging

from aiogram import Bot, Dispatcher

from src.config import config
from src.handlers.reputation.reputation import router


async def main():
    logging.basicConfig(level=logging.INFO)

    bot = Bot(token=config.BOT_TOKEN.get_secret_value())
    dispatcher = Dispatcher()
    dispatcher.include_router(router)

    await bot.delete_webhook(drop_pending_updates=True)
    await dispatcher.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
