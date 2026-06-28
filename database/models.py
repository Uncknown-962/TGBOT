from datetime import datetime, timezone
from sqlalchemy import BigInteger, String, DateTime, Boolean, Integer, Text, ForeignKey
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
from typing import Optional, List


class Base(DeclarativeBase):
    pass


class User(Base):
    __tablename__ = 'users'

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    username: Mapped[Optional[str]] = mapped_column(String(255))
    first_name: Mapped[Optional[str]] = mapped_column(String(255))
    last_name: Mapped[Optional[str]] = mapped_column(String(255))
    language_code: Mapped[Optional[str]] = mapped_column(String(10))
    language: Mapped[str] = mapped_column(String(10), default='ru')
    coins: Mapped[int] = mapped_column(Integer, default=1000)
    is_bot: Mapped[bool] = mapped_column(Boolean, default=False)
    is_premium: Mapped[bool] = mapped_column(Boolean, default=False)
    is_blocked: Mapped[bool] = mapped_column(Boolean, default=False)
    
    # Добавлено DateTime(timezone=True) для корректной работы с PostgreSQL
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))
    last_bonus: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), default=None)
    
    title: Mapped[str] = mapped_column(String(50), default="")
    referrer_id: Mapped[Optional[int]] = mapped_column(BigInteger, default=None)

    messages: Mapped[List["Message"]] = relationship(back_populates="user", cascade="all, delete-orphan")
    user_stats: Mapped[Optional["UserStats"]] = relationship(back_populates="user", cascade="all, delete-orphan")
    notes: Mapped[List["Note"]] = relationship(back_populates="user", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<User(id={self.id}, username={self.username})>"


class Message(Base):
    __tablename__ = 'messages'

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(BigInteger, ForeignKey('users.id', ondelete='CASCADE'))
    message_id: Mapped[int] = mapped_column(BigInteger)
    text: Mapped[Optional[str]] = mapped_column(Text)
    message_type: Mapped[str] = mapped_column(String(50))
    
    # Добавлено DateTime(timezone=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))

    user: Mapped["User"] = relationship(back_populates="messages")

    def __repr__(self):
        return f"<Message(id={self.id}, user_id={self.user_id})>"


class UserStats(Base):
    __tablename__ = 'user_stats'

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(BigInteger, ForeignKey('users.id', ondelete='CASCADE'), unique=True)
    total_messages: Mapped[int] = mapped_column(Integer, default=0)
    total_commands: Mapped[int] = mapped_column(Integer, default=0)
    
    # Добавлено DateTime(timezone=True)
    last_activity: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))

    user: Mapped["User"] = relationship(back_populates="user_stats")

    def __repr__(self):
        return f"<UserStats(user_id={self.user_id}, total_messages={self.total_messages})>"


class Note(Base):
    __tablename__ = 'notes'

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(BigInteger, ForeignKey('users.id', ondelete='CASCADE'))
    text: Mapped[str] = mapped_column(Text)
    
    # Добавлено DateTime(timezone=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))

    user: Mapped["User"] = relationship(back_populates="notes")

    def __repr__(self):
        return f"<Note(id={self.id}, user_id={self.user_id})>"
