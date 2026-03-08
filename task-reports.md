## T1 — Создать базовую структуру репозитория
- Дата: 2026-03-08 22:29 +0300
- Статус: done
- Коммит: `b7febb8`

Что сделано:
- созданы каталоги `backend/`, `frontend/`, `docs/`;
- добавлен корневой `.gitignore` с базовыми исключениями для Python, Django, Node и локальной среды;
- добавлен минимальный `README.md` с описанием проекта и целевого стека.

Проверка:
- ручная: структура репозитория соответствует договорённости — passed

Состояние запуска:
- для `T1` запуск приложения ещё не требуется; структура подготовлена для следующей задачи `T2`

## T2 — Поднять минимальный `docker-compose`
- Дата: 2026-03-08 22:39 +0300
- Статус: done
- Коммит: `a46fe11`

Что сделано:
- добавлен [`docker-compose.yml`](/home/vr/projects/idea-lab/docker-compose.yml) с сервисами `db`, `web`, `frontend`;
- для `db` выбран `postgres:16-alpine`, настроены базовые переменные окружения, volume и healthcheck через `pg_isready`;
- добавлены минимальные Dockerfile-заглушки для [`backend/Dockerfile`](/home/vr/projects/idea-lab/backend/Dockerfile) и [`frontend/Dockerfile`](/home/vr/projects/idea-lab/frontend/Dockerfile);
- созданы каталоги `backend/`, `frontend/`, `docs/` с placeholder-файлами, чтобы compose-контексты были валидны.

Проверка:
- `docker compose config` — passed
- `docker compose up --build -d` — passed
- `docker compose ps` — passed (`db`, `web`, `frontend` в состоянии `healthy`)

Состояние запуска:
- `docker compose up` поднимает минимальный стек из трёх сервисов без падения;
- проект остаётся запускаемым после задачи

## T3 — Инициализировать Django-проект
- Дата: 2026-03-08 22:54 +0300
- Статус: done
- Коммит: `3dc7394`

Что сделано:
- создан минимальный Django-проект в `backend/` с пакетом `config`, `manage.py` и базовыми settings;
- обновлён [`backend/Dockerfile`](/home/vr/projects/idea-lab/backend/Dockerfile): контейнер `web` теперь собирается на `python:3.12-slim` и устанавливает Django;
- добавлен [`backend/entrypoint.sh`](/home/vr/projects/idea-lab/backend/entrypoint.sh), который применяет миграции и автоматически создаёт суперпользователя `admin:admin`;
- обновлён [`docker-compose.yml`](/home/vr/projects/idea-lab/docker-compose.yml): сервис `web` запускает `python manage.py runserver 0.0.0.0:8000`, публикует порт `8000` и проходит healthcheck через `python manage.py check`.

Проверка:
- `docker compose up --build -d` — passed
- `docker compose logs web --tail 40` — passed (`System check identified no issues`, `Starting development server at http://0.0.0.0:8000/`)
- `python3 -c "import sqlite3; ..."` по `backend/db.sqlite3` — passed (суперпользователь `admin`, `is_superuser=1`)
- `docker compose ps` — passed (`web`, `db`, `frontend` в состоянии `healthy`)

Состояние запуска:
- `docker compose up` поднимает реальный Django backend вместо заглушки;
- проект остаётся запускаемым после задачи
