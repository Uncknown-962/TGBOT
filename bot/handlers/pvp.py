import asyncio
import random
from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from aiogram.utils.keyboard import InlineKeyboardBuilder
from database.database import db

router = Router()

def get_rps_keyboard(bet: int) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(text="🪨 Камень", callback_data=f"rps_rock_{bet}"),
        InlineKeyboardButton(text="✂️ Ножницы", callback_data=f"rps_scissors_{bet}"),
        InlineKeyboardButton(text="📄 Бумага", callback_data=f"rps_paper_{bet}")
    )
    return builder.as_markup()

@router.message(Command("rps"))
async def cmd_rps(message: Message):
    user_id = message.from_user.id
    await db.increment_commands(user_id)
    
    args = message.text.split()
    if len(args) < 2:
        await message.answer("ℹ️ Использование: `/rps <ставка>` (например, /rps 100)", parse_mode="Markdown")
        return
        
    try:
        bet = int(args[1])
    except ValueError:
        await message.answer("❌ Ставка должна быть числом!")
        return
        
    if bet < 10:
        await message.answer("❌ Минимальная ставка — 10 🪙.")
        return
        
    coins = await db.get_user_coins(user_id)
    if coins < bet:
        await message.answer(f"❌ У вас недостаточно монет. Ваш баланс: {coins} 🪙.")
        return
        
    await message.answer(f"⚔️ <b>Игра: Камень-Ножницы-Бумага</b>\nВаша ставка: <b>{bet} 🪙</b>\n\nСделайте свой выбор!", reply_markup=get_rps_keyboard(bet), parse_mode="HTML")

@router.callback_query(F.data.startswith("rps_"))
async def cb_rps(callback: CallbackQuery):
    parts = callback.data.split('_')
    choice = parts[1]
    bet = int(parts[2])
    user_id = callback.from_user.id
    
    coins = await db.get_user_coins(user_id)
    if coins < bet:
        await callback.answer("❌ Недостаточно монет для этой ставки!", show_alert=True)
        return
        
    bot_choice = random.choice(["rock", "scissors", "paper"])
    emojis = {"rock": "🪨 Камень", "scissors": "✂️ Ножницы", "paper": "📄 Бумага"}
    
    await callback.message.edit_text(f"🎲 Вы выбрали: <b>{emojis[choice]}</b>\n🤖 Бот выбирает...", parse_mode="HTML")
    await asyncio.sleep(1.5)
    
    win = False
    draw = False
    
    if choice == bot_choice:
        draw = True
    elif (choice == "rock" and bot_choice == "scissors") or \
         (choice == "scissors" and bot_choice == "paper") or \
         (choice == "paper" and bot_choice == "rock"):
        win = True
        
    text = f"🎲 Вы: <b>{emojis[choice]}</b>\n🤖 Бот: <b>{emojis[bot_choice]}</b>\n\n"
    
    if draw:
        text += "🤝 <b>Ничья!</b> Монеты возвращены."
    elif win:
        await db.update_user_coins(user_id, bet)
        text += f"🎉 <b>Вы победили!</b> Выигрыш: {bet} 🪙!"
    else:
        await db.update_user_coins(user_id, -bet)
        text += f"😢 <b>Вы проиграли</b> {bet} 🪙."
        
    new_coins = await db.get_user_coins(user_id)
    text += f"\n\nВаш баланс: <b>{new_coins} 🪙</b>"
    
    await callback.message.edit_text(text, parse_mode="HTML")
    await callback.answer()
