import sys
import asyncio


def check_python_version():
    if sys.version_info < (3, 11):
        print("❌ Error: Python 3.11 or higher is required")
        print(f"Your version: {sys.version}")
        return False
    print(f"✅ Python version: {sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}")
    return True


def check_modules():
    required_modules = [
        'aiogram',
        'sqlalchemy',
        'aiosqlite',
        'dotenv',
        'loguru',
        'pydantic'
    ]

    missing = []
    for module in required_modules:
        try:
            __import__(module)
            print(f"✅ {module}")
        except ImportError:
            missing.append(module)
            print(f"❌ {module} - not installed")

    return len(missing) == 0, missing


def check_env_file():
    import os
    from pathlib import Path

    env_path = Path(__file__).parent / '.env'

    if not env_path.exists():
        print("❌ .env file not found")
        print("Please copy .env.example to .env and configure it")
        return False

    print("✅ .env file exists")

    from dotenv import load_dotenv
    load_dotenv(env_path)

    bot_token = os.getenv('BOT_TOKEN')
    admin_ids = os.getenv('ADMIN_IDS')

    if not bot_token or bot_token == 'your_bot_token_here':
        print("❌ BOT_TOKEN is not configured in .env")
        return False
    print("✅ BOT_TOKEN is configured")

    if not admin_ids or admin_ids == '123456789':
        print("⚠️  ADMIN_IDS is not configured in .env (using default)")
    else:
        print("✅ ADMIN_IDS is configured")

    return True


async def check_database():
    try:
        from database.database import db

        await db.create_tables()
        print("✅ Database connection successful")
        return True
    except Exception as e:
        print(f"❌ Database error: {e}")
        return False


async def check_bot_token():
    try:
        from aiogram import Bot
        from config.settings import settings

        bot = Bot(token=settings.BOT_TOKEN)
        me = await bot.get_me()
        print(f"✅ Bot token is valid: @{me.username}")
        await bot.session.close()
        return True
    except Exception as e:
        print(f"❌ Bot token error: {e}")
        return False


async def main():
    print("=" * 50)
    print("Telegram Bot - System Check")
    print("=" * 50)
    print()

    print("Checking Python version...")
    if not check_python_version():
        return False
    print()

    print("Checking required modules...")
    modules_ok, missing = check_modules()
    if not modules_ok:
        print(f"\n❌ Missing modules: {', '.join(missing)}")
        print("Run: pip install -r requirements.txt")
        return False
    print()

    print("Checking .env configuration...")
    if not check_env_file():
        return False
    print()

    print("Checking database connection...")
    if not await check_database():
        return False
    print()

    print("Checking bot token...")
    if not await check_bot_token():
        return False
    print()

    print("=" * 50)
    print("✅ All checks passed!")
    print("You can now run the bot with: python main.py")
    print("=" * 50)
    return True


if __name__ == "__main__":
    try:
        result = asyncio.run(main())
        sys.exit(0 if result else 1)
    except KeyboardInterrupt:
        print("\n\nCheck interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n❌ Critical error: {e}")
        sys.exit(1)
