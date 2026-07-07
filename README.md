# Начало Роста: Влияние

Платформа для поиска IT-возможностей для молодёжи Центральной Азии. Здесь собраны гранты, стажировки, хакатоны, конкурсы и AI-рекомендации на основе профиля пользователя.

Онлайн-демо сейчас недоступно: проект рассчитан на локальный запуск через Docker Compose.

## Скриншоты

| Главная | Возможности | AI-рекомендации |
|---|---|---|
| ![Главная](снимки%20проекта/home.png) | ![Возможности](снимки%20проекта/opportunities.png) | ![AI-рекомендации](снимки%20проекта/recommendations.png) |

| Профиль | О проекте |
|---|---|
| ![Профиль](снимки%20проекта/profile.png) | ![О проекте](снимки%20проекта/about.png) |

## Что умеет платформа

- Каталог IT-возможностей из Telegram, RSS и сайтов
- AI-рекомендации по интересам и навыкам
- Избранное для сохранения нужных объявлений
- Профиль с настройками и персональными данными
- Публичные страницы проекта и справка для пользователей

## Стек

| Слой | Технологии |
|---|---|
| Backend | Django 5.1, Django REST Framework, PostgreSQL, Redis, Celery |
| Frontend | React 18, Vite, Redux Toolkit, TailwindCSS, daisyUI |
| AI | OpenRouter |
| Инфраструктура | Docker Compose, Nginx, Gunicorn |

## Запуск локально

```bash
cp .env.example .env
docker compose up -d --build

docker exec nachalo_backend python manage.py seed_sources
docker exec nachalo_backend python manage.py seed_international
```

После запуска сайт доступен на http://localhost:8080.

## Репозиторий

Исходники проекта: https://github.com/bekrahoon/nachalo-rosta-master.git

## Лицензия

MIT
