from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, WebAppInfo
from shared.config import config

def get_start_keyboard() -> InlineKeyboardMarkup:
    """Клавиатура для /start"""
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(
            text="📚 Открыть документацию",
            web_app=WebAppInfo(url=config.WEBAPP_URL)
        )],
        [
            InlineKeyboardButton(text="⌨️ Команды", callback_data="commands"),
            InlineKeyboardButton(text="🎯 Типы тегов", callback_data="types")
        ],
        [
            InlineKeyboardButton(text="📜 Правила", callback_data="rules"),
            InlineKeyboardButton(text="📄 Лицензия", callback_data="license")
        ]
    ])
    return keyboard


def get_webapp_keyboard() -> InlineKeyboardMarkup:
    """Клавиатура для Mini-App"""
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(
            text="📖 Открыть документацию",
            web_app=WebAppInfo(url=config.WEBAPP_URL)
        )]
    ])
    return keyboard


def get_help_keyboard() -> InlineKeyboardMarkup:
    """Клавиатура помощи"""
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="⌨️ Команды", callback_data="commands"),
            InlineKeyboardButton(text="🎯 Типы", callback_data="types")
        ],
        [
            InlineKeyboardButton(text="📜 Правила", callback_data="rules"),
            InlineKeyboardButton(text="📄 Лицензия", callback_data="license")
        ]
    ])
    return keyboard