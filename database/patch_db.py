import asyncio
import aiosqlite
from pathlib import Path

async def patch_db():
    db_path = Path("C:/Projects/4.6/TelegramBot/database/bot.db")
    if db_path.exists():
        async with aiosqlite.connect(db_path) as db:
            try:
                await db.execute("ALTER TABLE users ADD COLUMN coins INTEGER DEFAULT 1000")
                await db.commit()
                print("Column 'coins' added successfully.")
            except Exception as e:
                print(f"Skipping migration: {e}")

if __name__ == "__main__":
    asyncio.run(patch_db())
