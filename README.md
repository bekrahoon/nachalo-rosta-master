# Начало Роста: Влияние

Агрегатор возможностей для молодёжи Центральной Азии. Собирает гранты, стипендии, хакатоны, стажировки и волонтёрские программы из 30+ источников в одном месте.

**Сайт:** http://nachalo.live

## Что делает платформа

- **Каталог возможностей** — объявления из Telegram-каналов, RSS-фидов и сайтов, с фильтрами по типу и региону
- **AI-рекомендации** — подбор возможностей на основе профиля, интересов и навыков пользователя (OpenRouter API)
- **Совместные заявки** — поиск напарников для хакатонов, конкурсов и проектов с привязкой к конкретной возможности из каталога
- **Избранное** — сохранение интересных объявлений

## Технологии

| Слой | Стек |
|------|------|
| Backend | Django 5.1, Django REST Framework, PostgreSQL, Redis, Celery |
| Frontend | React 18, Vite, Redux Toolkit, TailwindCSS, daisyUI |
| AI | OpenRouter (классификация объявлений + рекомендации) |
| Инфраструктура | Docker Compose, Nginx, Gunicorn |

## Запуск

```bash
# Клонировать и перейти в директорию
cd nachalo-rosta-master

# Создать .env (скопировать из .env и настроить)
cp .env.example .env

# Запустить
docker compose up -d

# Добавить источники и объявления
docker exec nachalo_backend python manage.py seed_sources
docker exec nachalo_backend python manage.py seed_international
```

Сайт будет доступен на http://localhost:8080

## Структура

```
backend/
  apps/
    accounts/        — регистрация, JWT-аутентификация, профиль
    aggregator/      — источники, сбор данных, AI-классификация, каталог
      collectors/    — telegram, rss, wordpress, html scraper
    recommendations/ — AI-рекомендации (OpenRouter)
    teams/           — совместные заявки
    portfolio/       — избранное
  config/            — settings, urls, celery

frontend/
  src/
    pages/           — Home, Opportunities, Recommendations, Teams, TeamDetail, Portfolio, Profile, Settings, StaticPage
    components/      — Navbar, Layout, ListingCard, etc.
    api/             — axios client
    store/           — Redux (auth)

nginx/               — reverse proxy config
```

## API

| Endpoint | Описание |
|----------|----------|
| `POST /api/v1/auth/register/` | Регистрация |
| `POST /api/v1/auth/token/` | Получение JWT |
| `GET /api/v1/aggregator/listings/` | Каталог возможностей |
| `GET /api/v1/aggregator/listings/facets/` | Фильтры (типы, регионы, теги) |
| `GET /api/v1/recommendations/` | AI-рекомендации пользователя |
| `POST /api/v1/recommendations/refresh/` | Запуск генерации рекомендаций |
| `GET /api/v1/teams/` | Совместные заявки |
| `POST /api/v1/teams/` | Создать заявку |
| `POST /api/v1/teams/{id}/join/` | Присоединиться |
| `GET /api/v1/portfolio/` | Избранное |

## Источники данных

Агрегатор поддерживает 4 типа коллекторов:

- **telegram_web_preview** — парсинг публичных Telegram-каналов
- **rss_feed** — RSS/Atom фиды
- **wordpress_api** — WordPress REST API
- **html_scrape** — парсинг HTML-страниц по CSS-селекторам

Сбор данных и классификация происходят автоматически через Celery Beat.

## Деплой

Проект задеплоен на DigitalOcean Droplet (Ubuntu 24.04, Docker).

```bash
# На сервере
cd /root/nachalo-rosta
docker compose up -d --build
```

## Лицензия

MIT
