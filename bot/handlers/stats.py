from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message
from datetime import datetime, timezone

from database.database import db
from bot.utils.logger import log

router = Router()


@router.message(Command("stats"))
async def cmd_stats(message: Message):
    user_id = message.from_user.id
    await db.increment_commands(user_id)

    user = await db.get_user(user_id)
    stats = await db.get_user_stats(user_id)

    if not user or not stats:
        await message.answer("❌ Статистика не найдена")
        return

    days_active = (datetime.now(timezone.utc).replace(tzinfo=None) - user.created_at).days or 1

    stats_text = f"""
📊 <b>Ваша статистика</b>

👤 <b>Профиль:</b>
• ID: <code>{user.id}</code>
• Имя: {user.first_name}
• Username: @{user.username or 'не указан'}
• Premium: {'✅' if user.is_premium else '❌'}

📈 <b>Активность:</b>
• Всего сообщений: {stats.total_messages}
• Команд выполнено: {stats.total_commands}
• Сообщений в день: {stats.total_messages // days_active}

⏰ <b>Даты:</b>
• Регистрация: {user.created_at.strftime('%d.%m.%Y %H:%M')}
• Последняя активность: {stats.last_activity.strftime('%d.%m.%Y %H:%M')}
• Дней с ботом: {days_active}
"""

    await message.answer(stats_text, parse_mode="HTML")
    log.info(f"User {user_id} requested stats")


@router.message(Command("top"))
async def cmd_top(message: Message):
    user_id = message.chat.id
    await db.increment_commands(user_id)
    
    top_coins = await db.get_top_users_by_coins(5)
    top_xp = await db.get_top_users_by_xp(5)
    
    text = "🏆 <b>Глобальный рейтинг</b>\n\n"
    text += "💰 <b>Богатейшие игроки:</b>\n"
    for idx, u in enumerate(top_coins, 1):
        text += f"{idx}. {u.first_name} — <b>{u.coins} 🪙</b>\n"
        
    text += "\n🌟 <b>Самые активные (Опыт):</b>\n"
    for idx, (u, xp) in enumerate(top_xp, 1):
        text += f"{idx}. {u.first_name} — <b>{xp} XP</b>\n"
        
    await message.answer(text, parse_mode="HTML")
    log.info(f"User {user_id} requested leaderboard")


@router.message(F.text == "📊 Статистика")
async def button_stats(message: Message):
    await cmd_stats(message)
