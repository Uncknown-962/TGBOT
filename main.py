import asyncio
import sys
from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode

from config.settings import settings
from database.database import db
from bot.handlers import setup_routers
from bot.middlewares.database import DatabaseMiddleware
from bot.middlewares.admin import AdminMiddleware
from bot.middlewares.throttling import ThrottlingMiddleware
from bot.utils.logger import log


async def on_startup(bot: Bot):
    log.info("Bot is starting...")

    try:
        await db.create_tables()
        log.info("Database tables created successfully")
    except Exception as e:
        log.error(f"Failed to create database tables: {e}")
        sys.exit(1)

    bot_info = await bot.get_me()
    log.info(f"Bot started: @{bot_info.username}")

    for admin_id in settings.ADMIN_IDS:
        try:
            await bot.send_message(
                admin_id,
                "🤖 <b>Бот запущен!</b>\n\nВсе системы работают нормально.",
                parse_mode=ParseMode.HTML
            )
        except Exception as e:
            log.warning(f"Failed to notify admin {admin_id}: {e}")


async def on_shutdown(bot: Bot):
    log.info("Bot is shutting down...")

    for admin_id in settings.ADMIN_IDS:
        try:
            await bot.send_message(
                admin_id,
                "🛑 <b>Бот остановлен</b>",
                parse_mode=ParseMode.HTML
            )
        except Exception:
            pass

    log.info("Bot stopped")


async def main():
    try:
        settings.validate()
    except ValueError as e:
        log.error(f"Configuration error: {e}")
        sys.exit(1)

    bot = Bot(
        token=settings.BOT_TOKEN,
        default=DefaultBotProperties(parse_mode=ParseMode.HTML)
    )

    dp = Dispatcher()

    dp.message.middleware(DatabaseMiddleware())
    dp.callback_query.middleware(DatabaseMiddleware())

    dp.message.middleware(AdminMiddleware())
    dp.callback_query.middleware(AdminMiddleware())

    dp.message.middleware(ThrottlingMiddleware(rate_limit=1.0))
    dp.callback_query.middleware(ThrottlingMiddleware(rate_limit=1.0))

    router = setup_routers()
    dp.include_router(router)

    dp.startup.register(on_startup)
    dp.shutdown.register(on_shutdown)

     try:
        # Фоновая задача, которая пингует сервер каждые 10 минут и не дает ему уснуть
        async def keep_alive():
            import aiohttp
            # ВНИМАНИЕ: Замените URL ниже на реальную ссылку вашего бота из панели Render!
            # Она находится в левом верхнем углу страницы Render (выглядит как https://...onrender.com)
            url = "https://tgbot-ikbm.onrender.com" 
            
            await asyncio.sleep(30) # Небольшая пауза при самом первом запуске
            while True:
                try:
                    async with aiohttp.ClientSession() as session:
                        async with session.get(url) as resp:
                            log.debug(f"Keep-alive ping sent to {url}, status: {resp.status}")
                except Exception as e:
                    log.warning(f"Keep-alive ping failed: {e}")
                await asyncio.sleep(600) # Повторяем каждые 10 минут (600 секунд)

        # Запускаем пинговалку в фоне
        asyncio.create_task(keep_alive())

        log.info("Starting polling...")
        await dp.start_polling(bot, allowed_updates=dp.resolve_used_update_types())
    except Exception as e:
        log.error(f"Critical error: {e}")
        raise
    finally:
        await bot.session.close()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        log.info("Bot stopped by user")
    except Exception as e:
        log.critical(f"Fatal error: {e}")
        sys.exit(1)
