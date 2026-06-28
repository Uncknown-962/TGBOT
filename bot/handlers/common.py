from aiogram import Router, F
from aiogram.types import Message

from database.database import db
from bot.utils.logger import log

router = Router()


@router.message(F.text)
async def handle_text(message: Message):
    user_id = message.from_user.id

    user = await db.get_user(user_id)
    if user and user.is_blocked:
        await message.answer("❌ Вы заблокированы")
        return

    await db.add_message(
        user_id=user_id,
        message_id=message.message_id,
        text=message.text,
        message_type="text"
    )

    await message.answer(
        "Извините, я не понял вашу команду.\n"
        "Используйте /help для просмотра доступных команд."
    )


@router.message(F.photo)
async def handle_photo(message: Message):
    await db.add_message(
        user_id=message.from_user.id,
        message_id=message.message_id,
        text=message.caption,
        message_type="photo"
    )

    await message.answer("📷 Фото получено!")


@router.message(F.document)
async def handle_document(message: Message):
    await db.add_message(
        user_id=message.from_user.id,
        message_id=message.message_id,
        text=message.caption,
        message_type="document"
    )

    await message.answer("📄 Документ получен!")


@router.message(F.video)
async def handle_video(message: Message):
    await db.add_message(
        user_id=message.from_user.id,
        message_id=message.message_id,
        text=message.caption,
        message_type="video"
    )

    await message.answer("🎥 Видео получено!")


@router.message()
async def handle_any(message: Message):
    log.info(f"Unhandled message type from user {message.from_user.id}: {message.content_type}")
    await message.answer("Извините, этот тип контента пока не поддерживается.")
