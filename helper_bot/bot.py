import asyncio
import logging
from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.types import MenuButtonWebApp, WebAppInfo

from shared.config import config
from shared.database import Database
from helper_bot.handlers import start, webapp

logging.basicConfig(level=logging.INFO)

async def main():
    db = Database(config.DATABASE_URL)
    await db.connect()
    
    bot = Bot(
        token=config.HELPER_TOKEN,
        default=DefaultBotProperties(parse_mode=ParseMode.HTML)
    )
    
    # Гамбургер меню с Mini-App
    await bot.set_chat_menu_button(
        menu_button=MenuButtonWebApp(
            text="📚 Документация",
            web_app=WebAppInfo(url=config.WEBAPP_URL)
        )
    )
    
    dp = Dispatcher()
    
    start.init_service(bot, db)
    webapp.init_service(bot, db)
    
    dp.include_router(start.router)
    dp.include_router(webapp.router)
    
    print("📚 Helper Bot started (LS + Mini-App)")
    
    try:
        await dp.start_polling(bot)
    finally:
        await bot.session.close()
        await db.disconnect()

if __name__ == "__main__":
    asyncio.run(main())