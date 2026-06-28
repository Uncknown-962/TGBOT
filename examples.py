"""
Примеры использования различных функций бота
"""

# Пример 1: Использование декораторов
from bot.utils.decorators import log_handler, check_blocked, rate_limit
from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message

router = Router()

@router.message(Command("example1"))
@log_handler
@check_blocked
@rate_limit(limit=2.0)
async def example_command(message: Message):
    await message.answer("Пример команды с декораторами")


# Пример 2: Работа с текстом
from bot.utils.text import escape_html, truncate_text, plural_form, format_number

text_with_html = "<b>Test</b>"
safe_text = escape_html(text_with_html)  # &lt;b&gt;Test&lt;/b&gt;

long_text = "Очень длинный текст..." * 10
short_text = truncate_text(long_text, max_length=50)

days = 5
form = plural_form(days, ('день', 'дня', 'дней'))  # 'дней'
print(f"{days} {form}")

number = 1000000
formatted = format_number(number)  # '1 000 000'


# Пример 3: Работа с датами
from bot.utils.datetime import time_ago, format_datetime, get_time_range
from datetime import datetime, timedelta

now = datetime.utcnow()
past = now - timedelta(hours=2)
print(time_ago(past))  # '2 часа назад'

formatted_date = format_datetime(now)  # '28.06.2026 21:05'

start, end = get_time_range('week')
print(f"Неделя: с {start} по {end}")


# Пример 4: Работа с пользователями
from bot.utils.user import get_user_display_name, format_user_link, is_user_admin

async def example_user_info(user_id: int):
    from database.database import db

    user = await db.get_user(user_id)
    if user:
        display_name = await get_user_display_name(user)
        print(f"Пользователь: {display_name}")

        user_link = await format_user_link(user)
        print(f"Ссылка: {user_link}")

        is_admin = await is_user_admin(user_id)
        print(f"Администратор: {is_admin}")


# Пример 5: Создание inline клавиатуры
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder

def create_custom_keyboard() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()

    builder.row(
        InlineKeyboardButton(text="Кнопка 1", callback_data="btn_1"),
        InlineKeyboardButton(text="Кнопка 2", callback_data="btn_2")
    )
    builder.row(
        InlineKeyboardButton(text="Назад", callback_data="back")
    )

    return builder.as_markup()


# Пример 6: Создание reply клавиатуры
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from aiogram.utils.keyboard import ReplyKeyboardBuilder

def create_custom_reply_keyboard() -> ReplyKeyboardMarkup:
    builder = ReplyKeyboardBuilder()

    builder.row(
        KeyboardButton(text="📱 Поделиться контактом", request_contact=True)
    )
    builder.row(
        KeyboardButton(text="📍 Поделиться местоположением", request_location=True)
    )
    builder.row(
        KeyboardButton(text="Отмена")
    )

    return builder.as_markup(resize_keyboard=True, one_time_keyboard=True)


# Пример 7: Работа с FSM (Finite State Machine)
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

class RegistrationStates(StatesGroup):
    waiting_for_name = State()
    waiting_for_age = State()
    waiting_for_city = State()

@router.message(Command("register"))
async def start_registration(message: Message, state: FSMContext):
    await message.answer("Как вас зовут?")
    await state.set_state(RegistrationStates.waiting_for_name)

@router.message(RegistrationStates.waiting_for_name)
async def process_name(message: Message, state: FSMContext):
    await state.update_data(name=message.text)
    await message.answer("Сколько вам лет?")
    await state.set_state(RegistrationStates.waiting_for_age)

@router.message(RegistrationStates.waiting_for_age)
async def process_age(message: Message, state: FSMContext):
    if not message.text.isdigit():
        await message.answer("Пожалуйста, введите число")
        return

    await state.update_data(age=int(message.text))
    await message.answer("В каком городе вы живете?")
    await state.set_state(RegistrationStates.waiting_for_city)

@router.message(RegistrationStates.waiting_for_city)
async def process_city(message: Message, state: FSMContext):
    data = await state.get_data()
    name = data.get('name')
    age = data.get('age')
    city = message.text

    await message.answer(
        f"Спасибо за регистрацию!\n\n"
        f"Имя: {name}\n"
        f"Возраст: {age}\n"
        f"Город: {city}"
    )

    await state.clear()


# Пример 8: Обработка callback queries
from aiogram.types import CallbackQuery
from aiogram import F

@router.callback_query(F.data == "example_callback")
async def handle_callback(callback: CallbackQuery):
    await callback.answer("Callback обработан!", show_alert=True)
    await callback.message.edit_text("Текст изменен после callback")


# Пример 9: Работа с медиа
@router.message(F.photo)
async def handle_photo(message: Message):
    photo = message.photo[-1]  # Берем самое большое фото
    file_id = photo.file_id

    await message.answer(f"Получено фото!\nFile ID: {file_id}")

    # Отправка фото обратно
    await message.answer_photo(file_id, caption="Ваше фото")


# Пример 10: Планировщик задач
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from datetime import datetime

scheduler = AsyncIOScheduler()

async def scheduled_task():
    """Задача, которая выполняется по расписанию"""
    from config.settings import settings
    from aiogram import Bot

    bot = Bot(token=settings.BOT_TOKEN)

    for admin_id in settings.ADMIN_IDS:
        try:
            await bot.send_message(
                admin_id,
                f"🕐 Запланированное сообщение в {datetime.now()}"
            )
        except Exception:
            pass

    await bot.session.close()

# Запуск задачи каждый день в 10:00
# scheduler.add_job(scheduled_task, 'cron', hour=10, minute=0)


# Пример 11: Middleware для логирования
from typing import Callable, Dict, Any, Awaitable
from aiogram import BaseMiddleware
from aiogram.types import TelegramObject

class LoggingMiddleware(BaseMiddleware):
    async def __call__(
        self,
        handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: Dict[str, Any]
    ) -> Any:
        from bot.utils.logger import log

        log.info(f"Received event: {event}")

        result = await handler(event, data)

        log.info(f"Event processed successfully")

        return result


# Пример 12: Фильтр для определенных пользователей
from aiogram.filters import Filter

class UserFilter(Filter):
    def __init__(self, user_ids: list):
        self.user_ids = user_ids

    async def __call__(self, message: Message) -> bool:
        return message.from_user.id in self.user_ids

# Использование:
# @router.message(UserFilter(user_ids=[123456789, 987654321]))
# async def only_for_specific_users(message: Message):
#     await message.answer("Эта команда доступна только определенным пользователям")
