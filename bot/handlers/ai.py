import aiohttp
from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message
from config.settings import settings

router = Router()

@router.message(Command("ask"))
async def cmd_ask(message: Message):
    if not hasattr(settings, 'GEMINI_API_KEY') or not settings.GEMINI_API_KEY:
        await message.answer("❌ AI не настроен. Добавьте GEMINI_API_KEY в .env")
        return
        
    args = message.text.split(maxsplit=1)
    if len(args) < 2:
        await message.answer("ℹ️ Использование: `/ask <ваш вопрос>`", parse_mode="Markdown")
        return
        
    question = args[1]
    wait_msg = await message.answer("⏳ <i>Думаю...</i>", parse_mode="HTML")
    
    try:
        url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={settings.GEMINI_API_KEY}"
        payload = {
            "contents": [{"parts": [{"text": question}]}]
        }
        async with aiohttp.ClientSession() as session:
            async with session.post(url, json=payload) as resp:
                data = await resp.json()
                if resp.status == 200:
                    answer = data['candidates'][0]['content']['parts'][0]['text']
                    await wait_msg.edit_text(answer[:4096], parse_mode="Markdown")
                else:
                    await wait_msg.edit_text("❌ Ошибка от API.")
    except Exception as e:
        await wait_msg.edit_text(f"❌ Ошибка соединения: {e}")
