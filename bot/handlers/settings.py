from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message, CallbackQuery

from bot.keyboards.inline import get_settings_keyboard, get_language_keyboard
from database.database import db

router = Router()


@router.message(Command("settings"))
async def cmd_settings(message: Message):
    await db.increment_commands(message.from_user.id)

    settings_text = """
⚙️ <b>Настройки</b>

Выберите, что хотите настроить:
"""

    await message.answer(
        settings_text,
        parse_mode="HTML",
        reply_markup=get_settings_keyboard()
    )


@router.message(F.text == "⚙️ Настройки")
async def button_settings(message: Message):
    await cmd_settings(message)


@router.callback_query(F.data == "settings_menu")
async def callback_settings_menu(callback: CallbackQuery):
    await callback.message.edit_text(
        "⚙️ <b>Настройки</b>\n\nВыберите, что хотите настроить:",
        parse_mode="HTML",
        reply_markup=get_settings_keyboard()
    )
    await callback.answer()


@router.callback_query(F.data == "settings_language")
async def callback_language(callback: CallbackQuery):
    await callback.message.edit_text(
        "🌐 <b>Выбор языка</b>\n\nВыберите язык интерфейса:",
        parse_mode="HTML",
        reply_markup=get_language_keyboard()
    )
    await callback.answer()


@router.callback_query(F.data.startswith("lang_"))
async def callback_set_language(callback: CallbackQuery):
    lang = callback.data.split("_")[1]

    lang_names = {"ru": "Русский 🇷🇺", "en": "English 🇬🇧"}

    await db.set_user_language(callback.from_user.id, lang)

    await callback.answer(f"Язык изменен на {lang_names.get(lang, lang)}", show_alert=True)
    await callback.message.edit_text(
        f"✅ Язык интерфейса изменен на {lang_names.get(lang, lang)}",
        reply_markup=get_settings_keyboard()
    )


@router.callback_query(F.data == "settings_notifications")
async def callback_notifications(callback: CallbackQuery):
    await callback.answer("🔔 Настройки уведомлений (в разработке)", show_alert=True)


@router.callback_query(F.data == "settings_back")
async def callback_settings_back(callback: CallbackQuery):
    await callback.message.delete()
    await callback.answer()
