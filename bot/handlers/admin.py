from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
import os
import signal

from bot.filters.admin import IsAdmin
from bot.keyboards.inline import get_confirm_keyboard, get_pagination_keyboard, get_admin_inline_keyboard
from bot.keyboards.reply import get_cancel_keyboard, get_main_keyboard
from database.database import db
from bot.utils.logger import log
from bot.utils.user import get_user_info

router = Router()
router.message.filter(IsAdmin())
router.callback_query.filter(IsAdmin())


class BroadcastStates(StatesGroup):
    waiting_for_message = State()


@router.message(Command("admin"))
async def cmd_admin(message: Message):
    await db.increment_commands(message.chat.id)

    admin_text = """
🔑 <b>Панель администратора</b>

Доступные команды:

/users - Список всех пользователей
/stats_all - Общая статистика бота
/broadcast - Рассылка сообщений
/block [user_id] - Заблокировать пользователя
/unblock [user_id] - Разблокировать пользователя
/shutdown - Выключить бота

Используйте эти команды с осторожностью!
"""

    await message.answer(admin_text, parse_mode="HTML", reply_markup=get_admin_inline_keyboard())
    log.info(f"Admin {message.chat.id} opened admin panel")


@router.message(Command("stats_all"))
async def cmd_stats_all(message: Message):
    await db.increment_commands(message.chat.id)

    users = await db.get_all_users()
    total_users = len(users)
    active_users = len([u for u in users if not u.is_blocked])
    blocked_users = len([u for u in users if u.is_blocked])
    premium_users = len([u for u in users if u.is_premium])

    total_messages = 0
    total_commands = 0

    for user in users:
        stats = await db.get_user_stats(user.id)
        if stats:
            total_messages += stats.total_messages
            total_commands += stats.total_commands

    stats_text = f"""
📊 <b>Общая статистика бота</b>

👥 <b>Пользователи:</b>
• Всего: {total_users}
• Активных: {active_users}
• Заблокированных: {blocked_users}
• Premium: {premium_users}

📈 <b>Активность:</b>
• Всего сообщений: {total_messages}
• Всего команд: {total_commands}
• Среднее сообщений на пользователя: {total_messages // total_users if total_users > 0 else 0}
"""

    await message.answer(stats_text, parse_mode="HTML")
    log.info(f"Admin {message.chat.id} requested global stats")


@router.message(Command("users"))
async def cmd_users(message: Message):
    await db.increment_commands(message.chat.id)

    users = await db.get_all_users()

    if not users:
        await message.answer("❌ Пользователей не найдено")
        return

    users_text = "👥 <b>Список пользователей</b>\n\n"

    for i, user in enumerate(users[:20], 1):
        status = "🚫" if user.is_blocked else "✅"
        premium = "⭐" if user.is_premium else ""
        users_text += f"{i}. {status} {premium} <code>{user.id}</code> - {user.first_name}"
        if user.username:
            users_text += f" (@{user.username})"
        users_text += "\n"

    if len(users) > 20:
        users_text += f"\n... и еще {len(users) - 20} пользователей"

    await message.answer(users_text, parse_mode="HTML")


@router.message(Command("broadcast"))
async def cmd_broadcast(message: Message, state: FSMContext):
    await db.increment_commands(message.chat.id)

    await message.answer(
        "📢 <b>Рассылка сообщений</b>\n\n"
        "Отправьте сообщение, которое хотите разослать всем пользователям.\n"
        "Можно отправить текст, фото, видео или документ.",
        parse_mode="HTML",
        reply_markup=get_cancel_keyboard()
    )

    await state.set_state(BroadcastStates.waiting_for_message)


@router.message(BroadcastStates.waiting_for_message, F.text == "❌ Отмена")
async def broadcast_cancel(message: Message, state: FSMContext):
    await state.clear()
    await message.answer(
        "❌ Рассылка отменена",
        reply_markup=get_main_keyboard()
    )


@router.message(BroadcastStates.waiting_for_message)
async def broadcast_confirm(message: Message, state: FSMContext):
    await state.update_data(broadcast_message=message)

    users = await db.get_all_users()
    active_users = len([u for u in users if not u.is_blocked])

    await message.answer(
        f"📢 Подтвердите рассылку\n\n"
        f"Сообщение будет отправлено {active_users} пользователям.\n"
        f"Вы уверены?",
        reply_markup=get_confirm_keyboard("broadcast")
    )


@router.callback_query(F.data == "confirm_broadcast")
async def broadcast_send(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    broadcast_msg = data.get('broadcast_message')

    if not broadcast_msg:
        await callback.answer("❌ Ошибка: сообщение не найдено", show_alert=True)
        return

    users = await db.get_all_users()
    active_users = [u for u in users if not u.is_blocked]

    success = 0
    failed = 0

    status_msg = await callback.message.answer("📤 Начинаю рассылку...")

    for i, user in enumerate(active_users):
        try:
            await broadcast_msg.copy_to(user.id)
            success += 1
        except Exception as e:
            failed += 1
            log.error(f"Failed to send broadcast to {user.id}: {e}")

        if (i + 1) % 10 == 0:
            await status_msg.edit_text(
                f"📤 Рассылка: {i + 1}/{len(active_users)}\n"
                f"✅ Успешно: {success}\n"
                f"❌ Ошибок: {failed}"
            )

    await status_msg.edit_text(
        f"✅ Рассылка завершена!\n\n"
        f"Отправлено: {success}\n"
        f"Ошибок: {failed}"
    )

    await callback.message.delete()
    await state.clear()

    log.info(f"Admin {callback.from_user.id} completed broadcast: {success} success, {failed} failed")


@router.callback_query(F.data == "cancel_broadcast")
async def broadcast_cancel_callback(callback: CallbackQuery, state: FSMContext):
    await state.clear()
    await callback.message.edit_text("❌ Рассылка отменена")
    await callback.answer()


@router.message(Command("block"))
async def cmd_block_user(message: Message):
    await db.increment_commands(message.chat.id)

    args = message.text.split()
    if len(args) < 2:
        await message.answer("❌ Использование: /block [user_id]")
        return

    try:
        user_id = int(args[1])
        await db.block_user(user_id)
        await message.answer(f"✅ Пользователь {user_id} заблокирован")
        log.info(f"Admin {message.chat.id} blocked user {user_id}")
    except ValueError:
        await message.answer("❌ Неверный ID пользователя")
    except Exception as e:
        await message.answer(f"❌ Ошибка: {e}")


@router.message(Command("unblock"))
async def cmd_unblock_user(message: Message):
    await db.increment_commands(message.chat.id)

    args = message.text.split()
    if len(args) < 2:
        await message.answer("❌ Использование: /unblock [user_id]")
        return

    try:
        user_id = int(args[1])
        await db.unblock_user(user_id)
        await message.answer(f"✅ Пользователь {user_id} разблокирован")
        log.info(f"Admin {message.chat.id} unblocked user {user_id}")
    except ValueError:
        await message.answer("❌ Неверный ID пользователя")
    except Exception as e:
        await message.answer(f"❌ Ошибка: {e}")


@router.callback_query(F.data == "admin_users")
async def cb_users(callback: CallbackQuery):
    await cmd_users(callback.message)
    await callback.answer()

@router.callback_query(F.data == "admin_broadcast")
async def cb_broadcast(callback: CallbackQuery, state: FSMContext):
    await cmd_broadcast(callback.message, state)
    await callback.answer()

@router.callback_query(F.data == "admin_stats")
async def cb_stats(callback: CallbackQuery):
    await cmd_stats_all(callback.message)
    await callback.answer()

@router.callback_query(F.data == "admin_close")
async def cb_close(callback: CallbackQuery):
    await callback.message.delete()
    await callback.answer()

@router.callback_query(F.data == "admin_leaderboard")
async def cb_leaderboard(callback: CallbackQuery):
    from bot.handlers.stats import cmd_top
    await cmd_top(callback.message)
    await callback.answer()

@router.message(Command("shutdown"))
async def cmd_shutdown(message: Message):
    await message.answer("🛑 Бот выключается...")
    log.info(f"Admin {message.chat.id} triggered shutdown")
    os.kill(os.getpid(), signal.SIGINT)

@router.callback_query(F.data == "admin_shutdown")
async def cb_shutdown(callback: CallbackQuery):
    await callback.message.edit_text("🛑 Бот выключается...")
    await callback.answer()
    log.info(f"Admin {callback.message.chat.id} triggered shutdown")
    os.kill(os.getpid(), signal.SIGINT)

@router.message(Command("userinfo"))
async def cmd_userinfo(message: Message):
    await db.increment_commands(message.chat.id)
    args = message.text.split()
    if len(args) < 2:
        await message.answer("❌ Использование: /userinfo [user_id]")
        return
    try:
        user_id = int(args[1])
        info = await get_user_info(user_id)
        if info:
            await message.answer(info, parse_mode="HTML")
        else:
            await message.answer("❌ Пользователь не найден")
    except ValueError:
        await message.answer("❌ Неверный ID пользователя")
