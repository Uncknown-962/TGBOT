from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder


def get_admin_inline_keyboard() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(text="👥 Пользователи", callback_data="admin_users"),
        InlineKeyboardButton(text="📊 Статистика", callback_data="admin_stats")
    )
    builder.row(
        InlineKeyboardButton(text="📢 Рассылка", callback_data="admin_broadcast"),
        InlineKeyboardButton(text="❌ Выключить бота", callback_data="admin_shutdown")
    )
    builder.row(
        InlineKeyboardButton(text="◀️ Закрыть", callback_data="admin_close")
    )
    return builder.as_markup()

def get_settings_keyboard() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(text="🌐 Язык", callback_data="settings_language"),
        InlineKeyboardButton(text="🔔 Уведомления", callback_data="settings_notifications")
    )
    builder.row(
        InlineKeyboardButton(text="◀️ Назад", callback_data="settings_back")
    )
    return builder.as_markup()


def get_language_keyboard() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(text="🇷🇺 Русский", callback_data="lang_ru"),
        InlineKeyboardButton(text="🇬🇧 English", callback_data="lang_en")
    )
    builder.row(
        InlineKeyboardButton(text="◀️ Назад", callback_data="settings_menu")
    )
    return builder.as_markup()


def get_confirm_keyboard(action: str) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(text="✅ Да", callback_data=f"confirm_{action}"),
        InlineKeyboardButton(text="❌ Нет", callback_data=f"cancel_{action}")
    )
    return builder.as_markup()


def get_pagination_keyboard(page: int, total_pages: int, prefix: str) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()

    buttons = []
    if page > 1:
        buttons.append(InlineKeyboardButton(text="⬅️", callback_data=f"{prefix}_page_{page-1}"))

    buttons.append(InlineKeyboardButton(text=f"{page}/{total_pages}", callback_data="current_page"))

    if page < total_pages:
        buttons.append(InlineKeyboardButton(text="➡️", callback_data=f"{prefix}_page_{page+1}"))

    builder.row(*buttons)
    builder.row(InlineKeyboardButton(text="◀️ Назад", callback_data=f"{prefix}_back"))

    return builder.as_markup()
