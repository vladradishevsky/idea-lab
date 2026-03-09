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

## T4 — Добавить backend health endpoint
- Дата: 2026-03-08 23:05 +0300
- Статус: done
- Коммит: `836ac37`

Что сделано:
- добавлен endpoint [`/api/health/`](/home/vr/projects/idea-lab/backend/config/urls.py), который возвращает JSON-ответ готовности приложения;
- реализован view [`health_check`](/home/vr/projects/idea-lab/backend/config/views.py) с ответом `{"status": "ok"}`;
- добавлен backend smoke-тест в [`backend/config/tests.py`](/home/vr/projects/idea-lab/backend/config/tests.py) на статус `200` и ожидаемый JSON.

Проверка:
- `docker compose exec -T web python manage.py test` — passed
- `docker compose exec -T web python manage.py shell -c "from django.test import Client; ..."` — passed (`200`, `{'status': 'ok'}`)
- `docker compose ps` — passed (`web`, `db`, `frontend` в состоянии `healthy`)

Состояние запуска:
- `docker compose up` продолжает поднимать проект без деградации;
- backend доступен с отдельным health endpoint для последующих задач

## T5 — Инициализировать React-приложение
- Дата: 2026-03-08 23:11 +0300
- Статус: done
- Коммит: `eb69d79`

Что сделано:
- обновлён [`frontend/Dockerfile`](/home/vr/projects/idea-lab/frontend/Dockerfile): контейнер `frontend` теперь собирается на `node:22-alpine`, устанавливает зависимости и запускает Vite dev server;
- добавлен минимальный React + Vite scaffold: [`frontend/package.json`](/home/vr/projects/idea-lab/frontend/package.json), [`frontend/vite.config.js`](/home/vr/projects/idea-lab/frontend/vite.config.js), [`frontend/index.html`](/home/vr/projects/idea-lab/frontend/index.html), [`frontend/src/App.jsx`](/home/vr/projects/idea-lab/frontend/src/App.jsx), [`frontend/src/main.jsx`](/home/vr/projects/idea-lab/frontend/src/main.jsx), [`frontend/src/styles.css`](/home/vr/projects/idea-lab/frontend/src/styles.css);
- обновлён [`docker-compose.yml`](/home/vr/projects/idea-lab/docker-compose.yml): сервис `frontend` публикует порт `5173`, запускает `npm run dev` и использует отдельный volume `frontend_node_modules`, чтобы bind mount не затирал установленные зависимости;
- обновлён lockfile [`frontend/package-lock.json`](/home/vr/projects/idea-lab/frontend/package-lock.json) для воспроизводимой установки зависимостей.

Проверка:
- `docker compose up --build -d` — passed
- `docker compose logs frontend --tail 40` — passed (`VITE v5.4.14 ready`, dev server слушает `http://localhost:5173/`)
- `docker compose exec -T frontend wget -q -O - http://127.0.0.1:5173` — passed (возвращается HTML стартовой страницы)
- `docker compose ps` — passed (`db`, `web`, `frontend` в состоянии `healthy`)

Состояние запуска:
- `docker compose up` поднимает реальный frontend вместо заглушки;
- проект остаётся запускаемым после задачи

## T6 — Сделать стартовую frontend-страницу и прокинуть env
- Дата: 2026-03-08 23:18 +0300
- Статус: done
- Коммит: `0bf9702`

Что сделано:
- обновлён [`docker-compose.yml`](/home/vr/projects/idea-lab/docker-compose.yml): для сервиса `frontend` добавлена переменная окружения `VITE_API_BASE_URL=http://localhost:8000`;
- доработана стартовая страница в [`frontend/src/App.jsx`](/home/vr/projects/idea-lab/frontend/src/App.jsx): теперь она показывает явный статус готовности frontend и выводит базовый URL backend API из env;
- обновлены стили в [`frontend/src/styles.css`](/home/vr/projects/idea-lab/frontend/src/styles.css), чтобы статусные блоки были читаемыми на стартовом экране.

Проверка:
- `docker compose up --build -d` — passed
- `docker compose logs frontend --tail 40` — passed (`VITE v5.4.14 ready`, dev server слушает `http://localhost:5173/`)
- Playwright smoke-check `http://127.0.0.1:5173/` — passed (страница показывает `Frontend is ready for development` и `http://localhost:8000`)
- `docker compose ps` — passed (`db`, `web`, `frontend` в состоянии `healthy`)

Состояние запуска:
- стартовая frontend-страница открывается на `localhost:5173` и показывает ожидаемый статус;
- проект остаётся запускаемым после задачи

## T7 — Подключить PostgreSQL к Django
- Дата: 2026-03-08 23:24 +0300
- Статус: done
- Коммит: `1e1106a`

Что сделано:
- обновлён [`backend/config/settings.py`](/home/vr/projects/idea-lab/backend/config/settings.py): Django переведён с SQLite на PostgreSQL и читает параметры подключения из env;
- обновлён [`docker-compose.yml`](/home/vr/projects/idea-lab/docker-compose.yml): сервис `web` теперь получает явные `POSTGRES_*` переменные для подключения к контейнеру `db`;
- обновлён [`backend/requirements.txt`](/home/vr/projects/idea-lab/backend/requirements.txt): добавлен драйвер `psycopg[binary]` для работы Django с PostgreSQL;
- проверено, что при старте контейнера `web` миграции применяются в БД `idea_lab` внутри PostgreSQL.

Проверка:
- `docker compose config` — passed
- `docker compose up --build -d` — passed
- `docker compose logs web --tail 60` — passed (миграции применены, `System check identified no issues`, dev server стартовал)
- `docker compose exec -T web python manage.py shell -c "from django.conf import settings; from django.db import connection; ..."` — passed (`django.db.backends.postgresql`, host `db`, DB `idea_lab`)
- `docker compose exec -T db psql -U idea_lab -d idea_lab -c "\\dt"` — passed (таблицы Django созданы в PostgreSQL)
- `docker compose exec -T web python manage.py test` — passed
- `docker compose ps` — passed (`db`, `web`, `frontend` в состоянии `healthy`)

Состояние запуска:
- `docker compose up` поднимает стек с backend на PostgreSQL вместо SQLite;
- проект остаётся запускаемым после задачи

## T8 — Настроить базовые команды разработки
- Дата: 2026-03-08 23:31 +0300
- Статус: done
- Коммит: `c303fb9`

Что сделано:
- обновлён [`README.md`](/home/vr/projects/idea-lab/README.md): добавлены требования к окружению, быстрый старт, адреса сервисов, учётные данные admin и базовые команды разработки;
- в README описаны команды для запуска, остановки, пересборки, просмотра статуса контейнеров, логов и backend-тестов;
- проверено, что сценарий из README позволяет заново остановить и поднять проект локально.

Проверка:
- `docker compose down` — passed
- `docker compose up --build -d` — passed
- `docker compose ps` — passed (`db`, `web`, `frontend` в состоянии `healthy`)
- `docker compose logs web --tail 40` — passed (backend стартовал без ошибок)
- `docker compose logs frontend --tail 20` — passed (Vite dev server поднялся на `http://localhost:5173/`)
- `docker compose exec -T web python manage.py test` — passed

Состояние запуска:
- README покрывает базовые dev-команды для локальной работы со стеком;
- проект остаётся запускаемым после задачи

## T9 — Создать Django app для доменной логики
- Дата: 2026-03-08 23:41 +0300
- Статус: done
- Коммит: `3f697a9`

Что сделано:
- создано Django-приложение [`backend/ideas/`](/home/vr/projects/idea-lab/backend/ideas) для будущей доменной логики идей, источников и API;
- приложение подключено в [`backend/config/settings.py`](/home/vr/projects/idea-lab/backend/config/settings.py) через `ideas.apps.IdeasConfig`;
- добавлен минимальный smoke-тест в [`backend/ideas/tests.py`](/home/vr/projects/idea-lab/backend/ideas/tests.py), который подтверждает регистрацию app в Django.

Проверка:
- `docker compose exec -T web python manage.py check` — passed
- `docker compose exec -T web python manage.py test` — passed
- `docker compose logs web --tail 40` — passed (backend перезагрузился после подключения app без ошибок)
- `docker compose ps` — passed (`db`, `web`, `frontend` в состоянии `healthy`)

Состояние запуска:
- backend импортирует новое приложение `ideas` без ошибок;
- проект остаётся запускаемым после задачи

## T10 — Реализовать модель `SourceSystem`
- Дата: 2026-03-08 23:45 +0300
- Статус: done
- Коммит: `6f693f6`

Что сделано:
- в [`backend/ideas/models.py`](/home/vr/projects/idea-lab/backend/ideas/models.py) добавлена модель `SourceSystem` с полями `name`, `base_url`, `is_active`, `created_at`, `updated_at`;
- добавлена миграция [`backend/ideas/migrations/0001_initial.py`](/home/vr/projects/idea-lab/backend/ideas/migrations/0001_initial.py) для создания таблицы `ideas_sourcesystem`;
- в [`backend/ideas/tests.py`](/home/vr/projects/idea-lab/backend/ideas/tests.py) добавлен backend-тест на создание и чтение записи `SourceSystem` через ORM.

Проверка:
- `docker compose exec -T web python manage.py migrate` — passed
- `docker compose exec -T web python manage.py check` — passed
- `docker compose exec -T web python manage.py test` — passed
- `docker compose exec -T db psql -U idea_lab -d idea_lab -c "\\d ideas_sourcesystem"` — passed (таблица создана в PostgreSQL)
- `docker compose ps` — passed (`db`, `web`, `frontend` в состоянии `healthy`)

Состояние запуска:
- backend стартует с применённой миграцией `ideas.0001_initial`;
- проект остаётся запускаемым после задачи

## T11 — Реализовать enum статусов и модель `Stage` без сложной логики
- Дата: 2026-03-08 23:50 +0300
- Статус: done
- Коммит: `328a02d`

Что сделано:
- в [`backend/ideas/models.py`](/home/vr/projects/idea-lab/backend/ideas/models.py) добавлен enum `StageStatus` и модель `Stage` со всеми полями из PRD;
- добавлена миграция [`backend/ideas/migrations/0002_stage.py`](/home/vr/projects/idea-lab/backend/ideas/migrations/0002_stage.py) для создания таблицы `ideas_stage`;
- в [`backend/ideas/tests.py`](/home/vr/projects/idea-lab/backend/ideas/tests.py) добавлен backend-тест, который проверяет создание `Stage` с дефолтным статусом `new`.

Проверка:
- `docker compose exec -T web python manage.py migrate` — passed
- `docker compose exec -T web python manage.py check` — passed
- `docker compose exec -T web python manage.py test` — passed
- `docker compose exec -T db psql -U idea_lab -d idea_lab -c "\\d ideas_stage"` — passed (таблица создана в PostgreSQL)
- `docker compose ps` — passed (`db`, `web`, `frontend` в состоянии `healthy`)

Состояние запуска:
- backend стартует с применённой миграцией `ideas.0002_stage`;
- проект остаётся запускаемым после задачи

## T12 — Добавить ограничения и индексы для `Stage`
- Дата: 2026-03-09 23:53 +0300
- Статус: done
- Коммит: `ac3ecf0`

Что сделано:
- в [`backend/ideas/models.py`](/home/vr/projects/idea-lab/backend/ideas/models.py) для `Stage` добавлены `UniqueConstraint` по паре (`source_system`, `source_id`), `CheckConstraint` для диапазона `0..100` и индексы по `status`, `created_at`, `is_filled`, (`status`, `created_at`);
- добавлены валидаторы `MinValueValidator` и `MaxValueValidator` для полей `seo_kd_percent` и `implementation_ease_percent`;
- создана миграция [`backend/ideas/migrations/0003_stage_constraints.py`](/home/vr/projects/idea-lab/backend/ideas/migrations/0003_stage_constraints.py);
- в [`backend/ideas/tests.py`](/home/vr/projects/idea-lab/backend/ideas/tests.py) добавлены тесты на уникальность `(source_system, source_id)` и на отклонение процентов вне диапазона.

Проверка:
- `docker compose exec -T web python manage.py migrate` — passed
- `docker compose exec -T web python manage.py check` — passed
- `docker compose exec -T web python manage.py test` — passed
- `docker compose exec -T db psql -U idea_lab -d idea_lab -c "\\d ideas_stage"` — passed (у таблицы есть уникальное ограничение, check constraints и индексы)
- `docker compose ps` — passed (`db`, `web`, `frontend` в состоянии `healthy`)

Состояние запуска:
- backend стартует с применённой миграцией `ideas.0003_stage_constraints`;
- проект остаётся запускаемым после задачи

## T13 — Подключить модели в Django Admin
- Дата: 2026-03-09 00:01 +0300
- Статус: done
- Коммит: `b56a2df`

Что сделано:
- в [`backend/ideas/admin.py`](/home/vr/projects/idea-lab/backend/ideas/admin.py) зарегистрированы `SourceSystem` и `Stage` через `ModelAdmin`;
- для `SourceSystem` настроены `list_display`, `list_filter`, `search_fields` и сортировка;
- для `Stage` настроены `list_display`, фильтры по служебным полям, поиск по ключевым полям, `autocomplete_fields` для источника и `list_select_related`.

Проверка:
- `docker compose exec -T web python manage.py check` — passed
- `docker compose exec -T web python manage.py shell -c "from django.contrib import admin; ..."` — passed (`SourceSystem` и `Stage` зарегистрированы в admin site)

Состояние запуска:
- backend продолжает стартовать с подключёнными моделями в Django Admin;
- проект остаётся запускаемым после задачи

## T14 — Добавить начальные `source_system`
- Дата: 2026-03-09 00:00 +0300
- Статус: done
- Коммит: `8c298a6`

Что сделано:
- добавлена миграция [`backend/ideas/migrations/0004_seed_source_systems.py`](/home/vr/projects/idea-lab/backend/ideas/migrations/0004_seed_source_systems.py) со стартовыми источниками из PRD: `Kwork`, `Freelance.ru`, `FL.ru`;
- миграция реализована через `RunPython` и использует `update_or_create`, чтобы при повторном применении поддерживать ожидаемые значения `base_url` и `is_active`;
- в [`backend/ideas/tests.py`](/home/vr/projects/idea-lab/backend/ideas/tests.py) добавлен тест, который проверяет наличие стартовых `source_system` после миграций.

Проверка:
- `docker compose exec -T web python manage.py test` — passed
- `docker compose exec -T web python manage.py shell -c "from ideas.models import SourceSystem; ..."` — passed

Состояние запуска:
- backend стартует с предзаполненным справочником источников;
- проект остаётся запускаемым после задачи

## T15 — Подключить DRF и базовую конфигурацию API
- Дата: 2026-03-09 00:00 +0300
- Статус: done
- Коммит: `195a9b1`

Что сделано:
- в [`backend/requirements.txt`](/home/vr/projects/idea-lab/backend/requirements.txt) добавлен `djangorestframework`, а в [`backend/config/settings.py`](/home/vr/projects/idea-lab/backend/config/settings.py) подключён `rest_framework` и базовые renderer classes;
- базовый API-роутинг вынесен в [`backend/config/api_urls.py`](/home/vr/projects/idea-lab/backend/config/api_urls.py) и подключён через `/api/` в [`backend/config/urls.py`](/home/vr/projects/idea-lab/backend/config/urls.py);
- в [`backend/config/views.py`](/home/vr/projects/idea-lab/backend/config/views.py) добавлены DRF views для API root и health endpoint, а в [`backend/config/tests.py`](/home/vr/projects/idea-lab/backend/config/tests.py) — smoke-тесты на `/api/` и `/api/health/`.

Проверка:
- `docker compose build web` — passed
- `docker compose up -d web` — passed
- `docker compose exec -T web python manage.py test` — passed
- `docker compose exec -T web python manage.py check` — passed
- `docker compose exec -T web python manage.py shell -c "from django.test import Client; ..."` — passed

Состояние запуска:
- backend стартует с подключённым DRF и базовым `/api/` роутингом;
- проект остаётся запускаемым после задачи

## T16 — Реализовать serializer для ingestion одного объекта
- Дата: 2026-03-09 00:00 +0300
- Статус: done
- Коммит: `b13db82`

Что сделано:
- добавлен serializer [`backend/ideas/serializers.py`](/home/vr/projects/idea-lab/backend/ideas/serializers.py) для ingestion одного объекта на базе модели `Stage`;
- в serializer явно зафиксированы обязательные поля `source_system`, `source_id`, `source_url`, `title` и опциональные `description`, `category`;
- в [`backend/ideas/tests.py`](/home/vr/projects/idea-lab/backend/ideas/tests.py) добавлены тесты на успешную валидацию корректного payload и на ошибку при отсутствии обязательных полей.

Проверка:
- `docker compose exec -T web python manage.py test` — passed
- `docker compose exec -T web python manage.py shell -c "from ideas.serializers import StageIngestionSerializer; ..."` — passed

Состояние запуска:
- backend стартует с готовым ingestion serializer для следующего API endpoint;
- проект остаётся запускаемым после задачи

## T17 — Реализовать ingestion endpoint для одного объекта
- Дата: 2026-03-09 00:00 +0300
- Статус: done
- Коммит: `553f660`

Что сделано:
- добавлен POST endpoint `/api/ingest/` в [`backend/ideas/views.py`](/home/vr/projects/idea-lab/backend/ideas/views.py), который валидирует payload через `StageIngestionSerializer` и создаёт одну запись `Stage`;
- endpoint подключён в [`backend/config/api_urls.py`](/home/vr/projects/idea-lab/backend/config/api_urls.py), а [`backend/config/views.py`](/home/vr/projects/idea-lab/backend/config/views.py) обновлён так, чтобы API root показывал ссылку на ingestion endpoint;
- в [`backend/ideas/tests.py`](/home/vr/projects/idea-lab/backend/ideas/tests.py) добавлен backend-тест, который проверяет успешное создание записи через API и дефолтный статус `new`.

Проверка:
- `docker compose exec -T web python manage.py test` — passed
- `docker compose exec -T web python manage.py shell -c "from django.test import Client; ..."` — passed

Состояние запуска:
- backend умеет принимать одну идею через ingestion API;
- проект остаётся запускаемым после задачи

## T18 — Добавить дедупликацию ingestion
- Дата: 2026-03-09 00:00 +0300
- Статус: done
- Коммит: `ddd0250`

Что сделано:
- в [`backend/ideas/views.py`](/home/vr/projects/idea-lab/backend/ideas/views.py) добавлена дедупликация ingestion по паре `source_system + source_id` перед созданием записи;
- endpoint `/api/ingest/` теперь возвращает счётчики `created` и `ignored`, чтобы контракт был готов к следующему расширению на batch ingestion;
- в [`backend/ideas/tests.py`](/home/vr/projects/idea-lab/backend/ideas/tests.py) добавлен тест, который подтверждает игнорирование дубликата и отсутствие обновления существующей записи.

Проверка:
- `docker compose exec -T web python manage.py test` — passed
- `docker compose exec -T web python manage.py shell -c "from django.test import Client; ..."` — passed

Состояние запуска:
- backend принимает одну идею и игнорирует дубликаты без обновления существующей записи;
- проект остаётся запускаемым после задачи

## T19 — Поддержать ingestion массива объектов
- Дата: 2026-03-09 00:00 +0300
- Статус: done
- Коммит: `2a0f90e`

Что сделано:
- в [`backend/ideas/views.py`](/home/vr/projects/idea-lab/backend/ideas/views.py) endpoint `/api/ingest/` расширен на приём как одного объекта, так и массива объектов;
- batch ingestion использует общий serializer в режиме `many=True`, считает суммарные `created` и `ignored` и сохраняет только уникальные записи;
- в [`backend/ideas/tests.py`](/home/vr/projects/idea-lab/backend/ideas/tests.py) добавлен тест на batch payload со смесью новых и дублирующихся записей.

Проверка:
- `docker compose exec -T web python manage.py test` — passed
- `docker compose exec -T web python manage.py shell -c "from django.test import Client; ..."` — passed

Состояние запуска:
- backend принимает идеи по одной и пачкой, корректно суммируя `created` и `ignored`;
- проект остаётся запускаемым после задачи

## T20 — Добавить логирование ingest-операций
- Дата: 2026-03-09 00:00 +0300
- Статус: done
- Коммит: `dd489cc`

Что сделано:
- в [`backend/ideas/views.py`](/home/vr/projects/idea-lab/backend/ideas/views.py) добавлено логирование ingest-операций через logger `ideas.ingest` для успешной обработки и ошибок валидации;
- в [`backend/config/settings.py`](/home/vr/projects/idea-lab/backend/config/settings.py) добавлена базовая logging-конфигурация с выводом `ideas.ingest` в консоль контейнера;
- в [`backend/ideas/tests.py`](/home/vr/projects/idea-lab/backend/ideas/tests.py) добавлены тесты, которые проверяют логирование результатов `created/ignored` и логирование ошибок валидации.

Проверка:
- `docker compose exec -T web python manage.py test` — passed
- `docker compose exec -T web python manage.py shell -c "from django.test import Client; ..."` — passed

Состояние запуска:
- ingest-операции логируются в dev-режиме с результатами обработки и ошибками валидации;
- проект остаётся запускаемым после задачи

## T21 — Реализовать endpoint списка идей с пагинацией
- Дата: 2026-03-09 00:00 +0300
- Статус: done
- Коммит: `0700333`

Что сделано:
- добавлен endpoint `/api/stages/` в [`backend/ideas/views.py`](/home/vr/projects/idea-lab/backend/ideas/views.py) на базе `ListAPIView` с серверной пагинацией;
- добавлен serializer [`StageListSerializer`](/home/vr/projects/idea-lab/backend/ideas/serializers.py) для списка `Stage` и подключён маршрут в [`backend/config/api_urls.py`](/home/vr/projects/idea-lab/backend/config/api_urls.py);
- API root в [`backend/config/views.py`](/home/vr/projects/idea-lab/backend/config/views.py) обновлён ссылкой на список, а в [`backend/ideas/tests.py`](/home/vr/projects/idea-lab/backend/ideas/tests.py) добавлены тесты на пагинацию и дефолтный порядок `created_at ASC`.

Проверка:
- `docker compose exec -T web python manage.py test` — passed
- `docker compose exec -T web python manage.py shell -c "from django.test import Client; ..."` — passed

Состояние запуска:
- backend отдаёт пагинированный список идей с дефолтной сортировкой по времени создания;
- проект остаётся запускаемым после задачи

## T22 — Добавить фильтры списка идей
- Дата: 2026-03-09 19:31 +0300
- Статус: done
- Коммит: `4ea8a56`

Что сделано:
- в [`backend/ideas/serializers.py`](/home/vr/projects/idea-lab/backend/ideas/serializers.py) добавлен `StageListFilterSerializer` для валидации query params списка идей;
- в [`backend/ideas/views.py`](/home/vr/projects/idea-lab/backend/ideas/views.py) `StageListView` расширен фильтрами `status`, `source_system_id`, `category`, `is_filled` и `include_rejected`;
- по умолчанию `/api/stages/` теперь скрывает записи со статусом `rejected`, но позволяет явно запрашивать их через `status=rejected` или `include_rejected=true`;
- в [`backend/ideas/tests.py`](/home/vr/projects/idea-lab/backend/ideas/tests.py) добавлены backend-тесты на каждый обязательный фильтр и на их типовое сочетание.

Проверка:
- `docker compose exec -T web python manage.py test` — passed
- `docker compose exec -T web python manage.py shell -c "..."` — passed (`/api/stages/` вернул `14`, `/api/stages/?include_rejected=true` вернул `15`)

Состояние запуска:
- backend продолжает отдавать пагинированный список идей и теперь поддерживает обязательные фильтры из PRD;
- проект остаётся запускаемым после задачи

## T23 — Реализовать endpoint получения одной идеи
- Дата: 2026-03-09 19:46 +0300
- Статус: done
- Коммит: `c5205fb`

Что сделано:
- в [`backend/ideas/serializers.py`](/home/vr/projects/idea-lab/backend/ideas/serializers.py) добавлен `StageDetailSerializer` с полным набором полей карточки идеи;
- в [`backend/ideas/views.py`](/home/vr/projects/idea-lab/backend/ideas/views.py) добавлен `StageDetailView` на базе `RetrieveAPIView`;
- в [`backend/config/api_urls.py`](/home/vr/projects/idea-lab/backend/config/api_urls.py) подключён маршрут `/api/stages/<id>/`;
- в [`backend/config/views.py`](/home/vr/projects/idea-lab/backend/config/views.py) API root дополнен ссылкой на detail endpoint;
- в [`backend/ideas/tests.py`](/home/vr/projects/idea-lab/backend/ideas/tests.py) добавлен backend-тест на получение полной карточки по `id`, а в [`backend/config/tests.py`](/home/vr/projects/idea-lab/backend/config/tests.py) обновлён контракт API root.

Проверка:
- `docker compose exec -T web python manage.py test` — passed
- `docker compose exec -T web python manage.py shell -c "..."` — passed (`GET /api/stages/<id>/` вернул `200`, корректный `id`, `custom_title` и `status`)

Состояние запуска:
- backend продолжает подниматься в compose-окружении и теперь умеет отдавать полную карточку одной идеи;
- проект остаётся запускаемым после задачи

## T24 — Реализовать action быстрой смены статуса `accepted/rejected`
- Дата: 2026-03-09 19:50 +0300
- Статус: done
- Коммит: `2104c0f`

Что сделано:
- в [`backend/ideas/serializers.py`](/home/vr/projects/idea-lab/backend/ideas/serializers.py) добавлен `StageStatusUpdateSerializer`, который принимает только `accepted` и `rejected`;
- в [`backend/ideas/views.py`](/home/vr/projects/idea-lab/backend/ideas/views.py) добавлен `StageStatusUpdateView` для quick filter action;
- action разрешает быстрый перевод только для идей со статусом `new`, а недопустимые переходы возвращают `400`;
- в [`backend/config/api_urls.py`](/home/vr/projects/idea-lab/backend/config/api_urls.py) подключён маршрут `/api/stages/<id>/status/`, а [`backend/config/views.py`](/home/vr/projects/idea-lab/backend/config/views.py) и [`backend/config/tests.py`](/home/vr/projects/idea-lab/backend/config/tests.py) обновлены под новый endpoint;
- в [`backend/ideas/tests.py`](/home/vr/projects/idea-lab/backend/ideas/tests.py) добавлены backend-тесты на `new -> accepted`, `new -> rejected` и отклонение недопустимого перехода.

Проверка:
- `docker compose exec -T web python manage.py test` — passed
- `docker compose exec -T web python manage.py shell -c "..."` — passed (`POST /api/stages/<id>/status/` вернул `200` и статус `accepted`)

Состояние запуска:
- backend продолжает подниматься в compose-окружении и теперь поддерживает quick filter action для смены статуса;
- проект остаётся запускаемым после задачи

## T25 — Реализовать обновление карточки проработки
- Дата: 2026-03-09 19:55 +0300
- Статус: done
- Коммит: `ebdcbe1`

Что сделано:
- в [`backend/ideas/serializers.py`](/home/vr/projects/idea-lab/backend/ideas/serializers.py) добавлен `StageElaborationUpdateSerializer` только для полей проработки;
- в [`backend/ideas/views.py`](/home/vr/projects/idea-lab/backend/ideas/views.py) добавлен endpoint `PATCH /api/stages/<id>/elaboration/` для частичного обновления карточки;
- endpoint явно отклоняет служебные и неразрешённые поля, чтобы контракт редактирования не смешивался со статусами, `is_filled` и source-данными;
- в [`backend/config/api_urls.py`](/home/vr/projects/idea-lab/backend/config/api_urls.py), [`backend/config/views.py`](/home/vr/projects/idea-lab/backend/config/views.py) и [`backend/config/tests.py`](/home/vr/projects/idea-lab/backend/config/tests.py) добавлен новый маршрут и обновлён API root;
- в [`backend/ideas/tests.py`](/home/vr/projects/idea-lab/backend/ideas/tests.py) добавлены backend-тесты на успешное сохранение полей проработки и на отклонение служебных полей.

Проверка:
- `docker compose exec -T web python manage.py test` — passed
- `docker compose exec -T web python manage.py shell -c "..."` — passed (`PATCH /api/stages/<id>/elaboration/` вернул `200` для полей проработки и `400` для `status`)

Состояние запуска:
- backend продолжает подниматься в compose-окружении и теперь поддерживает отдельный контракт обновления карточки проработки;
- проект остаётся запускаемым после задачи

## T26 — Добавить автопереход в `in_progress`
- Дата: 2026-03-09 19:56 +0300
- Статус: done
- Коммит: `40a72e2`

Что сделано:
- в [`backend/ideas/views.py`](/home/vr/projects/idea-lab/backend/ideas/views.py) добавлена логика автоперехода в `in_progress` после `PATCH /api/stages/<id>/elaboration/`;
- если у карточки `is_filled=false` и после сохранения заполнено хотя бы одно поле проработки, статус автоматически меняется на `in_progress`;
- логика не затрагивает уже заполненные карточки с `is_filled=true`, чтобы не смешивать `T26` с будущей задачей `T27`;
- в [`backend/ideas/tests.py`](/home/vr/projects/idea-lab/backend/ideas/tests.py) обновлены и добавлены backend-тесты на переход `accepted -> in_progress`, `new -> in_progress` и на отсутствие автоперехода при `is_filled=true`.

Проверка:
- `docker compose exec -T web python manage.py test` — passed
- `docker compose exec -T web python manage.py shell -c "..."` — passed (`PATCH /api/stages/<id>/elaboration/` вернул `200` и статус `in_progress`)

Состояние запуска:
- backend продолжает подниматься в compose-окружении и теперь автоматически выставляет `in_progress` при начале проработки;
- проект остаётся запускаемым после задачи

## T27 — Добавить переход в `completed` и фиксацию `filled_at`
- Дата: 2026-03-09 19:58 +0300
- Статус: done
- Коммит: `b1efe89`

Что сделано:
- в [`backend/ideas/serializers.py`](/home/vr/projects/idea-lab/backend/ideas/serializers.py) `StageElaborationUpdateSerializer` расширен полем `is_filled`, чтобы завершение карточки происходило через тот же update endpoint;
- в [`backend/ideas/views.py`](/home/vr/projects/idea-lab/backend/ideas/views.py) добавлена логика: при `is_filled=true` статус становится `completed`, а `filled_at` фиксируется текущей датой, если раньше не был установлен;
- повторные обновления уже завершённой карточки сохраняют существующий `filled_at` и не перетирают его новой датой;
- в [`backend/ideas/tests.py`](/home/vr/projects/idea-lab/backend/ideas/tests.py) добавлены backend-тесты на переход в `completed`, фиксацию `filled_at`, сохранение уже существующей даты завершения и запрет ручного обновления `filled_at`.

Проверка:
- `docker compose exec -T web python manage.py test` — passed
- `docker compose exec -T web python manage.py shell -c "..."` — passed (`PATCH /api/stages/<id>/elaboration/` вернул `200`, статус `completed` и дату в `filled_at`)

Состояние запуска:
- backend продолжает подниматься в compose-окружении и теперь поддерживает полный переход в `completed` через ручную установку `is_filled=true`;
- проект остаётся запускаемым после задачи

## T28 — Реализовать dashboard aggregates endpoint
- Дата: 2026-03-09 20:00 +0300
- Статус: done
- Коммит: `718c906`

Что сделано:
- в [`backend/ideas/views.py`](/home/vr/projects/idea-lab/backend/ideas/views.py) добавлен `StageDashboardAggregatesView`, который считает количество идей по всем статусам из PRD;
- endpoint возвращает стабильный JSON с ключами `new`, `accepted`, `rejected`, `in_progress`, `completed`, даже когда часть значений равна нулю;
- в [`backend/config/api_urls.py`](/home/vr/projects/idea-lab/backend/config/api_urls.py) подключён маршрут `/api/dashboard/aggregates/`, а [`backend/config/views.py`](/home/vr/projects/idea-lab/backend/config/views.py) и [`backend/config/tests.py`](/home/vr/projects/idea-lab/backend/config/tests.py) обновлены под новый endpoint;
- в [`backend/ideas/tests.py`](/home/vr/projects/idea-lab/backend/ideas/tests.py) добавлен backend-тест, который проверяет точные counts по статусам.

Проверка:
- `docker compose exec -T web python manage.py test` — passed
- `docker compose exec -T web python manage.py shell -c "..."` — passed (`GET /api/dashboard/aggregates/` вернул агрегаты со статусами `new`, `accepted`, `rejected`, `in_progress`, `completed`)

Состояние запуска:
- backend продолжает подниматься в compose-окружении и теперь умеет отдавать агрегаты для dashboard;
- проект остаётся запускаемым после задачи

## T29 — Настроить frontend routing
- Дата: 2026-03-09 20:18 +0300
- Статус: done
- Коммит: `7c43b10`

Что сделано:
- в [`frontend/package.json`](/home/vr/projects/idea-lab/frontend/package.json) и lockfile добавлена зависимость `react-router-dom` для клиентского роутинга;
- в [`frontend/src/main.jsx`](/home/vr/projects/idea-lab/frontend/src/main.jsx) приложение обёрнуто в `BrowserRouter`;
- в [`frontend/src/App.jsx`](/home/vr/projects/idea-lab/frontend/src/App.jsx) настроены маршруты `/`, `/filter`, `/stages` и добавлены отдельные route-specific страницы-заглушки;
- в [`frontend/src/styles.css`](/home/vr/projects/idea-lab/frontend/src/styles.css) обновлены стили стартового экрана под новый routing shell и route placeholders.

Проверка:
- `docker compose exec -T frontend npm install react-router-dom@6.30.1` — passed
- `docker compose logs frontend --tail 60` — passed (`react-router-dom` оптимизирован Vite, dev server продолжает работать)
- Playwright smoke-check `http://127.0.0.1:5173/`, `http://127.0.0.1:5173/filter`, `http://127.0.0.1:5173/stages` — passed (каждый маршрут рендерит свой заголовок и текущий pathname)
- `docker compose ps` — passed (`db`, `web`, `frontend` в состоянии `healthy`)

Состояние запуска:
- frontend продолжает подниматься в compose-окружении и теперь поддерживает базовые клиентские маршруты для dashboard, quick filter и elaboration;
- проект остаётся запускаемым после задачи

## T30 — Собрать базовый layout и навигацию
- Дата: 2026-03-09 20:21 +0300
- Статус: done
- Коммит: `56ad043`

Что сделано:
- в [`frontend/src/App.jsx`](/home/vr/projects/idea-lab/frontend/src/App.jsx) добавлен общий `AppLayout` с брендовым header-блоком и primary navigation;
- маршруты `/`, `/filter`, `/stages` переведены на единый shell, а навигация собрана на `NavLink` с активным состоянием для текущей страницы;
- в [`frontend/src/styles.css`](/home/vr/projects/idea-lab/frontend/src/styles.css) добавлены стили header, pills-навигации, общего page layout и адаптивного поведения для узких экранов.

Проверка:
- `docker compose logs frontend --tail 60` — passed (Vite dev server продолжает работать после обновления layout)
- Playwright smoke-check `http://127.0.0.1:5173/` — passed (в шапке рендерятся ссылки `Dashboard`, `Quick Filter`, `Elaboration`)
- Playwright navigation click-check `/ -> /filter -> /stages -> /` — passed (клики по nav-ссылкам меняют URL, контент страницы и активную ссылку)
- `docker compose ps` — passed (`db`, `web`, `frontend` в состоянии `healthy`)

Состояние запуска:
- frontend продолжает подниматься в compose-окружении и теперь имеет общий layout и рабочую навигацию между тремя основными разделами;
- проект остаётся запускаемым после задачи

## T31 — Настроить базовый API client на frontend
- Дата: 2026-03-09 20:26 +0300
- Статус: done
- Коммит: `5abf8b5`

Что сделано:
- добавлен базовый frontend API layer в [`frontend/src/api/client.js`](/home/vr/projects/idea-lab/frontend/src/api/client.js) с общим `fetch`-wrapper, JSON-обработкой и единым `ApiError`;
- добавлены endpoint-функции в [`frontend/src/api/resources.js`](/home/vr/projects/idea-lab/frontend/src/api/resources.js) и общий async hook в [`frontend/src/hooks/useApiRequest.js`](/home/vr/projects/idea-lab/frontend/src/hooks/useApiRequest.js);
- в [`frontend/src/App.jsx`](/home/vr/projects/idea-lab/frontend/src/App.jsx) добавлен общий `RequestSummary` со стандартными состояниями `loading/error/success`, подключённый к реальным backend endpoint'ам;
- в [`frontend/vite.config.js`](/home/vr/projects/idea-lab/frontend/vite.config.js) настроен dev proxy для `/api`, а в [`docker-compose.yml`](/home/vr/projects/idea-lab/docker-compose.yml) frontend переведён на same-origin схему без прямого cross-origin доступа к backend;
- в [`frontend/src/styles.css`](/home/vr/projects/idea-lab/frontend/src/styles.css) добавлены общие UI-стили для блока асинхронного состояния, списка данных и error/loading-состояний.

Проверка:
- `docker compose up -d frontend` — passed
- `docker compose exec -T frontend wget -q -O - http://127.0.0.1:5173/api/health/` — passed (`{"status":"ok"}` через Vite proxy)
- Playwright smoke-check `http://127.0.0.1:5173/` — passed (dashboard route показывает успешный ответ API root через общий request layer)
- Playwright mocked error-check `http://127.0.0.1:5173/filter` — passed (при ответе `500` от `/api/health/` UI показывает общий error state и сообщение `Simulated failure`)
- `docker compose ps` — passed (`db`, `web`, `frontend` в состоянии `healthy`)

Состояние запуска:
- frontend продолжает подниматься в compose-окружении и теперь имеет рабочий базовый API client с общей обработкой загрузки и ошибок;
- проект остаётся запускаемым после задачи

## T32 — Реализовать dashboard page
- Дата: 2026-03-09 20:31 +0300
- Статус: done
- Коммит: `137882c`

Что сделано:
- в [`frontend/src/api/resources.js`](/home/vr/projects/idea-lab/frontend/src/api/resources.js) добавлен запрос `getDashboardAggregates` для чтения `/api/dashboard/aggregates/`;
- в [`frontend/src/App.jsx`](/home/vr/projects/idea-lab/frontend/src/App.jsx) реализована реальная dashboard-страница на маршруте `/` с загрузкой агрегатов, KPI-блоками, воронкой по статусам и CTA-переходами в quick filter и elaboration;
- dashboard использует общий request layer из `T31` и показывает состояния `loading` и `error` для агрегатов;
- в [`frontend/src/styles.css`](/home/vr/projects/idea-lab/frontend/src/styles.css) добавлены стили для dashboard hero, KPI-карточек, funnel-блоков и workflow entry points.

Проверка:
- `docker compose logs frontend --tail 80` — passed
- Playwright smoke-check `http://127.0.0.1:5173/` — passed (dashboard рендерит CTA-ссылки на `/filter` и `/stages`, затем после загрузки показывает реальные агрегаты `new`, `accepted`, `rejected`, `in_progress`, `completed`)
- Playwright mocked error-check `http://127.0.0.1:5173/` — passed (при ответе `503` от `/api/dashboard/aggregates/` dashboard показывает error state с сообщением `Aggregates unavailable`)
- `docker compose ps` — passed (`db`, `web`, `frontend` в состоянии `healthy`)

Состояние запуска:
- frontend продолжает подниматься в compose-окружении и теперь имеет рабочую dashboard-страницу на реальных backend-агрегатах;
- проект остаётся запускаемым после задачи
