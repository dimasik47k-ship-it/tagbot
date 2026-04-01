import asyncio
import logging
from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode

from shared.config import config
from shared.database import Database
from founder_bot.handlers import ranks

logging.basicConfig(level=logging.INFO)

async def main():
    db = Database(config.DATABASE_URL)
    await db.connect()
    
    bot = Bot(
        token=config.FOUNDER_TOKEN,
        default=DefaultBotProperties(parse_mode=ParseMode.HTML)
    )
    
    dp = Dispatcher()
    ranks.init_service(bot, db)
    dp.include_router(ranks.router)
    
    print("🏷 Founder Bot started (Groups only)")
    
    try:
        await dp.start_polling(bot)
    finally:
        await bot.session.close()
        await db.disconnect()

if __name__ == "__main__":
    asyncio.run(main())