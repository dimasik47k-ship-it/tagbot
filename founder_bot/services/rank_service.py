import logging
from typing import Optional, Dict
from aiogram import Bot
from aiogram.exceptions import TelegramBadRequest
from shared.database import Database
from datetime import datetime

logger = logging.getLogger(__name__)

class RankService:
    def __init__(self, bot: Bot, db: Database):
        self.bot = bot
        self.db = db

    async def set_rank(self, chat_id: int, user_id: int, rank: str, tag_type: str = 'dm') -> tuple[bool, str]:
        try:
            # Сохраняем в БД
            await self.db.set_rank(chat_id, user_id, rank, tag_type)
            
            # Если DM — ставим тег через Telegram API
            if tag_type == 'dm':
                try:
                    await self.bot.set_chat_member_tag(
                        chat_id=chat_id,
                        user_id=user_id,
                        tag=rank
                    )
                except TelegramBadRequest as e:
                    logger.warning(f"Failed to set DM tag: {e}")
            
            return True, f"✅ Ранг [{rank}] тип [{tag_type.upper()}] установлен!"
        except Exception as e:
            logger.exception(f"Error in set_rank: {e}")
            return False, f"❌ Ошибка: {e}"

    async def get_rank(self, chat_id: int, user_id: int) -> Optional[Dict]:
        return await self.db.get_rank(chat_id, user_id)

    async def delete_rank(self, chat_id: int, user_id: int) -> tuple[bool, str]:
        try:
            rank_data = await self.db.get_rank(chat_id, user_id)
            await self.db.delete_rank(chat_id, user_id)
            
            if rank_data and rank_data.get('tag_type') == 'dm':
                try:
                    await self.bot.set_chat_member_tag(
                        chat_id=chat_id,
                        user_id=user_id,
                        tag=""
                    )
                except:
                    pass
            return True, "✅ Ранг удалён!"
        except Exception as e:
            logger.exception(f"Error in delete_rank: {e}")
            return False, f"❌ Ошибка: {e}"

    async def get_top_ranks(self, chat_id: int, limit: int = 10) -> list:
        return await self.db.get_top_ranks(chat_id, limit)

    def format_ms_message(self, rank: str, name: str, username: str, user_id: int, date: str, text: str, bot_username: str) -> str:
        """Красивое оформление сообщения"""
        emojis = {'VIP': '💎', 'Admin': '🛡️', 'Owner': '👑', 'Mod': '⚡'}
        emoji = emojis.get(rank, '🔖')
        
        user_tag = f"@{username}" if username else "—"
        bot_tag = f"@{bot_username}" if bot_username else ""
        
        info_box = (
            f"╭─ 📌 User Info ─────────────────╮\n"
            f"│ 👤 <b>Name:</b>        {name}\n"
            f"│ 🔖 <b>Username:</b>    {user_tag}\n"
            f"│ 🆔 <b>ID:</b>          <code>{user_id}</code>\n"
            f"│ 🏷 <b>Tag:</b>         {emoji} <b>{rank}</b>\n"
            f"│ 📅 <b>Date:</b>        {date}\n"
            f"╰───────────────────────────────╯"
        )
        
        message_box = (
            f"\n💬 <b>Message:</b>\n"
            f"┌───────────────────────────────┐\n"
            f"{self._wrap_text(text)}\n"
            f"└───────────────────────────────┘"
        )
        
        footer = f"\n<b>— By {bot_tag}</b>" if bot_tag else ""
        
        return info_box + message_box + footer

    def _wrap_text(self, text: str, max_width: int = 30) -> str:
        if not text:
            return "│ <i>Нет текста</i>"
        
        lines = []
        for line in text.split('\n'):
            if len(line) <= max_width:
                lines.append(f"│ {line}")
            else:
                for i in range(0, len(line), max_width):
                    chunk = line[i:i+max_width]
                    lines.append(f"│ {chunk}")
        
        return '\n'.join(lines) if lines else "│ <i>Пусто</i>"