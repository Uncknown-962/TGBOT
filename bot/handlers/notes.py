from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message
import html

from database.database import db
from bot.utils.logger import log

router = Router()


@router.message(Command("note"))
async def cmd_notes(message: Message):
    user_id = message.from_user.id
    await db.increment_commands(user_id)

    args = message.text.split(maxsplit=1)

    if len(args) == 1:
        await show_notes(message, user_id)
    else:
        command_args = args[1].split(maxsplit=1)
        subcommand = command_args[0].lower()

        if subcommand == "add" and len(command_args) > 1:
            text = command_args[1]
            await db.add_note(user_id, text)
            await message.answer("✅ Заметка успешно добавлена!")
            log.info(f"User {user_id} added a note")
        
        elif subcommand == "del" and len(command_args) > 1:
            try:
                note_idx = int(command_args[1])
                notes = await db.get_notes(user_id)
                if 1 <= note_idx <= len(notes):
                    note_to_delete = notes[note_idx - 1]
                    await db.delete_note(note_to_delete.id, user_id)
                    await message.answer("✅ Заметка удалена!")
                    log.info(f"User {user_id} deleted note {note_to_delete.id}")
                else:
                    await message.answer("❌ Заметка с таким номером не найдена.")
            except ValueError:
                await message.answer("❌ Укажите корректный номер заметки.")
        else:
            await message.answer("❌ Неверный формат команды.\nИспользуйте: /note add [текст] или /note del [номер]")

async def show_notes(message: Message, user_id: int):
    notes = await db.get_notes(user_id)
    if not notes:
        await message.answer("📝 У вас нет сохраненных заметок.\n\nИспользуйте `/note add [текст]` чтобы добавить.", parse_mode="Markdown")
        return
    
    notes_text = "📝 <b>Ваши заметки:</b>\n\n"
    for idx, note in enumerate(notes, 1):
        safe_text = html.escape(note.text)
        notes_text += f"<b>{idx}.</b> {safe_text}\n"
    
    notes_text += "\n<i>Для удаления используйте /note del [номер]</i>"
    await message.answer(notes_text, parse_mode="HTML")


@router.message(F.text == "📝 Заметки")
async def button_notes(message: Message):
    user_id = message.from_user.id
    await db.increment_commands(user_id)
    await show_notes(message, user_id)
