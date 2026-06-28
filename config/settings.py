import os
from pathlib import Path
from typing import List
from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent.parent

# Загружаем .env файл только если он физически существует (на вашем ПК)
ENV_PATH = BASE_DIR / '.env'
if ENV_PATH.exists():
    load_dotenv(ENV_PATH)

class Settings:
    BOT_TOKEN: str = os.getenv('BOT_TOKEN', '')
    
    # Исправлена обработка списка ID администраторов
    ADMIN_IDS: List[int] = [
        int(id_) for id_ in os.getenv('ADMIN_IDS', '').replace(' ', '').split(',') 
        if id_.strip() and id_.strip().isdigit()
    ]

    DATABASE_URL: str = os.getenv('DATABASE_URL', 'sqlite+aiosqlite:///./database/bot.db')

    REDIS_HOST: str = os.getenv('REDIS_HOST', 'localhost')
    REDIS_PORT: int = int(os.getenv('REDIS_PORT', 6379))
    REDIS_DB: int = int(os.getenv('REDIS_DB', 0))

    LOG_LEVEL: str = os.getenv('LOG_LEVEL', 'INFO')

    WEBHOOK_URL: str = os.getenv('WEBHOOK_URL', '')
    WEBHOOK_PATH: str = os.getenv('WEBHOOK_PATH', '/webhook')
    WEBAPP_HOST: str = os.getenv('WEBAPP_HOST', '0.0.0.0')
    WEBAPP_PORT: int = int(os.getenv('WEBAPP_PORT', 8080))

    @classmethod
    def validate(cls):
        if not cls.BOT_TOKEN:
            raise ValueError("Configuration error: BOT_TOKEN is not set")
        if not cls.ADMIN_IDS:
            raise ValueError("Configuration error: ADMIN_IDS is not set")

# Инициализируем настройки и запускаем валидацию
settings = Settings()
settings.validate()
