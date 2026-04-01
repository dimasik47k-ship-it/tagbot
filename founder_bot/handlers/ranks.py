import logging
from aiogram import Router, F
from aiogram.types import Message
from aiogram.filters import Command, CommandObject
from datetime import datetime

from shared.config import config
from shared.database import Database
from founder_bot.services.rank_service import RankService

logger = logging.getLogger(__name__)

router = Router()
rank_service = None

def init_service(bot, db: Database):
    global rank_service
    rank_service = RankService(bot, db)

@router.message(Command("setrang"))
async def cmd_setrang(message: Message, command: CommandObject):
    if message.chat.type == "private":
        return await message.answer("❌ Только в группах.")

    try:
        caller = await message.bot.get_chat_member(message.chat.id, message.from_user.id)
        if caller.status not in ["administrator", "creator"]:
            return await message.answer("🚫 Только администраторы.")
    except Exception:
        return await message.answer("❌ Не удалось проверить права.")

    if not message.reply_to_message:
        return await message.answer("⚠️ Используй команду ответом на сообщение")

    args = message.text.split()
    if len(args) < 2:
        return await message.answer("⚠️ Пример: `/setrang VIP ms`")

    new_rank = args[1].strip()
    tag_type = 'dm'
    
    if len(args) >= 3:
        t = args[2].strip().lower()
        if t in ['ms', 'dm']:
            tag_type = t
        else:
            return await message.answer("⚠️ Тип должен быть ms или dm")

    if len(new_rank) > config.MAX_TAG_LENGTH:
        return await message.answer(f"❌ Тег слишком длинный (макс. {config.MAX_TAG_LENGTH})")

    target_user = message.reply_to_message.from_user

    if target_user.id == message.from_user.id:
        return await message.answer("🚫 Нельзя самому себе.")

    try:
        target_member = await message.bot.get_chat_member(message.chat.id, target_user.id)
        if target_member.status == "creator" and caller.status != "creator":
            return await message.answer("👑 Нельзя владельцу.")
    except Exception:
        pass

    success, response_text = await rank_service.set_rank(
        chat_id=message.chat.id,
        user_id=target_user.id,
        rank=new_rank,
        tag_type=tag_type
    )

    await message.answer(response_text)
    if success:
        logger.info(f"Rank set: {new_rank} ({tag_type}) for {target_user.id}")


@router.message(Command("delrang"))
async def cmd_delrang(message: Message):
    if message.chat.type == "private":
        return await message.answer("❌ Только в группах.")

    try:
        member = await message.bot.get_chat_member(message.chat.id, message.from_user.id)
        if member.status not in ["administrator", "creator"]:
            return await message.answer("🚫 Только администраторы.")
    except Exception:
        return await message.answer("❌ Не удалось проверить права.")

    target_user = None

    if message.reply_to_message:
        target_user = message.reply_to_message.from_user
    elif message.entities:
        for entity in message.entities:
            if entity.type == "text_mention":
                target_user = entity.user
                break

    if not target_user:
        return await message.answer(
            "⚠️ Используй:\n"
            "• /delrang (ответом на сообщение)\n"
            "• /delrang @username (по упоминанию)"
        )

    if target_user.is_bot:
        return await message.answer("🤖 У ботов нет тегов")

    success, response_text = await rank_service.delete_rank(
        chat_id=message.chat.id,
        user_id=target_user.id
    )
    await message.answer(response_text)
    
    if success:
        logger.info(f"Rank deleted for {target_user.id} ({target_user.full_name})")


@router.message(Command("delrangid"))
async def cmd_delrangid(message: Message):
    if message.chat.type == "private":
        return await message.answer("❌ Только в группах.")

    try:
        member = await message.bot.get_chat_member(message.chat.id, message.from_user.id)
        if member.status not in ["administrator", "creator"]:
            return await message.answer("🚫 Только администраторы.")
    except Exception:
        return await message.answer("❌ Не удалось проверить права.")

    args = message.text.split()
    if len(args) < 2:
        return await message.answer("⚠️ Пример: `/delrangid 123456789`")

    try:
        user_id = int(args[1])
    except ValueError:
        return await message.answer("❌ Неверный ID")

    success, response_text = await rank_service.delete_rank(
        chat_id=message.chat.id,
        user_id=user_id
    )
    await message.answer(response_text)


@router.message(Command("myrang"))
async def cmd_myrang(message: Message):
    try:
        rank_data = await rank_service.get_rank(message.chat.id, message.from_user.id)
        if rank_data and rank_data['rank']:
            await message.answer(
                f"🏷 <b>Твой ранг:</b> [{rank_data['rank']}]\n"
                f"📌 <b>Тип:</b> {rank_data['tag_type'].upper()}\n"
                f"💡 {'Виден всем (бот переписывает сообщения)' if rank_data['tag_type'] == 'ms' else 'Виден только админам'}",
                parse_mode="HTML"
            )
        else:
            await message.answer("🏷 Ранг не установлен")
    except Exception as e:
        logger.error(f"Error: {e}")
        await message.answer("❌ Ошибка")


@router.message(Command("checkrang"))
async def cmd_checkrang(message: Message):
    if message.chat.type == "private":
        return await message.answer("❌ Только в группах.")

    target_user = None
    if message.reply_to_message:
        target_user = message.reply_to_message.from_user

    if not target_user:
        return await message.answer("⚠️ Ответьте на сообщение")

    try:
        rank_data = await rank_service.get_rank(message.chat.id, target_user.id)
        name = target_user.full_name
        if rank_data and rank_data['rank']:
            await message.answer(
                f"🏷 <b>{name}:</b>\n"
                f"Ранг: [{rank_data['rank']}]\n"
                f"Тип: {rank_data['tag_type'].upper()}",
                parse_mode="HTML"
            )
        else:
            await message.answer(f"🏷 <b>{name}:</b> нет ранга", parse_mode="HTML")
    except Exception:
        await message.answer("❌ Ошибка")


@router.message(Command("toprang"))
async def cmd_toprang(message: Message):
    try:
        top_users = await rank_service.get_top_ranks(message.chat.id, limit=10)
        if not top_users:
            return await message.answer("📊 Нет рангов")
        
        text = "🏆 <b>Топ:</b>\n\n"
        for i, user in enumerate(top_users, 1):
            try:
                member = await message.bot.get_chat_member(message.chat.id, user['user_id'])
                name = member.user.full_name
                tag_type = user.get('tag_type', 'dm').upper()
                text += f"{i}. <b>{name}</b> — [{user['rank']}] ({tag_type})\n"
            except:
                text += f"{i}. User {user['user_id']} — [{user['rank']}]\n"
        
        await message.answer(text, parse_mode="HTML")
    except Exception as e:
        logger.error(f"Error: {e}")
        await message.answer("❌ Ошибка")


@router.message()
async def handle_ms_tags(message: Message):
    """Переписывает сообщения пользователей с MS тегом"""
    if message.chat.type == "private":
        return

    if message.text and message.text.startswith('/'):
        return

    try:
        rank_data = await rank_service.get_rank(message.chat.id, message.from_user.id)
        
        if rank_data and rank_data['rank'] and rank_data['tag_type'] == 'ms':
            name = message.from_user.full_name
            username = message.from_user.username
            user_id = message.from_user.id
            date = datetime.now().strftime("%d.%m.%Y %H:%M")
            bot_username = (await message.bot.get_me()).username
            text = message.text or message.caption or ""
            
            formatted_text = rank_service.format_ms_message(
                rank=rank_data['rank'],
                name=name,
                username=username,
                user_id=user_id,
                date=date,
                text=text,
                bot_username=bot_username
            )
            
            if message.photo:
                await message.delete()
                await message.answer_photo(photo=message.photo[-1].file_id, caption=formatted_text, parse_mode="HTML")
            elif message.video:
                await message.delete()
                await message.answer_video(video=message.video.file_id, caption=formatted_text, parse_mode="HTML")
            elif message.document:
                await message.delete()
                await message.answer_document(document=message.document.file_id, caption=formatted_text, parse_mode="HTML")
            elif message.audio:
                await message.delete()
                await message.answer_audio(audio=message.audio.file_id, caption=formatted_text, parse_mode="HTML")
            elif message.voice:
                await message.delete()
                await message.answer_voice(voice=message.voice.file_id, caption=formatted_text, parse_mode="HTML")
            elif message.animation:
                await message.delete()
                await message.answer_animation(animation=message.animation.file_id, caption=formatted_text, parse_mode="HTML")
            elif message.sticker:
                await message.delete()
                await message.answer_sticker(sticker=message.sticker.file_id)
            elif message.video_note:
                await message.delete()
                await message.answer_video_note(video_note=message.video_note.file_id)
            elif message.text:
                await message.delete()
                await message.answer(text=formatted_text, parse_mode="HTML")
            else:
                await message.delete()
                
    except Exception as e:
        logger.error(f"Error in handle_ms_tags: {e}")