"""
Вспомогательные функции для работы с пользователями
"""
from typing import Optional, List
from aiogram.types import User as TelegramUser

from database.database import db
from database.models import User


async def get_user_display_name(user: User) -> str:
    """Возвращает отображаемое имя пользователя"""
    if user.username:
        return f"@{user.username}"
    elif user.first_name and user.last_name:
        return f"{user.first_name} {user.last_name}"
    elif user.first_name:
        return user.first_name
    else:
        return f"User {user.id}"


async def format_user_link(user: User) -> str:
    """Возвращает HTML ссылку на пользователя"""
    display_name = await get_user_display_name(user)
    return f'<a href="tg://user?id={user.id}">{display_name}</a>'


async def is_user_admin(user_id: int) -> bool:
    """Проверяет, является ли пользователь администратором"""
    from config.settings import settings
    return user_id in settings.ADMIN_IDS


async def get_active_users_count() -> int:
    """Возвращает количество активных пользователей"""
    users = await db.get_all_users()
    return len([u for u in users if not u.is_blocked])


async def get_user_info(user_id: int) -> Optional[str]:
    """Возвращает информацию о пользователе"""
    user = await db.get_user(user_id)
    if not user:
        return None

    stats = await db.get_user_stats(user_id)

    info = f"""
👤 <b>Информация о пользователе</b>

ID: <code>{user.id}</code>
Имя: {user.first_name}
Фамилия: {user.last_name or 'не указана'}
Username: @{user.username or 'не указан'}
Язык: {user.language_code or 'не указан'}
Premium: {'✅' if user.is_premium else '❌'}
Заблокирован: {'✅' if user.is_blocked else '❌'}

Регистрация: {user.created_at.strftime('%d.%m.%Y %H:%M')}
Последнее обновление: {user.updated_at.strftime('%d.%m.%Y %H:%M')}
"""

    if stats:
        info += f"""
📊 <b>Статистика:</b>
Сообщений: {stats.total_messages}
Команд: {stats.total_commands}
Последняя активность: {stats.last_activity.strftime('%d.%m.%Y %H:%M')}
"""

    return info


def extract_user_data(telegram_user: TelegramUser) -> dict:
    """Извлекает данные пользователя из объекта Telegram User"""
    return {
        'id': telegram_user.id,
        'username': telegram_user.username,
        'first_name': telegram_user.first_name,
        'last_name': telegram_user.last_name,
        'language_code': telegram_user.language_code,
        'is_bot': telegram_user.is_bot,
        'is_premium': getattr(telegram_user, 'is_premium', False)
    }
