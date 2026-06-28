from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message
from database.database import db

router = Router()

@router.message(Command("shop"))
async def cmd_shop(message: Message):
    user_id = message.from_user.id
    await db.increment_commands(user_id)
    
    coins = await db.get_user_coins(user_id)
    text = f"""
🛒 <b>Магазин</b>

Ваш баланс: <b>{coins} 🪙</b>

1️⃣ <b>VIP-статус (💎)</b> — 5000 🪙
<i>Удваивает ежедневный бонус и опыт!</i>
Купить: `/buy vip`

2️⃣ <b>Кастомный Титул (🏷)</b> — 1000 🪙
<i>Отображается в вашем профиле!</i>
Купить: `/buy title <ваш_титул>`
"""
    await message.answer(text, parse_mode="HTML")

@router.message(Command("buy"))
async def cmd_buy(message: Message):
    user_id = message.from_user.id
    await db.increment_commands(user_id)
    
    args = message.text.split(maxsplit=2)
    if len(args) < 2:
        await message.answer("❌ Используйте `/buy vip` или `/buy title <название>`", parse_mode="Markdown")
        return
        
    item = args[1].lower()
    user = await db.get_user(user_id)
    
    if item == "vip":
        if user.is_premium:
            await message.answer("❌ У вас уже есть VIP-статус!")
            return
        if user.coins < 5000:
            await message.answer("❌ Недостаточно монет! Нужно 5000 🪙.")
            return
            
        await db.update_user_coins(user_id, -5000)
        await db.set_user_vip(user_id, True)
        await message.answer("💎 Поздравляем! Вы приобрели <b>VIP-статус</b>!", parse_mode="HTML")
        
    elif item == "title":
        if len(args) < 3:
            await message.answer("❌ Укажите название титула: `/buy title <название>`", parse_mode="Markdown")
            return
            
        title = args[2][:30]
        if user.coins < 1000:
            await message.answer("❌ Недостаточно монет! Нужно 1000 🪙.")
            return
            
        await db.update_user_coins(user_id, -1000)
        await db.set_user_title(user_id, title)
        await message.answer(f"🏷 Вы успешно купили титул: <b>{title}</b>", parse_mode="HTML")
    else:
        await message.answer("❌ Товар не найден. Смотрите /shop.")
