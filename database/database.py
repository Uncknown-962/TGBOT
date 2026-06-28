from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy import select, delete
from typing import Optional, List
from datetime import datetime, timezone
from contextlib import asynccontextmanager

from database.models import Base, User, Message, UserStats, Note
from config.settings import settings


class Database:
    def __init__(self, db_url: str):
        self.engine = create_async_engine(db_url, echo=False)
        self.session_maker = async_sessionmaker(
            self.engine,
            class_=AsyncSession,
            expire_on_commit=False
        )

    async def create_tables(self):
        async with self.engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)

    async def drop_tables(self):
        async with self.engine.begin() as conn:
            await conn.run_sync(Base.metadata.drop_all)

    @asynccontextmanager
    async def get_session(self):
        """Async context manager for getting a database session"""
        async with self.session_maker() as session:
            yield session

    async def add_user(self, user_data: dict) -> User:
        async with self.session_maker() as session:
            result = await session.execute(
                select(User).where(User.id == user_data['id'])
            )
            user = result.scalar_one_or_none()

            if user:
                for key, value in user_data.items():
                    setattr(user, key, value)
                user.updated_at = datetime.now(timezone.utc)
            else:
                user = User(**user_data)
                session.add(user)

                user_stats = UserStats(user_id=user.id)
                session.add(user_stats)

            await session.commit()
            await session.refresh(user)
            return user

    async def get_user(self, user_id: int) -> Optional[User]:
        async with self.session_maker() as session:
            result = await session.execute(
                select(User).where(User.id == user_id)
            )
            return result.scalar_one_or_none()

    async def add_message(self, user_id: int, message_id: int, text: Optional[str], message_type: str):
        async with self.session_maker() as session:
            message = Message(
                user_id=user_id,
                message_id=message_id,
                text=text,
                message_type=message_type
            )
            session.add(message)

            result = await session.execute(
                select(UserStats).where(UserStats.user_id == user_id)
            )
            stats = result.scalar_one_or_none()

            if stats:
                stats.total_messages += 1
                stats.last_activity = datetime.now(timezone.utc)

            await session.commit()

    async def increment_commands(self, user_id: int):
        async with self.session_maker() as session:
            result = await session.execute(
                select(UserStats).where(UserStats.user_id == user_id)
            )
            stats = result.scalar_one_or_none()

            if stats:
                stats.total_commands += 1
                stats.last_activity = datetime.now(timezone.utc)
                await session.commit()

    async def get_user_stats(self, user_id: int) -> Optional[UserStats]:
        async with self.session_maker() as session:
            result = await session.execute(
                select(UserStats).where(UserStats.user_id == user_id)
            )
            return result.scalar_one_or_none()

    async def get_all_users(self):
        async with self.session_maker() as session:
            result = await session.execute(select(User))
            return result.scalars().all()

    async def block_user(self, user_id: int):
        async with self.session_maker() as session:
            result = await session.execute(
                select(User).where(User.id == user_id)
            )
            user = result.scalar_one_or_none()
            if user:
                user.is_blocked = True
                await session.commit()

    async def unblock_user(self, user_id: int):
        async with self.session_maker() as session:
            result = await session.execute(
                select(User).where(User.id == user_id)
            )
            user = result.scalar_one_or_none()
            if user:
                user.is_blocked = False
                await session.commit()

    async def set_user_language(self, user_id: int, language: str):
        async with self.session_maker() as session:
            result = await session.execute(
                select(User).where(User.id == user_id)
            )
            user = result.scalar_one_or_none()
            if user:
                user.language = language
                user.updated_at = datetime.now(timezone.utc)
                await session.commit()

    async def get_notes(self, user_id: int) -> List[Note]:
        async with self.session_maker() as session:
            result = await session.execute(
                select(Note).where(Note.user_id == user_id).order_by(Note.created_at)
            )
            return result.scalars().all()

    async def add_note(self, user_id: int, text: str) -> Note:
        async with self.session_maker() as session:
            note = Note(user_id=user_id, text=text)
            session.add(note)
            await session.commit()
            await session.refresh(note)
            return note

    async def get_notes(self, user_id: int) -> list[Note]:
        async with self.session_maker() as session:
            result = await session.execute(
                select(Note).where(Note.user_id == user_id).order_by(Note.created_at.desc())
            )
            return result.scalars().all()

    async def delete_note(self, note_id: int, user_id: int) -> bool:
        """Delete a note. Returns True if deleted, False if not found or not owned."""
        async with self.session_maker() as session:
            result = await session.execute(
                select(Note).where(Note.id == note_id, Note.user_id == user_id)
            )
            note = result.scalar_one_or_none()
            if note:
                await session.delete(note)
                await session.commit()
                return True
            return False

    # --- Language ---

    async def update_user_language(self, user_id: int, language: str):
        async with self.session_maker() as session:
            result = await session.execute(
                select(User).where(User.id == user_id)
            )
            user = result.scalar_one_or_none()
            if user:
                user.language = language
                user.updated_at = datetime.now(timezone.utc)
                await session.commit()

    # --- User count ---

    async def get_users_count(self) -> int:
        async with self.session_maker() as session:
            result = await session.execute(select(User))
            return len(result.scalars().all())

    async def get_user_coins(self, user_id: int) -> int:
        async with self.session_maker() as session:
            result = await session.execute(select(User).where(User.id == user_id))
            user = result.scalar_one_or_none()
            return user.coins if user else 0

    async def update_user_coins(self, user_id: int, amount: int) -> int:
        async with self.session_maker() as session:
            result = await session.execute(select(User).where(User.id == user_id))
            user = result.scalar_one_or_none()
            if user:
                user.coins += amount
                await session.commit()
                return user.coins
            return 0

    async def get_top_users_by_coins(self, limit: int = 10):
        async with self.session_maker() as session:
            result = await session.execute(
                select(User).order_by(User.coins.desc()).limit(limit)
            )
            return result.scalars().all()

    async def get_top_users_by_xp(self, limit: int = 10):
        async with self.session_maker() as session:
            result = await session.execute(
                select(User, UserStats)
                .join(UserStats, User.id == UserStats.user_id)
            )
            users_with_stats = result.all()
            
            now = datetime.now(timezone.utc).replace(tzinfo=None)
            user_xps = []
            for user, stats in users_with_stats:
                days_active = (now - user.created_at).days or 1
                exp = (days_active * 10) + (stats.total_messages * 2)
                user_xps.append((user, exp))
            
            user_xps.sort(key=lambda x: x[1], reverse=True)
            return user_xps[:limit]

    async def claim_bonus(self, user_id: int, amount: int, current_time: datetime):
        async with self.session_maker() as session:
            result = await session.execute(select(User).where(User.id == user_id))
            user = result.scalar_one_or_none()
            if user:
                user.coins += amount
                user.last_bonus = current_time
                await session.commit()

    async def set_referrer(self, user_id: int, referrer_id: int):
        async with self.session_maker() as session:
            result = await session.execute(select(User).where(User.id == user_id))
            user = result.scalar_one_or_none()
            if user and not user.referrer_id:
                user.referrer_id = referrer_id
                await session.commit()

    async def set_user_title(self, user_id: int, title: str):
        async with self.session_maker() as session:
            result = await session.execute(select(User).where(User.id == user_id))
            user = result.scalar_one_or_none()
            if user:
                user.title = title
                await session.commit()

    async def set_user_vip(self, user_id: int, is_vip: bool):
        async with self.session_maker() as session:
            result = await session.execute(select(User).where(User.id == user_id))
            user = result.scalar_one_or_none()
            if user:
                user.is_premium = is_vip
                await session.commit()


db = Database(settings.DATABASE_URL)
