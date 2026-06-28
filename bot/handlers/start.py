from aiogram import Router, F
from aiogram.filters import CommandStart, Command
from aiogram.types import Message

from bot.keyboards.reply import get_main_keyboard
from database.database import db
from bot.utils.logger import log

router = Router()


@router.message(CommandStart())
async def cmd_start(message: Message, is_admin: bool = False):
    user = message.from_user

    await db.increment_commands(user.id)

    welcome_text = f"""
👋 Добро пожаловать, {user.first_name}!

Я многофункциональный бот с расширенными возможностями.

Используйте кнопки меню или команды:
/help - Помощь
/stats - Статистика
/settings - Настройки
"""

    if is_admin:
        welcome_text += "\n🔑 У вас есть права администратора!\n/admin - Панель администратора"

    keyboard = get_main_keyboard()

    await message.answer(welcome_text, reply_markup=keyboard)
    log.info(f"User {user.id} (@{user.username}) started the bot")


@router.message(Command("help"))
async def cmd_help(message: Message, is_admin: bool = False):
    await db.increment_commands(message.from_user.id)

    help_text = """
📖 <b>Доступные команды:</b>

/start - Запустить бота
/help - Показать эту справку
/stats - Показать вашу статистику
/settings - Настройки
/about - О боте
/support - Связаться с поддержкой

<b>Кнопки меню:</b>
📊 Статистика - Ваша статистика использования
ℹ️ О боте - Информация о боте
⚙️ Настройки - Персональные настройки
📞 Поддержка - Связь с поддержкой
"""

    if is_admin:
        help_text += """
\n🔑 <b>Команды администратора:</b>

/admin - Панель администратора
/users - Список пользователей
/broadcast - Рассылка сообщений
/stats_all - Общая статистика
"""

    await message.answer(help_text, parse_mode="HTML")


@router.message(Command("about"))
async def cmd_about(message: Message):
    await db.increment_commands(message.from_user.id)

    about_text = """
ℹ️ <b>О боте</b>

Версия: 1.0.0
Разработчик: @your_username

<b>Возможности:</b>
• База данных пользователей
• Система статистики
• Панель администратора
• Middleware для защиты от спама
• Логирование всех действий
• Inline и Reply клавиатуры
• Обработка callback'ов

<b>Технологии:</b>
• Python 3.11+
• aiogram 3.7
• SQLAlchemy (async)
• SQLite/PostgreSQL
"""

    await message.answer(about_text, parse_mode="HTML")


@router.message(F.text == "ℹ️ О боте")
async def button_about(message: Message):
    await cmd_about(message)
