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
- Коммит: `pending`

Что сделано:
- добавлен [`docker-compose.yml`](/home/vr/projects/idea-lab/docker-compose.yml) с сервисами `db`, `web`, `frontend`;
- для `db` выбран `postgres:16-alpine`, настроены базовые переменные окружения, volume и healthcheck через `pg_isready`;
- добавлены минимальные Dockerfile-заглушки для [`backend/Dockerfile`](/home/vr/projects/idea-lab/backend/Dockerfile) и [`frontend/Dockerfile`](/home/vr/projects/idea-lab/frontend/Dockerfile);
- созданы каталоги `backend/`, `frontend/`, `docs/` с placeholder-файлами, чтобы compose-контексты были валидны.

Проверка:
- `docker compose config` — passed
- `docker compose up --build -d` — blocked: текущая среда не имеет доступа к `unix:///var/run/docker.sock`

Состояние запуска:
- compose-конфигурация собрана и валидируется локально;
- полноценный smoke-check запуска контейнеров требует прав на Docker daemon на хосте
