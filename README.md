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

## План работ и требования
- [PRD.md](/home/vr/projects/idea-lab/PRD.md)
- [TASKS.md](/home/vr/projects/idea-lab/TASKS.md)
- [task-reports.md](/home/vr/projects/idea-lab/task-reports.md)
