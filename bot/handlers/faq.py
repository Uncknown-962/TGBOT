from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message

from bot.utils.faq import get_faq_list, get_faq_answer, search_faq
from database.database import db

router = Router()


@router.message(Command("faq"))
async def cmd_faq(message: Message):
    await db.increment_commands(message.from_user.id)

    args = message.text.split(maxsplit=1)

    if len(args) == 1:
        await message.answer(get_faq_list(), parse_mode="HTML")
    else:
        try:
            faq_id = int(args[1])
            answer = get_faq_answer(faq_id)
            await message.answer(answer, parse_mode="HTML")
        except ValueError:
            query = args[1]
            results = search_faq(query)
            await message.answer(results, parse_mode="HTML")


@router.message(F.text == "❓ FAQ")
async def button_faq(message: Message):
    await message.answer(get_faq_list(), parse_mode="HTML")
