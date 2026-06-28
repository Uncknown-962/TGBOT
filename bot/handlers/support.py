from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

from bot.keyboards.reply import get_cancel_keyboard, get_main_keyboard
from database.database import db
from config.settings import settings

router = Router()


class SupportStates(StatesGroup):
    waiting_for_message = State()


@router.message(Command("support"))
async def cmd_support(message: Message, state: FSMContext):
    await db.increment_commands(message.from_user.id)

    support_text = """
📞 <b>Поддержка</b>

Если у вас возникли вопросы или проблемы, отправьте сообщение администраторам.

Напишите ваше сообщение:
"""

    await message.answer(
        support_text,
        parse_mode="HTML",
        reply_markup=get_cancel_keyboard()
    )

    await state.set_state(SupportStates.waiting_for_message)


@router.message(F.text == "📞 Поддержка")
async def button_support(message: Message, state: FSMContext):
    await cmd_support(message, state)


@router.message(SupportStates.waiting_for_message, F.text == "❌ Отмена")
async def support_cancel(message: Message, state: FSMContext):
    await state.clear()
    await message.answer(
        "❌ Отменено",
        reply_markup=get_main_keyboard()
    )


@router.message(SupportStates.waiting_for_message)
async def support_send(message: Message, state: FSMContext):
    user = message.from_user

    support_msg = f"""
📩 <b>Новое сообщение в поддержку</b>

От: {user.first_name} {user.last_name or ''}
Username: @{user.username or 'не указан'}
ID: <code>{user.id}</code>

<b>Сообщение:</b>
{message.text}
"""

    sent_count = 0
    for admin_id in settings.ADMIN_IDS:
        try:
            await message.bot.send_message(admin_id, support_msg, parse_mode="HTML")
            sent_count += 1
        except Exception:
            pass

    if sent_count > 0:
        await message.answer(
            "✅ Ваше сообщение отправлено администраторам.\n"
            "Мы ответим вам как можно скорее!",
            reply_markup=get_main_keyboard()
        )
    else:
        await message.answer(
            "❌ Не удалось отправить сообщение. Попробуйте позже.",
            reply_markup=get_main_keyboard()
        )

    await state.clear()
