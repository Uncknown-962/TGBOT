import asyncio
import aiosqlite
from pathlib import Path

async def patch_db():
    db_path = Path("C:/Projects/4.6/TelegramBot/database/bot.db")
    if db_path.exists():
        async with aiosqlite.connect(db_path) as db:
            try:
                await db.execute("ALTER TABLE users ADD COLUMN last_bonus DATETIME")
                print("Column 'last_bonus' added.")
            except Exception as e:
                print(f"Skipped last_bonus: {e}")
                
            try:
                await db.execute("ALTER TABLE users ADD COLUMN title VARCHAR(50) DEFAULT ''")
                print("Column 'title' added.")
            except Exception as e:
                print(f"Skipped title: {e}")
                
            try:
                await db.execute("ALTER TABLE users ADD COLUMN referrer_id BIGINT")
                print("Column 'referrer_id' added.")
            except Exception as e:
                print(f"Skipped referrer_id: {e}")
            
            await db.commit()

if __name__ == "__main__":
    asyncio.run(patch_db())
