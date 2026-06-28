import asyncio
from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder

from database.database import db

router = Router()


def get_casino_keyboard() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(text="🎰 Крутить слоты (10 🪙)", callback_data="play_slots")
    )
    builder.row(
        InlineKeyboardButton(text="🎲 Кинуть кубик (20 🪙)", callback_data="play_dice")
    )
    return builder.as_markup()


@router.message(Command("games", "casino", "dice"))
async def cmd_games(message: Message):
    user_id = message.from_user.id
    await db.increment_commands(user_id)
    coins = await db.get_user_coins(user_id)
    
    text = f"""
🎰 <b>Добро пожаловать в Казино!</b> 🎲

Ваш баланс: <b>{coins} 🪙</b>

Выберите игру:
"""
    await message.answer(text, reply_markup=get_casino_keyboard(), parse_mode="HTML")


@router.message(F.text == "🎲 Игры")
async def button_games(message: Message):
    await cmd_games(message)


@router.callback_query(F.data == "play_slots")
async def play_slots(callback: CallbackQuery):
    user_id = callback.from_user.id
    coins = await db.get_user_coins(user_id)
    
    if coins < 10:
        await callback.answer("❌ Недостаточно монет! Нужно 10 🪙", show_alert=True)
        return
    
    await db.update_user_coins(user_id, -10)
    
    msg = await callback.message.answer_dice(emoji="🎰")
    await callback.answer()
    
    # Wait for the slot animation to finish
    await asyncio.sleep(2.5)
    
    val = msg.dice.value
    win_amount = 0
    
    if val == 64:
        win_amount = 500
        text = "🎉 ДЖЕКПОТ! 777! Вы выиграли 500 🪙!"
    elif val in (1, 22, 43):
        win_amount = 50
        text = "🎊 Три в ряд! Вы выиграли 50 🪙!"
    else:
        text = "😢 Вы ничего не выиграли."
    
    if win_amount > 0:
        await db.update_user_coins(user_id, win_amount)
    
    new_coins = await db.get_user_coins(user_id)
    await callback.message.answer(f"{text}\n\nВаш баланс: <b>{new_coins} 🪙</b>", reply_markup=get_casino_keyboard(), parse_mode="HTML")


@router.callback_query(F.data == "play_dice")
async def play_dice(callback: CallbackQuery):
    user_id = callback.from_user.id
    coins = await db.get_user_coins(user_id)
    
    if coins < 20:
        await callback.answer("❌ Недостаточно монет! Нужно 20 🪙", show_alert=True)
        return
        
    await db.update_user_coins(user_id, -20)
    
    msg = await callback.message.answer_dice(emoji="🎲")
    await callback.answer()
    
    # Wait for the dice animation to finish
    await asyncio.sleep(4)
    val = msg.dice.value
    
    win_amount = 0
    if val == 6:
        win_amount = 100
        text = "🎯 Выпало 6! Вы выиграли 100 🪙!"
    elif val == 5:
        win_amount = 40
        text = "👍 Выпало 5! Вы выиграли 40 🪙!"
    else:
        text = f"🎲 Выпало {val}. Вы проиграли."
        
    if win_amount > 0:
        await db.update_user_coins(user_id, win_amount)
        
    new_coins = await db.get_user_coins(user_id)
    await callback.message.answer(f"{text}\n\nВаш баланс: <b>{new_coins} 🪙</b>", reply_markup=get_casino_keyboard(), parse_mode="HTML")
