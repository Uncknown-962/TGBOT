"""
Утилиты для работы с текстом
"""


def escape_html(text: str) -> str:
    """Экранирование HTML символов"""
    return (text
            .replace('&', '&amp;')
            .replace('<', '&lt;')
            .replace('>', '&gt;'))


def escape_markdown(text: str) -> str:
    """Экранирование Markdown символов"""
    special_chars = ['_', '*', '[', ']', '(', ')', '~', '`', '>', '#', '+', '-', '=', '|', '{', '}', '.', '!']
    for char in special_chars:
        text = text.replace(char, f'\\{char}')
    return text


def truncate_text(text: str, max_length: int = 100, suffix: str = '...') -> str:
    """Обрезка текста до определенной длины"""
    if len(text) <= max_length:
        return text
    return text[:max_length - len(suffix)] + suffix


def format_number(number: int) -> str:
    """Форматирование числа с разделителями тысяч"""
    return f"{number:,}".replace(',', ' ')


def plural_form(number: int, forms: tuple) -> str:
    """
    Возвращает правильную форму слова в зависимости от числа

    Args:
        number: Число
        forms: Кортеж из 3 форм (1, 2, 5) например: ('день', 'дня', 'дней')

    Returns:
        Правильная форма слова

    Example:
        >>> plural_form(1, ('день', 'дня', 'дней'))
        'день'
        >>> plural_form(2, ('день', 'дня', 'дней'))
        'дня'
        >>> plural_form(5, ('день', 'дня', 'дней'))
        'дней'
    """
    if number % 10 == 1 and number % 100 != 11:
        return forms[0]
    elif 2 <= number % 10 <= 4 and (number % 100 < 10 or number % 100 >= 20):
        return forms[1]
    else:
        return forms[2]
