class TelegramError(Exception):
    """Ошибка отправки сообщения телеграма"""
    pass


class ENDPOINTError(Exception):
    """Ошибка доступа к сайту"""
    pass


class NoResponseFromAPI(Exception):
    """Нет ответа API."""
    pass
