import random
from datetime import datetime, timezone, timedelta
from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message
from database.database import db

router = Router()

@router.message(Command("bonus"))
async def cmd_bonus(message: Message):
    user_id = message.from_user.id
    await db.increment_commands(user_id)
    
    user = await db.get_user(user_id)
    now = datetime.now(timezone.utc).replace(tzinfo=None)
    
    if user.last_bonus:
        time_diff = now - user.last_bonus
        if time_diff < timedelta(hours=24):
            remaining = timedelta(hours=24) - time_diff
            hours, remainder = divmod(remaining.seconds, 3600)
            minutes, _ = divmod(remainder, 60)
            await message.answer(f"⏳ Следующий бонус будет доступен через <b>{hours}ч {minutes}м</b>.", parse_mode="HTML")
            return
            
    amount = random.randint(50, 200)
    if user.is_premium:
        amount *= 2
        
    await db.claim_bonus(user_id, amount, now)
    new_coins = await db.get_user_coins(user_id)
    
    text = f"🎁 Вы получили ежедневный бонус: <b>{amount} 🪙</b>!\n"
    if user.is_premium:
        text += "<i>(Бонус удвоен благодаря VIP статусу)</i>\n"
    text += f"\nВаш баланс: <b>{new_coins} 🪙</b>"
    
    await message.answer(text, parse_mode="HTML")
