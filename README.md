# Homework Bot 

## Бот для проверки домашней работы. 

Homework Bot - бот для отслеживания статуса проверки домашней работы на Яндекс.Практикум.

### Принцип работы API

Когда ревьюер проверяет вашу домашнюю работу, он присваивает ей один из статусов:

- работа принята на проверку
- работа возвращена для исправления ошибок
- работа принята

Стек: Python 3.9б python-dotenv 0.19.0б python-telegram-bot 13.7

### Как запустить проект:

- Клонировать репозиторий и перейти в него в командной строке:
```
git clone git@github.com:SammyTMG/homework_bot.git
```
- Переходим в папку:
```
cd homework_bot
```
- Cоздать и активировать виртуальное окружение:
 
 для MacOS
 ```
python3 -m venv venv
source venv/bin/activate
```
 для Windows
 ```
python -m venv venv
source venv/Scripts/activate
```
- Установить зависимости из файла requirements.txt:
```
python -m pip install --upgrade pip
pip install -r requirements.txt
```
- Записать в переменные окружения (файл .env) необходимые ключи:

токен профиля на Яндекс.Практикуме

токен телеграм-бота

свой ID в телеграме

- Запустить проект:
```
python homework.py
```
