"""
Декораторы для обработчиков
"""
import functools
from typing import Callable, Any
from aiogram.types import Message, CallbackQuery

from bot.utils.logger import log
from database.database import db


def log_handler(func: Callable) -> Callable:
    """Декоратор для логирования вызовов обработчиков"""
    @functools.wraps(func)
    async def wrapper(*args, **kwargs) -> Any:
        handler_name = func.__name__

        for arg in args:
            if isinstance(arg, Message):
                user_id = arg.from_user.id
                username = arg.from_user.username
                text = arg.text or arg.caption or arg.content_type
                log.info(f"Handler: {handler_name} | User: {user_id} (@{username}) | Text: {text}")
                break
            elif isinstance(arg, CallbackQuery):
                user_id = arg.from_user.id
                username = arg.from_user.username
                data = arg.data
                log.info(f"Handler: {handler_name} | User: {user_id} (@{username}) | Callback: {data}")
                break

        return await func(*args, **kwargs)

    return wrapper


def check_blocked(func: Callable) -> Callable:
    """Декоратор для проверки блокировки пользователя"""
    @functools.wraps(func)
    async def wrapper(*args, **kwargs) -> Any:
        message = None

        for arg in args:
            if isinstance(arg, (Message, CallbackQuery)):
                message = arg if isinstance(arg, Message) else arg.message
                user_id = arg.from_user.id
                break

        if message:
            user = await db.get_user(user_id)
            if user and user.is_blocked:
                await message.answer("❌ Вы заблокированы и не можете использовать бота")
                return None

        return await func(*args, **kwargs)

    return wrapper


def admin_only(func: Callable) -> Callable:
    """Декоратор для проверки прав администратора"""
    @functools.wraps(func)
    async def wrapper(*args, **kwargs) -> Any:
        is_admin = kwargs.get('is_admin', False)

        if not is_admin:
            for arg in args:
                if isinstance(arg, Message):
                    await arg.answer("❌ Эта команда доступна только администраторам")
                    return None
                elif isinstance(arg, CallbackQuery):
                    await arg.answer("❌ Эта функция доступна только администраторам", show_alert=True)
                    return None

        return await func(*args, **kwargs)

    return wrapper


def rate_limit(limit: float = 1.0):
    """
    Декоратор для ограничения частоты вызовов

    Args:
        limit: Минимальное время между вызовами в секундах
    """
    def decorator(func: Callable) -> Callable:
        last_call = {}

        @functools.wraps(func)
        async def wrapper(*args, **kwargs) -> Any:
            import time

            user_id = None
            message = None

            for arg in args:
                if isinstance(arg, (Message, CallbackQuery)):
                    user_id = arg.from_user.id
                    message = arg if isinstance(arg, Message) else arg.message
                    break

            if user_id:
                now = time.time()
                last = last_call.get(user_id, 0)

                if now - last < limit:
                    if message:
                        await message.answer("⏳ Пожалуйста, подождите немного перед следующей командой")
                    return None

                last_call[user_id] = now

            return await func(*args, **kwargs)

        return wrapper

    return decorator
