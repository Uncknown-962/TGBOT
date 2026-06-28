from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message
from datetime import datetime, timezone

from database.database import db
from bot.utils.logger import log

router = Router()


def get_activity_level(total_messages: int) -> tuple[str, int, int]:
    if total_messages <= 10:
        return "🌱 Новичок", total_messages, 11
    elif total_messages <= 50:
        return "🌿 Активный", total_messages - 10, 40
    elif total_messages <= 200:
        return "🌳 Опытный", total_messages - 50, 150
    elif total_messages <= 500:
        return "⭐ Продвинутый", total_messages - 200, 300
    else:
        return "🏆 Легенда", 1, 1


def generate_progress_bar(current: int, total: int, length: int = 10) -> str:
    if total == 1 and current == 1:
        return "🟩" * length
    progress = int((current / total) * length)
    return "🟩" * progress + "⬜" * (length - progress)


@router.message(Command("profile"))
async def cmd_profile(message: Message):
    user_id = message.from_user.id
    await db.increment_commands(user_id)

    user = await db.get_user(user_id)
    stats = await db.get_user_stats(user_id)

    if not user or not stats:
        await message.answer("❌ Профиль не найден")
        return

    days_active = (datetime.now(timezone.utc).replace(tzinfo=None) - user.created_at).days or 1
    level_name, current_xp, required_xp = get_activity_level(stats.total_messages)
    progress_bar = generate_progress_bar(current_xp, required_xp)

    profile_text = f"""
👤 <b>Ваш профиль</b>

<b>Имя:</b> {user.first_name}
<b>ID:</b> <code>{user.id}</code>
<b>Уровень:</b> {level_name}

<b>Прогресс до следующего уровня:</b>
{progress_bar} ({current_xp}/{required_xp})

📅 <b>Дней с ботом:</b> {days_active}
💬 <b>Всего сообщений:</b> {stats.total_messages}
"""

    await message.answer(profile_text, parse_mode="HTML")
    log.info(f"User {user_id} requested profile")


@router.message(F.text == "👤 Профиль")
async def button_profile(message: Message):
    await cmd_profile(message)
