# ⚡ QUICKSTART — Запуск за 5 минут

Полный гайд для быстрого запуска проекта "Начало Роста: Влияние".

---

## 📋 Требования

- [Docker](https://www.docker.com/products/docker-desktop) (включая Docker Compose)
- Git

**Всё!** Больше ничего не требуется. Python, Node.js, PostgreSQL и Redis будут запущены в контейнерах.

---

## 🚀 5 шагов для запуска

### 1️⃣ Клонирование репозитория

```bash
git clone https://github.com/your-repo/nachalo-rosta.git
cd nachalo-rosta
```

### 2️⃣ Подготовка переменных окружения

```bash
# Копируем шаблон
cp .env.example .env

# Открываем и редактируем .env (опционально для разработки)
# Главное — поменяй SECRET_KEY на что-то безопасное
nano .env
```

### 3️⃣ Запуск Docker Compose

```bash
# Запуск всех сервисов в фоне
docker-compose up -d

# Проверка статуса (должны быть все зелёные)
docker-compose ps
```

Ожидаемый вывод:
```
NAME                  STATUS
nachalo_postgres      Up (healthy)
nachalo_redis         Up (healthy)
nachalo_backend       Up
nachalo_celery        Up
nachalo_celery_beat   Up
nachalo_frontend      Up
nachalo_nginx         Up
```

### 4️⃣ Инициализация базы данных

```bash
# Применяем миграции (создаём таблицы)
docker-compose exec backend python manage.py migrate

# Создаём администратора
docker-compose exec backend python manage.py createsuperuser
# Введи:
# Email: admin@example.com
# Password: (придумай пароль)

# Собираем статичные файлы (для Nginx)
docker-compose exec backend python manage.py collectstatic --noinput
```

### 5️⃣ Открываем в браузере

| Компонент | URL | Что там |
|-----------|-----|---------|
| **Frontend** | http://localhost:5173 | React приложение (TBD) |
| **API Docs** | http://localhost:8000/api/docs/ | Swagger документация |
| **API** | http://localhost:8000/api/v1/ | REST API endpoints |
| **Admin** | http://localhost:8000/admin/ | Django админ панель |

---

## ✨ Готово!

Проект запущен и работает! 🎉

---

## 🧪 Первые шаги (тестирование)

### Тест 1: Регистрация нового пользователя

Откройи Swagger: http://localhost:8000/api/docs/

1. Найди endpoint **POST /api/v1/auth/register/**
2. Нажми "Try it out"
3. Введи данные:
   ```json
   {
     "email": "john@example.com",
     "password": "MySecurePassword123!",
     "password_confirm": "MySecurePassword123!",
     "first_name": "John",
     "last_name": "Doe"
   }
   ```
4. Нажми "Execute"

**Ожидаемый ответ (201 Created):**
```json
{
  "message": "Registration successful. Please check your email to verify your account.",
  "email": "john@example.com"
}
```

### Тест 2: Проверка письма верификации

В development режиме письма не отправляются по email, а выводятся в консоль:

```bash
docker-compose logs backend | grep "verification"
```

Или посмотри сразу в БД:

```bash
docker-compose exec postgres psql -U nachalo_user -d nachalo_db
SELECT email_verification_token FROM accounts_customuser WHERE email='john@example.com';
```

Скопируй токен и используй его для верификации email.

### Тест 3: Верификация email

В Swagger найди endpoint **POST /api/v1/auth/verify-email/**

Введи:
```json
{
  "token": "the_token_you_copied"
}
```

**Ожидаемый ответ (200 OK):**
```json
{
  "message": "Email verified successfully. You can now log in.",
  "user": {
    "id": "550e8400-e29b-41d4-a716-446655440000",
    "email": "john@example.com",
    ...
  }
}
```

### Тест 4: Вход и получение JWT токенов

Endpoint: **POST /api/v1/auth/token/**

Введи:
```json
{
  "email": "john@example.com",
  "password": "MySecurePassword123!"
}
```

**Ожидаемый ответ (200 OK):**
```json
{
  "access": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "refresh": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
}
```

Скопируй `access` токен — он будет нужен для доступа к защищённым эндпоинтам.

### Тест 5: Получить профиль

Endpoint: **GET /api/v1/auth/profile/**

Нажми на замок 🔒 и вставь access token:
```
Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

**Ожидаемый ответ (200 OK):**
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "email": "john@example.com",
  "first_name": "John",
  "last_name": "Doe",
  "full_name": "John Doe",
  ...
}
```

---

## 🔧 Полезные команды

### Просмотр логов

```bash
# Все логи
docker-compose logs -f

# Только Django
docker-compose logs -f backend

# Только Celery Worker
docker-compose logs -f celery_worker

# Только React
docker-compose logs -f frontend
```

### Остановка и удаление контейнеров

```bash
# Остановить все контейнеры
docker-compose stop

# Удалить всё (контейнеры, сети, но НЕ данные в БД)
docker-compose down

# Удалить всё включая volumes (ОСТОРОЖНО — потеряются все данные)
docker-compose down -v
```

### Перезапуск сервиса

```bash
# Перезапустить backend
docker-compose restart backend

# Перезапустить frontend
docker-compose restart frontend

# Перезапустить всё
docker-compose restart
```

### Доступ к консоли Django

```bash
# Django shell
docker-compose exec backend python manage.py shell

# В shell можешь делать:
from django.contrib.auth import get_user_model
User = get_user_model()
users = User.objects.all()
for u in users:
    print(u.email)
```

### Доступ к БД PostgreSQL

```bash
docker-compose exec postgres psql -U nachalo_user -d nachalo_db

# Полезные SQL команды:
\c nachalo_db                                    # Подключиться к БД
\dt                                             # Список таблиц
SELECT * FROM accounts_customuser;              # Все пользователи
\q                                              # Выход
```

### Запуск тестов

```bash
# Backend тесты
docker-compose exec backend pytest

# С покрытием
docker-compose exec backend pytest --cov=apps
```

---

## 🆘 Troubleshooting

### ❌ Ошибка: "Error response from daemon: Cannot connect to Docker daemon"

**Решение:** Docker не запущен. Запусти Docker Desktop или демон Docker.

```bash
# macOS/Windows
# Открой Docker Desktop

# Linux
sudo systemctl start docker
```

### ❌ Ошибка: "Connection refused" при подключении к БД

**Решение:** PostgreSQL контейнер ещё запускается. Подожди 5-10 секунд.

```bash
# Проверь статус
docker-compose ps

# Если postgres не ready, проверь логи
docker-compose logs postgres
```

### ❌ Ошибка: "port 5173 is already in use"

**Решение:** Другой процесс занял порт. Найди и убей процесс.

```bash
# Linux/macOS
lsof -i :5173
kill -9 <PID>

# Windows (PowerShell)
netstat -ano | findstr :5173
taskkill /PID <PID> /F

# Или просто поменяй порт в docker-compose.yml
# Измени "5173:5173" на "5174:5173"
```

### ❌ Письма не отправляются

**Это нормально в development режиме!** Письма выводятся в консоль.

Для настоящей отправки отредактируй .env:

```env
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-app-password
```

Как получить App Password для Gmail:
1. Включи 2-factor authentication на аккаунте Google
2. Перейди на https://myaccount.google.com/apppasswords
3. Выбери "Mail" и "Windows Computer" (или твою ОС)
4. Скопируй пароль и вставь в EMAIL_HOST_PASSWORD

### ❌ Мигрэйции не применяются

```bash
# Проверь статус миграций
docker-compose exec backend python manage.py showmigrations

# Примени их вручную
docker-compose exec backend python manage.py migrate
```

### ❌ Статичные файлы не загружаются

```bash
# Пересобери статичные файлы
docker-compose exec backend python manage.py collectstatic --noinput

# Проверь что файлы есть
docker-compose exec backend ls -la /app/staticfiles/
```

---

## 📚 Следующие шаги

### Рекомендуемый порядок изучения:

1. **Базовая информация:**
   - Прочитай [README.md](./README.md)
   - Прочитай [PHASE_1_SUMMARY.md](./PHASE_1_SUMMARY.md)

2. **Тестирование API:**
   - Открой [API_TESTING_GUIDE.md](./API_TESTING_GUIDE.md)
   - Протестируй все endpoints в Swagger

3. **Локальная разработка (опционально):**
   - Установи зависимости локально
   - Запусти Django и React на локальной машине
   - Настрой IDE (PyCharm, VS Code и т.д.)

4. **Frontend разработка (Этап 2):**
   - Подожди когда будет готово React приложение
   - Используй API эндпоинты для интеграции

---

## 🎓 Учебные ресурсы

- [Django Documentation](https://docs.djangoproject.com/)
- [Django REST Framework](https://www.django-rest-framework.org/)
- [JWT Introduction](https://jwt.io/introduction)
- [React Documentation](https://react.dev/)
- [Docker Documentation](https://docs.docker.com/)

---

## 📞 Нужна помощь?

1. **Проверь Troubleshooting раздел выше**
2. **Посмотри логи:** `docker-compose logs -f`
3. **Прочитай [API_TESTING_GUIDE.md](./API_TESTING_GUIDE.md)** для примеров
4. **Откройте issue** в репозитории на GitHub

---

**Поздравляем! 🎉 Проект запущен и готов к разработке!**

Переходи к [Этапу 2](./PHASE_2_PLAN.md) для разработки React frontend.
