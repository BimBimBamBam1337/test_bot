from dotenv import load_dotenv

load_dotenv()

import os
import asyncio

from loguru import logger

fro


async def on_startup():
    from telegram.handlers import routers
    from telegram.middlewares import UserMiddleware

    middleware = UserMiddleware()
    dp.message.outer_middleware(middleware)
    dp.callback_query.outer_middleware(middleware)

    dp.include_routers(*routers)
    scheduler.start()
    bot_info = await bot.get_me()
    logger.info(f"Bot @{bot_info.username} [{bot_info.id}] is started")


async def on_shutdown():
    logger.info("Bot stopped")
    await bot.session.close()


async def main():
    try:
        await on_startup()
        await dp.start_polling(bot)
    except Exception as e:
        logger.critical(e)
    finally:
        await on_shutdown()


if __name__ == "__main__":
    import asyncio

    asyncio.run(main())
