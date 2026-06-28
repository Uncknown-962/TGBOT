"""
Утилиты для работы с датами и временем
"""
from datetime import datetime, timedelta, timezone
from typing import Optional


def format_datetime(dt: datetime, format_str: str = "%d.%m.%Y %H:%M") -> str:
    """Форматирование даты и времени"""
    return dt.strftime(format_str)


def format_date(dt: datetime) -> str:
    """Форматирование даты"""
    return dt.strftime("%d.%m.%Y")


def format_time(dt: datetime) -> str:
    """Форматирование времени"""
    return dt.strftime("%H:%M")


def time_ago(dt: datetime) -> str:
    """
    Возвращает человекочитаемое представление времени

    Example:
        >>> time_ago(datetime.now() - timedelta(minutes=5))
        '5 минут назад'
    """
    now = datetime.now(timezone.utc).replace(tzinfo=None)
    diff = now - dt

    seconds = diff.total_seconds()

    if seconds < 60:
        return "только что"
    elif seconds < 3600:
        minutes = int(seconds / 60)
        if minutes == 1:
            return "1 минуту назад"
        elif 2 <= minutes <= 4:
            return f"{minutes} минуты назад"
        else:
            return f"{minutes} минут назад"
    elif seconds < 86400:
        hours = int(seconds / 3600)
        if hours == 1:
            return "1 час назад"
        elif 2 <= hours <= 4:
            return f"{hours} часа назад"
        else:
            return f"{hours} часов назад"
    elif seconds < 2592000:
        days = int(seconds / 86400)
        if days == 1:
            return "вчера"
        elif 2 <= days <= 4:
            return f"{days} дня назад"
        else:
            return f"{days} дней назад"
    elif seconds < 31536000:
        months = int(seconds / 2592000)
        if months == 1:
            return "1 месяц назад"
        elif 2 <= months <= 4:
            return f"{months} месяца назад"
        else:
            return f"{months} месяцев назад"
    else:
        years = int(seconds / 31536000)
        if years == 1:
            return "1 год назад"
        elif 2 <= years <= 4:
            return f"{years} года назад"
        else:
            return f"{years} лет назад"


def get_time_range(period: str) -> tuple[datetime, datetime]:
    """
    Возвращает временной диапазон

    Args:
        period: 'today', 'yesterday', 'week', 'month', 'year'

    Returns:
        Кортеж (start_date, end_date)
    """
    now = datetime.now(timezone.utc).replace(tzinfo=None)
    today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)

    if period == 'today':
        return today_start, now
    elif period == 'yesterday':
        yesterday = today_start - timedelta(days=1)
        return yesterday, today_start
    elif period == 'week':
        week_start = today_start - timedelta(days=today_start.weekday())
        return week_start, now
    elif period == 'month':
        month_start = today_start.replace(day=1)
        return month_start, now
    elif period == 'year':
        year_start = today_start.replace(month=1, day=1)
        return year_start, now
    else:
        return today_start, now
