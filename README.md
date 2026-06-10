# 🚀 Начало Роста: Влияние (Beginning of Growth: Impact)

**Платформа молодёжного волонтёрства, социальных инициатив и личного развития**

---

## 📋 Описание проекта

"Начало Роста: Влияние" — это комплексная веб-платформа для:
- 🎯 **AI-рекомендаций** волонтёрских возможностей на основе интересов пользователя
- 🗺️ **Карты возможностей** — интерактивная карта волонтёрских проектов и инициатив
- 🏆 **Системы достижений** — геймификация волонтёрской деятельности
- 📄 **Волонтёрского портфолио** — автоматическое создание PDF-портфолио
- 👥 **Команд и поиска волонтёров** — создание команд и поиск соответствующих участников
- 📊 **Социального влияния** — трекинг и визуализация влияния волонтёрской деятельности

---

## 🛠️ Технологический стек

### Backend
- **Django 5.1** + **Django REST Framework**
- **PostgreSQL** — главная база данных
- **Redis** — кеширование и очередь задач
- **Celery** + **Celery Beat** — асинхронные задачи и расписание
- **JWT (simplejwt)** — аутентификация и авторизация
- **Docker** + **Docker Compose** — контейнеризация

### Frontend
- **React 18** + **Vite**
- **Redux Toolkit** + **React-Redux** — управление состоянием
- **Axios** + **Interceptors** — работа с API
- **React Router DOM** — маршрутизация
- **TailwindCSS** + **daisyUI** — стилизация
- **React Hook Form** + **Zod** — формы и валидация

### Инфраструктура
- **Nginx** — reverse proxy
- **Gunicorn** — WSGI сервер для Django
- **PostgreSQL** — база данных
- **Redis** — кеширование и очередь

---

## 📁 Структура проекта

```
nachalo-rosta/
├── backend/                    # Django приложение
│   ├── config/                # Конфигурация проекта
│   │   ├── settings/          # Django settings (base, local, production)
│   │   ├── urls.py            # Главные URL маршруты
│   │   ├── wsgi.py            # WSGI конфиг
│   │   └── __init__.py         # Celery конфиг
│   ├── apps/                  # Django приложения
│   │   ├── accounts/          # 🔐 Аутентификация и авторизация
│   │   ├── events/            # 📅 События и инициативы
│   │   ├── recommendations/   # 🤖 AI-рекомендации
│   │   ├── achievements/      # 🏆 Достижения
│   │   ├── portfolio/         # 📄 Портфолио и CV
│   │   ├── teams/             # 👥 Команды
│   │   ├── impact/            # 📊 Социальное влияние
│   │   └── core/              # 🔧 Основные утилиты
│   ├── templates/             # Email шаблоны и HTML
│   ├── manage.py              # Django CLI
│   └── requirements.txt        # Python зависимости
├── frontend/                  # React приложение
│   ├── src/
│   │   ├── components/        # React компоненты
│   │   ├── pages/             # Страницы
│   │   ├── store/             # Redux store
│   │   ├── api/               # API клиент
│   │   └── App.jsx            # Главный компонент
│   ├── public/                # Статичные файлы
│   ├── package.json           # NPM зависимости
│   ├── vite.config.js         # Vite конфиг
│   └── Dockerfile             # Docker образ для фронтенда
├── nginx/                     # Конфигурация Nginx
│   ├── nginx.conf             # Основной конфиг
│   └── conf.d/                # Конфиги приложений
├── docker-compose.yml         # Оркестрация контейнеров
├── Dockerfile.backend         # Docker образ для бэкенда
├── .env.example               # Пример переменных окружения
└── README.md                  # Этот файл

```

---

## 🚀 Быстрый старт

### Предварительные требования

- **Docker** и **Docker Compose**
- **Python 3.11+** (для локальной разработки)
- **Node.js 20+** (для локальной разработки фронтенда)

### 1. Клонирование и подготовка

```bash
# Клонируем репозиторий
git clone https://github.com/your-repo/nachalo-rosta.git
cd nachalo-rosta

# Копируем .env файл
cp .env.example .env

# Редактируем .env под свои нужды (особенно SECRET_KEY и EMAIL)
nano .env
```

### 2. Запуск с Docker Compose

```bash
# Запускаем все контейнеры
docker-compose up -d

# Применяем миграции базы данных
docker-compose exec backend python manage.py migrate

# Создаём суперпользователя (администратора)
docker-compose exec backend python manage.py createsuperuser

# Собираем статичные файлы
docker-compose exec backend python manage.py collectstatic --noinput

# Проверяем логи
docker-compose logs -f backend
```

### 3. Доступ к приложению

- **Frontend**: http://localhost:5173
- **Backend API**: http://localhost:8000/api/v1/
- **API Documentation (Swagger)**: http://localhost:8000/api/docs/
- **Django Admin**: http://localhost:8000/admin/

---

## 🔐 Аутентификация и авторизация

### API Endpoints

#### Регистрация и вход

```bash
# 1. Регистрация нового пользователя
POST /api/v1/auth/register/
Content-Type: application/json

{
  "email": "user@example.com",
  "password": "StrongPassword123!",
  "password_confirm": "StrongPassword123!",
  "first_name": "John",
  "last_name": "Doe"
}

# Ответ:
{
  "message": "Registration successful. Please check your email to verify your account.",
  "email": "user@example.com"
}

# 2. Проверка email (используется токен из письма)
POST /api/v1/auth/verify-email/
Content-Type: application/json

{
  "token": "verification_token_from_email"
}

# 3. Вход в систему (получение JWT токенов)
POST /api/v1/auth/token/
Content-Type: application/json

{
  "email": "user@example.com",
  "password": "StrongPassword123!"
}

# Ответ:
{
  "access": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "refresh": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
}

# 4. Обновление токена (access token истекает через 1 час)
POST /api/v1/auth/token/refresh/
Content-Type: application/json

{
  "refresh": "refresh_token"
}

# 5. Выход из системы (blacklist refresh token)
POST /api/v1/auth/logout/
Authorization: Bearer access_token
Content-Type: application/json

{
  "refresh": "refresh_token"
}
```

#### Сброс пароля

```bash
# 1. Запрос на сброс пароля (отправляет письмо)
POST /api/v1/auth/password-reset/request/
Content-Type: application/json

{
  "email": "user@example.com"
}

# 2. Подтверждение сброса пароля
POST /api/v1/auth/password-reset/confirm/
Content-Type: application/json

{
  "token": "reset_token_from_email",
  "new_password": "NewStrongPassword123!",
  "new_password_confirm": "NewStrongPassword123!"
}
```

#### Профиль и настройки

```bash
# Получить профиль текущего пользователя
GET /api/v1/auth/profile/
Authorization: Bearer access_token

# Обновить профиль
PUT /api/v1/auth/profile/
Authorization: Bearer access_token
Content-Type: application/json

{
  "first_name": "John",
  "last_name": "Doe",
  "bio": "I love volunteering",
  "country": "Kyrgyzstan",
  "city": "Bishkek"
}

# Изменить пароль
POST /api/v1/auth/password/change/
Authorization: Bearer access_token
Content-Type: application/json

{
  "old_password": "OldPassword123!",
  "new_password": "NewPassword123!",
  "new_password_confirm": "NewPassword123!"
}

# Проверить, валиден ли токен
POST /api/v1/auth/verify-token/
Authorization: Bearer access_token
```

### Роли пользователей

- **user** (волонтёр) — обычный пользователь
- **organizer** — может создавать события и управлять командами
- **admin** — полный доступ ко всем функциям
- **moderator** — может модерировать контент

### JWT Токены

- **Access Token** — живёт 1 час, используется для доступа к защищённым эндпоинтам
- **Refresh Token** — живёт 7 дней, используется для получения нового access token
- Токены хранятся в **httpOnly cookies** (более безопасно) или в **localStorage** (для SPA)

---

## 📧 Email конфигурация

### Gmail (рекомендуется для тестирования)

1. Создай Google Account
2. Включи **2-factor authentication**
3. Создай **App Password** (https://myaccount.google.com/apppasswords)
4. Добавь в `.env`:

```env
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-app-password
EMAIL_USE_TLS=True
```

### Для тестирования (Console backend)

```env
EMAIL_BACKEND=django.core.mail.backends.console.EmailBackend
```

---

## 🔧 Локальная разработка

### Установка зависимостей

```bash
# Backend
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt

# Frontend
cd ../frontend
npm install
```

### Запуск локально (без Docker)

```bash
# Terminal 1 — PostgreSQL
docker run -d -e POSTGRES_PASSWORD=password -p 5432:5432 postgres:16-alpine

# Terminal 2 — Redis
docker run -d -p 6379:6379 redis:7-alpine

# Terminal 3 — Django
cd backend
export DJANGO_SETTINGS_MODULE=config.settings.local
python manage.py runserver

# Terminal 4 — React
cd frontend
npm run dev

# Terminal 5 — Celery Worker
cd backend
celery -A config worker -l info

# Terminal 6 — Celery Beat (optional)
cd backend
celery -A config beat -l info
```

---

## 📚 API Documentation

После запуска приложения доступна интерактивная API документация:

- **Swagger UI**: http://localhost:8000/api/docs/
- **ReDoc**: http://localhost:8000/api/redoc/
- **OpenAPI Schema**: http://localhost:8000/api/schema/

---

## 🧪 Тестирование

```bash
# Backend тесты
cd backend
pytest

# Frontend тесты (TBD)
cd frontend
npm test
```

---

## 🐛 Troubleshooting

### Проблема: "Connection refused" при подключении к БД

```bash
# Проверяем, запущены ли контейнеры
docker-compose ps

# Переживаем миграции
docker-compose exec backend python manage.py migrate
```

### Проблема: "Permission denied" для логов

```bash
# Создаём папку для логов
mkdir -p backend/logs
chmod 777 backend/logs
```

### Проблема: Email не отправляется

```bash
# Проверяем, правильно ли настроены переменные окружения в .env
# Смотрим логи Celery
docker-compose logs celery_worker

# Включаем console backend для дебага
EMAIL_BACKEND=django.core.mail.backends.console.EmailBackend
```

---

## 📖 Дополнительные ресурсы

- [Django Documentation](https://docs.djangoproject.com/)
- [Django REST Framework](https://www.django-rest-framework.org/)
- [React Documentation](https://react.dev/)
- [Vite Documentation](https://vitejs.dev/)
- [Docker Documentation](https://docs.docker.com/)

---

## 📝 Лицензия

MIT License — свободный для использования в личных и коммерческих проектах.

---

## 🤝 Контрибьютинг

Приветствуются pull requests и issues! Пожалуйста, прочитайте CONTRIBUTING.md перед тем как отправлять PR.

---

## 📞 Контакты

- 📧 Email: support@nachalo-rosta.local
- 🌐 Website: https://nachalo-rosta.com (TBD)
- 💬 Telegram: @nachalo_rosta (TBD)

---

**Сделано с ❤️ для молодёжи Центральной Азии**
