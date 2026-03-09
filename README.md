# Idea Lab

Внутреннее веб-приложение для сбора, фильтрации и проработки бизнес-идей.

Целевой стек первой версии:
- backend: Django + Django REST Framework
- frontend: React
- database: PostgreSQL
- local infrastructure: Docker Compose

## Структура проекта
- `backend/` — Django backend
- `frontend/` — React frontend
- `docs/` — служебная документация

## Требования
- Docker
- Docker Compose

## Быстрый старт
Из корня репозитория выполните:

```bash
docker compose up --build -d
```

После старта сервисы доступны по адресам:
- frontend: [http://localhost:5173](http://localhost:5173)
- backend: [http://localhost:8000](http://localhost:8000)
- backend health: [http://localhost:8000/api/health/](http://localhost:8000/api/health/)
- Django admin: [http://localhost:8000/admin/](http://localhost:8000/admin/)

Данные для входа в Django admin:
- login: `admin`
- password: `admin`

## Базовые команды разработки
Запуск:

```bash
docker compose up --build -d
```

Остановка:

```bash
docker compose down
```

Пересборка:

```bash
docker compose build
docker compose build web
docker compose build frontend
```

Статус контейнеров:

```bash
docker compose ps
```

Логи:

```bash
docker compose logs -f
docker compose logs -f web
docker compose logs -f frontend
docker compose logs -f db
```

Backend-тесты:

```bash
docker compose exec -T web python manage.py test
```

## Backend API
Все endpoint'ы первой версии доступны без аутентификации под префиксом `http://localhost:8000/api/`.

### API root
- `GET /api/`
- Возвращает ссылки на доступные API endpoint'ы.

### Health check
- `GET /api/health/`
- Ответ:

```json
{
  "status": "ok"
}
```

### Ingestion
- `POST /api/ingest/`
- Принимает один объект или массив объектов.
- Обязательные поля:
  - `source_system`
  - `source_id`
  - `source_url`
  - `title`
- Опциональные поля:
  - `description`
  - `category`
- Дубликаты по паре `source_system + source_id` не обновляются и попадают в `ignored`.
- Ответ:

```json
{
  "created": 1,
  "ignored": 0
}
```

Пример одного объекта:

```json
{
  "source_system": 1,
  "source_id": "project-123",
  "source_url": "https://kwork.ru/projects/123",
  "title": "Build an MVP",
  "description": "Need a small product team",
  "category": "development"
}
```

### Dashboard aggregates
- `GET /api/dashboard/aggregates/`
- Возвращает количество идей по всем статусам:

```json
{
  "new": 10,
  "accepted": 4,
  "rejected": 2,
  "in_progress": 3,
  "completed": 1
}
```

### Stage list
- `GET /api/stages/`
- Пагинированный список идей.
- Дефолтная сортировка: `created_at ASC`.
- `rejected` скрыты по умолчанию.
- Поддерживаемые query params:
  - `page`
  - `page_size`
  - `status`
  - `source_system_id`
  - `category`
  - `is_filled`
  - `include_rejected`
- `status` можно передавать одним значением или списком через запятую, например `accepted,in_progress`.

Пример:

```text
GET /api/stages/?status=accepted,in_progress&source_system_id=1&is_filled=false
```

Формат элемента списка:

```json
{
  "id": 1,
  "source_system_id": 1,
  "source_id": "project-123",
  "source_url": "https://kwork.ru/projects/123",
  "title": "Build an MVP",
  "description": "Need a small product team",
  "category": "development",
  "status": "accepted",
  "is_filled": false,
  "filled_at": null,
  "created_at": "2026-03-09T10:00:00Z",
  "updated_at": "2026-03-09T10:00:00Z"
}
```

### Stage detail
- `GET /api/stages/<id>/`
- Возвращает полную карточку идеи, включая все поля проработки.

### Quick status update
- `POST /api/stages/<id>/status/`
- Используется экраном быстрой фильтрации.
- Разрешённые значения поля `status`:
  - `accepted`
  - `rejected`
- Работает только для идей со статусом `new`.

Пример payload:

```json
{
  "status": "accepted"
}
```

### Elaboration update
- `PATCH /api/stages/<id>/elaboration/`
- Используется для редактирования карточки проработки.
- Разрешённые поля:
  - `custom_title`
  - `custom_description`
  - `existing_solution`
  - `original_revenue_estimate`
  - `seo_query`
  - `seo_kd_percent`
  - `seo_popularity_vs_adblocker`
  - `planned_feature`
  - `implementation_ease_percent`
  - `risks`
  - `is_filled`
- Неразрешённые поля вроде `status`, `filled_at`, `source_system`, `source_id`, `source_url`, `title` отклоняются с `400`.
- Логика статусов:
  - если заполнено хотя бы одно поле проработки и `is_filled=false`, backend ставит `in_progress`;
  - если `is_filled=true`, backend ставит `completed`;
  - при первом `is_filled=true` backend автоматически заполняет `filled_at` текущей датой.

Пример payload:

```json
{
  "custom_title": "Niche research assistant",
  "seo_query": "idea validation software",
  "seo_kd_percent": 42,
  "implementation_ease_percent": 67,
  "is_filled": true
}
```

Ответом для `GET /api/stages/<id>/`, `POST /api/stages/<id>/status/` и `PATCH /api/stages/<id>/elaboration/` служит полная карточка идеи:

```json
{
  "id": 1,
  "source_system_id": 1,
  "source_id": "project-123",
  "source_url": "https://kwork.ru/projects/123",
  "title": "Build an MVP",
  "description": "Need a small product team",
  "category": "development",
  "custom_title": "Niche research assistant",
  "custom_description": null,
  "existing_solution": null,
  "original_revenue_estimate": null,
  "seo_query": "idea validation software",
  "seo_kd_percent": 42,
  "seo_popularity_vs_adblocker": null,
  "planned_feature": null,
  "implementation_ease_percent": 67,
  "risks": null,
  "status": "completed",
  "is_filled": true,
  "filled_at": "2026-03-09",
  "created_at": "2026-03-09T10:00:00Z",
  "updated_at": "2026-03-09T10:05:00Z"
}
```

## План работ и требования
- [PRD.md](/home/vr/projects/idea-lab/PRD.md)
- [TASKS.md](/home/vr/projects/idea-lab/TASKS.md)
- [task-reports.md](/home/vr/projects/idea-lab/task-reports.md)
