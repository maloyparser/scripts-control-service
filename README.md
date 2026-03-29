# Scripts Control Service

Сервис для управления Python-скриптами через веб-интерфейс.

## Что реализовано

- 3 контейнера через Docker Compose:
  - **frontend** (Nginx + vanilla JS)
  - **backend** (FastAPI + APScheduler + async SQLAlchemy)
  - **db** (PostgreSQL)
- На фронте доступно:
  - просмотр списка скриптов;
  - изменение cron-расписания;
  - запуск/пауза скриптов;
  - просмотр логов скриптов.
- Логи пишутся в PostgreSQL.
- Используется асинхронность:
  - асинхронные API-обработчики FastAPI;
  - асинхронный планировщик;
  - асинхронные Python-скрипты (через `asyncio`, `aiohttp`).
- Зависимости зафиксированы по версиям в `backend/requirements.txt`.
- Добавлены тесты (`pytest`).

## Скрипты

Скрипты лежат в `backend/scripts`:

1. `monitor_resources.py`
   - раз в минуту (по умолчанию) делает HTTP-запросы к трём доменам;
   - пишет статусы ответов.
2. `disk_report.py`
   - выводит статистику использования диска.
3. `quote_fetcher.py`
   - получает цитату из внешнего ресурса GitHub Zen с мягким fallback при недоступности сети.

## Запуск

```bash
cp .env.example .env
docker compose up --build
```

После запуска:

- Фронт: `http://localhost:3000`
- Бэкенд (API): `http://localhost:8000`
- PostgreSQL: `localhost:5432`

## Основные API-методы

- `GET /` — сервисный корневой маршрут (статус + ссылки на `/docs` и `/api/health`).
- `GET /api/scripts` — список скриптов. Добавьте `?line_by_line=true`, чтобы получить NDJSON (один JSON-объект cron на строку).
- `PUT /api/scripts/{script_name}/cron` — изменить cron (поддерживаются алиасы: `minutely`, `hourly`, `daily`, `weekly`).
- `POST /api/scripts/{script_name}/start` — запустить.
- `POST /api/scripts/{script_name}/pause` — поставить на паузу.
- `GET /api/scripts/{script_name}/logs?limit=20` — получить логи.

## Тесты

Запуск тестов:

```bash
cd backend
pytest
```

## Примечания

- В демо-конфигурации включён CORS `*`.
- Для запуска на сервере используйте `.env` (пример: `.env.example`) и задавайте безопасные значения для паролей.
- Для production рекомендуется:
  - закрыть PostgreSQL от внешнего доступа;
  - использовать секреты и переменные окружения из защищённого хранилища;
  - ограничить CORS;
  - добавить авторизацию.
