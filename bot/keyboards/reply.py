from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from aiogram.utils.keyboard import ReplyKeyboardBuilder


def get_main_keyboard() -> ReplyKeyboardMarkup:
    builder = ReplyKeyboardBuilder()
    builder.row(
        KeyboardButton(text="📊 Статистика"),
        KeyboardButton(text="👤 Профиль")
    )
    builder.row(
        KeyboardButton(text="📝 Заметки"),
        KeyboardButton(text="🎲 Игры")
    )
    builder.row(
        KeyboardButton(text="⚙️ Настройки"),
        KeyboardButton(text="📞 Поддержка")
    )
    builder.row(
        KeyboardButton(text="❓ FAQ"),
        KeyboardButton(text="ℹ️ О боте")
    )
    return builder.as_markup(resize_keyboard=True)



def get_cancel_keyboard() -> ReplyKeyboardMarkup:
    builder = ReplyKeyboardBuilder()
    builder.row(KeyboardButton(text="❌ Отмена"))
    return builder.as_markup(resize_keyboard=True)
