# YouTube Async Collector

[![Python 3.10+](https://img.shields.io/badge/Python-3.10%2B-blue?logo=python)](https://www.python.org/)
[![PostgreSQL 15+](https://img.shields.io/badge/PostgreSQL-15%2B-blue?logo=postgresql)](https://www.postgresql.org/)
[![AsyncIO](https://img.shields.io/badge/Async-IO-blue?logo=asyncio)](https://docs.python.org/3/library/asyncio.html)
[![SQLAlchemy](https://img.shields.io/badge/SQLAlchemy-2.0%2B-blue?logo=sqlalchemy&logoColor=white)](https://www.sqlalchemy.org/)

Асинхронное приложение для сбора и анализа данных YouTube с графическим интерфейсом. Приложение позволяет получать метаданные о видео, каналах и комментариях, сохраняя их в реляционную базу данных с четкой структурой отношений

## 🚀 Быстрый старт

### Требования:
- Python 3.8+
- PostgreSQL 12+
- YouTube Data API v3 ключ

1. **Клонирование репозитория**:
```bash
git clone https://github.com/Lavrov-Aleksej/youtube-async-collector.git
cd youtube-async-collector
```
2. **Настройка базы данных**:

- Создайте базу данных в PostgreSQL (например, youtube_data)
- Настройте файл .env:
```bash
DB_HOST='localhost'
DB_PORT='5432'
DB_USER='postgres'
DB_NAME='youtube_data'
DB_PASSWORD='my_password'
```
3. **Настройка миграций**:
```bash
alembic init -t async migrations # инициализация Alembic
```
- В env.py (в папке migrations) замените содержимое на:
```python
import asyncio
from logging.config import fileConfig
from sqlalchemy import pool
from sqlalchemy.engine import Connection
from sqlalchemy.ext.asyncio import async_engine_from_config
from alembic import context

from models.database import Base, DATABASE_URL
from models.orm_model import Comment, Channel, Video

config = context.config
config.set_main_option("sqlalchemy.url", DATABASE_URL)

if config.config_file_name is not None:
    fileConfig(config.config_file_name)

target_metadata = Base.metadata

# Остальной код оставить без изменений 
```
- Создание и применение миграций:
```bash
alembic revision --autogenerate -m "Initial revision"
alembic upgrade head
```

## 🐘 Первое использование

1. После запуска приложения (`python main.py`) введите ваш **YouTube API ключ** в появившемся окне

2. Используйте параметры поиска в основном интерфейсе:
   - 🔍 **Поиск по запросу** (по умолчанию: "Евгения Потапова")
   - 📅 **Фильтрация по датам** (по умолчанию: 2005-02-14 - текущая дата)
   - 🔢 **Ограничение количества** результатов (по умолчанию: 42)
   - 📼 **Выбор категории видео** (по умолчанию: 1). [Подробнее читать здесь](https://gist.github.com/dgp/1b24bf2961521bd75d6c)

3. Основные действия:
   - Введите поисковой запрос и фильтры
   - Нажмите "**Search Videos**" для получения списка видео
   - Нажмите "**Process Videos**" для сохранения данных в базу данных
   - Нажмите "**Process Video by ID | URL**" для обработки видео по ID или URL (не требуется предварительная настройка фильтров)
  
> ⚠️ **Важно**: Для работы приложения требуется [YouTube Data API v3 ключ](https://console.cloud.google.com/apis/library/youtube.googleapis.com)

## 📂 Структура проекта
```bash
youtube-async-collector/
│ 
├── controllers/
│   ├── youtube_api_controller.py  # Логика работы с YouTube API
│   ├── database_controller.py     # Работа с PostgreSQL
├── models/
│   ├── async_youtube_model.py     # Валидация данных YouTube
│   ├── orm_model.py               # Модели SQLAlchemy
│   ├── database.py                # Подключение к БД
├── view/
│   ├── layout.py                  # Графический интерфейс Tkinter
├── config.py                      # Настройки окружения
├── main.py                        # Точка входа
├── requirements.txt               # Зависимости
```

## 🗄️ Зависимости в базе данных
**Видео → Каналы**:
- Одно видео принадлежит одному каналу (отношение "многие к одному").
- Канал может иметь множество видео.

**Комментарии → Видео**:
- Один комментарий может относиться к одному видео (отношение "многие к одному").
- Видео может иметь множество комментариев.

**Комментарии → Каналы**:
- Один комментарий принадлежит одному каналу (автору) (отношение "многие к одному").
- Канал может иметь множество комментариев.

**Комментарии → Комментарии (самоссылка)**:
- Древовидная структура комментариев, где комментарий может быть ответом на другой комментарий.

## 📈 ER-диаграмма модели данных:

```bash
+---------------------+         +---------------------+         +---------------------+
|     Channel         |1       *|       Video         |1       *|      Comment        |
+---------------------+---------+---------------------+---------+---------------------+
| PK: id_channel      |---------| PK: video_id        |---------| PK: comment_id      |
|     title_channel   |         |     title           |         |     text            |
|     keywords        |         |     description     |         |     comment_publish_|
|     description     |         |     category        |         |     date            |
|     view_count      |         |     view_count      |         |     like_count      |
|     subscription_   |         |     comment_count   |         |     reply_count     |
|     count           |         |     like_count      |         | FK: video_id        |
|     video_count     |         |     publish_date    |         | FK: commenter_      |
|     country         |         | FK: channel_id      |         | channel_id          |
|     account_        |         +---------------------+         | FK: parent_comment_ |
|     creation_date   |                   |                     | id                  |
+---------------------+                   |1                    +---------------------+
        | 1                               |                            /|\
        |                                 |                             |
        | has many                        | has many                    | 1
        |                                 |                             |
        |                                 |                            has many
        |                                 |                             |
        |                                 |                    +---------------------+
        |                                 |                    |  Comment-Comment    |
        |                                 |                    |  (Self-Reference)   |
        +---------------------------------+--------------------+---------------------+

Условные обозначения:
───────              
PK    Первичный ключ  FK    Внешний ключ    1     Связь "один"    *     Связь "много"   /_\\   Самореференция
```

## 💖 Благодарности

Спасибо команде [SMAPPNYU](https://github.com/SMAPPNYU) за библиотеку [youtube-data-api](https://github.com/SMAPPNYU/youtube-data-api), которая значительно упростила работу с YouTube API в нашем проекте
