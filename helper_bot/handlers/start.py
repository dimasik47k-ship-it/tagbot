import logging
from aiogram import Router, F
from aiogram.types import Message, WebAppInfo
from aiogram.filters import Command

from shared.database import Database

logger = logging.getLogger(__name__)

router = Router()
db = None
bot = None

def init_service(bot_obj, database: Database):
    global db, bot
    db = database
    bot = bot_obj

@router.message(Command("start"))
async def cmd_start(message: Message):
    """Приветственное сообщение с Mini-App"""
    await db.save_user(
        user_id=message.from_user.id,
        username=message.from_user.username,
        full_name=message.from_user.full_name
    )
    
    text = (
        f"👋 Привет, {message.from_user.full_name}!\n\n"
        f"Я — помощник Tag Editor.\n\n"
        f"Здесь вы найдёте:\n"
        f"• 📖 Полную документацию\n"
        f"• ⌨️ Список команд\n"
        f"• 📜 Условия использования\n\n"
        f"Нажмите кнопку ниже, чтобы открыть документацию."
    )
    
    from helper_bot.keyboards.inline import get_start_keyboard
    keyboard = get_start_keyboard()
    
    await message.answer(text, reply_markup=keyboard)


@router.message(Command("help"))
async def cmd_help(message: Message):
    """Помощь"""
    text = (
        "📖 <b>Помощь</b>\n\n"
        f"<b>Основной бот:</b> @GXTag_bot\n"
        f"<b>Бот помощи:</b> @{(await bot.get_me()).username}\n\n"
        f"<b>Команды основного бота:</b>\n"
        f"• /setrang — выдать тег\n"
        f"• /delrang — удалить тег\n"
        f"• /myrang — мой тег\n"
        f"• /checkrang — проверить тег\n"
        f"• /toprang — топ пользователей\n\n"
        f"Откройте Mini-App для полной документации."
    )
    
    from helper_bot.keyboards.inline import get_start_keyboard
    keyboard = get_start_keyboard()
    
    await message.answer(text, reply_markup=keyboard, parse_mode="HTML")


@router.message(Command("rules"))
async def cmd_rules(message: Message):
    """Правила"""
    text = (
        "📜 <b>Правила использования</b>\n\n"
        f"1. Бот предназначен для управления тегами в группах.\n"
        f"2. Только администраторы могут выдавать теги.\n"
        f"3. Запрещено выдавать оскорбительные теги.\n"
        f"4. Бот может удалять сообщения пользователей с MS тегом.\n"
        f"5. Используя бота, вы соглашаетесь с условиями.\n\n"
        f"<b>Нарушение правил может привести к блокировке.</b>"
    )
    
    await message.answer(text, parse_mode="HTML")


@router.message(Command("license"))
async def cmd_license(message: Message):
    """Лицензия"""
    text = (
        "📄 <b>Лицензионное соглашение</b>\n\n"
        f"© 2026 Tag Editor. Все права защищены.\n\n"
        f"1. Бот предоставляется «как есть».\n"
        f"2. Разработчики не несут ответственности за ущерб.\n"
        f"3. Запрещено обратное проектирование кода.\n"
        f"4. Коммерческое использование требует согласия.\n\n"
        f"<b>Используя бота, вы принимаете эти условия.</b>"
    )
    
    await message.answer(text, parse_mode="HTML")