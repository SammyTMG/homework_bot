import os
import time
import logging
import sys

import telegram
import requests

from http import HTTPStatus
from exceptions import TelegramError, ENDPOINTError, NoResponseFromAPI
from dotenv import load_dotenv

load_dotenv()


PRACTICUM_TOKEN = os.getenv('PRACTICUM_TOKEN')
TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')
TELEGRAM_CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')

RETRY_PERIOD = 600
ENDPOINT = 'https://practicum.yandex.ru/api/user_api/homework_statuses/'
HEADERS = {'Authorization': f'OAuth {PRACTICUM_TOKEN}'}


HOMEWORK_VERDICTS = {
    'approved': 'Работа проверена: ревьюеру всё понравилось. Ура!',
    'reviewing': 'Работа взята на проверку ревьюером.',
    'rejected': 'Работа проверена: у ревьюера есть замечания.'
}


def check_tokens():
    """Проверяет доступность переменных окружения.
    Если все доступно, вернет - True"""
    logging.info('Проверка всех токенов')
    if all([PRACTICUM_TOKEN, TELEGRAM_TOKEN, TELEGRAM_CHAT_ID]):
        return True


def send_message(bot, message):
    """Отправляет сообщение в чат."""
    try:
        bot.send_message(chat_id=TELEGRAM_CHAT_ID,
                         text=message)
        logging.debug(f'Сообщение отправлено {message}')
    except telegram.error.TelegramError as error:
        logging.error(error)
        raise TelegramError(
            f'Не удалось отправить сообщение {error}')


def get_api_answer(current_timestamp):
    """Получить статус домашней работы."""
    timestamp = current_timestamp or int(time.time())
    params = {
        'url': ENDPOINT,
        'headers': HEADERS,
        'params': {'from_date': timestamp},
    }
    try:
        logging.info('Отправка запроса с параметрами')
        response = requests.get(**params)
        if response.status_code != HTTPStatus.OK:
            raise ENDPOINTError(response.status_code)
        return response.json()
    except Exception as error:
        raise ENDPOINTError(error)


def check_response(response):
    """Проверяет ответ API на соответствие документации"""
    logging.info('Проверка API')
    if not isinstance(response, dict):
        info = 'Ответ API не является dict'
        logging.error(info)
        raise TypeError(info)

    if 'homeworks' not in response or 'current_date' not in response:
        info = 'Нет ключа в API'
        logging.error(info)
        raise NoResponseFromAPI(info)

    homeworks = response.get('homeworks')
    if not isinstance(homeworks, list):
        info = 'homeworks не является словарем'
        logging.error(info)
        raise TypeError(info)
    return homeworks


def parse_status(homework):
    """Извлекает из информации о конкретной
    домашней работе статус этой работы."""
    logging.info('Проводим проверки информации о работе')
    homework_name = homework.get('homework_name')
    homework_verdict = homework.get('status')

    if 'homework_name' not in homework:
        info = 'Ключа homework_name нет в ответе API'
        logging.error(info)
        raise KeyError(info)

    if 'status' not in homework:
        info = 'Ключа status нет в ответе API'
        logging.error(info)
        raise KeyError(info)

    verdict = HOMEWORK_VERDICTS.get(homework_verdict)
    if homework_verdict not in HOMEWORK_VERDICTS:
        info = 'Неизвестный статус домашней работы'
        logging.error(info)
        raise KeyError(info)

    return f'Изменился статус проверки работы "{homework_name}". {verdict}'


def main():
    """Основная логика работы бота."""
    if not check_tokens():
        info = 'Отсутствуют необходимые переменные окружения'
        logging.critical(info)
        sys.exit(info)
    bot = telegram.Bot(token=TELEGRAM_TOKEN)
    current_timestamp = int(time.time())
    prev_message = ''

    while True:
        try:
            response = get_api_answer(current_timestamp)
            current_timestamp = response.get(
                'current_date', int(time.time())
            )
            homeworks = check_response(response)
            if homeworks:
                message = parse_status(homeworks[0])
            else:
                message = 'Нет новых статусов'
            if message != prev_message:
                send_message(bot, message)
                prev_message = message
            else:
                logging.info(message)

        except Exception as error:
            logging.error(error)
            message = f'Сбой в работе программы: {error}'
            if message != prev_message:
                send_message(bot, message)
                prev_message = message

        finally:
            time.sleep(RETRY_PERIOD)


if __name__ == '__main__':
    logging.basicConfig(
        level=logging.DEBUG,
        format=(
            '%(asctime)s, %(levelname)s, %(message)s'
        ),
        handlers=[logging.FileHandler('log.txt', encoding='UTF-8'),
                  logging.StreamHandler(sys.stdout)])
    main()
