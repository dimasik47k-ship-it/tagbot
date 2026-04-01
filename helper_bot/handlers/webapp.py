import logging
from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.filters import Command

from shared.database import Database

logger = logging.getLogger(__name__)

router = Router()
db = None

def init_service(bot, database: Database):
    global db
    db = database

@router.message(Command("webapp"))
async def cmd_webapp(message: Message):
    """Открыть Mini-App"""
    from shared.config import config
    from helper_bot.keyboards.inline import get_webapp_keyboard
    
    keyboard = get_webapp_keyboard()
    
    await message.answer(
        "📚 Откройте документацию в Mini-App:",
        reply_markup=keyboard
    )


@router.callback_query(F.data == "open_webapp")
async def cb_open_webapp(callback: CallbackQuery):
    """Открыть Mini-App по кнопке"""
    from shared.config import config
    from aiogram.types import WebAppInfo
    
    await callback.answer()
    await callback.message.answer(
        "📚 Документация:",
        reply_markup=get_webapp_keyboard()
    )


@router.callback_query(F.data == "commands")
async def cb_commands(callback: CallbackQuery):
    """Показать команды"""
    text = (
        "⌨️ <b>Все команды</b>\n\n"
        f"<b>В группе:</b>\n"
        f"• /setrang <тег> <ms/dm> — выдать тег\n"
        f"• /delrang — удалить тег\n"
        f"• /delrangid <ID> — удалить по ID\n\n"
        f"<b>Личные:</b>\n"
        f"• /myrang — мой тег\n"
        f"• /checkrang — проверить тег\n"
        f"• /toprang — топ пользователей\n"
        f"• /help — помощь\n"
        f"• /rules — правила\n"
        f"• /license — лицензия"
    )
    
    await callback.message.answer(text, parse_mode="HTML")
    await callback.answer()


@router.callback_query(F.data == "types")
async def cb_types(callback: CallbackQuery):
    """Типы тегов"""
    text = (
        "🎯 <b>Типы тегов</b>\n\n"
        f"<b>📝 MS (Message Style)</b>\n"
        f"• Бот переписывает сообщения\n"
        f"• Красивое оформление\n"
        f"• Видно всем участникам\n\n"
        f"<b>🔒 DM (Direct Message)</b>\n"
        f"• Тег в профиле пользователя\n"
        f"• Сообщения не меняются\n"
        f"• Видно только админам"
    )
    
    await callback.message.answer(text, parse_mode="HTML")
    await callback.answer()


from helper_bot.keyboards.inline import get_webapp_keyboard