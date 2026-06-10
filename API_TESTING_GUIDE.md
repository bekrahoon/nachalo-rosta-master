# 🧪 API Testing Guide — "Начало Роста: Влияние"

Полный гайд для тестирования всех endpoints аутентификации и авторизации.

---

## 🛠️ Инструменты для тестирования

### Вариант 1: Swagger UI (Рекомендуется)
Просто откройте: http://localhost:8000/api/docs/

### Вариант 2: cURL (командная строка)
```bash
curl -X POST http://localhost:8000/api/v1/auth/register/ \
  -H "Content-Type: application/json" \
  -d '{"email":"user@example.com","password":"StrongPass123!"}'
```

### Вариант 3: Postman
Импортируй OpenAPI schema из: http://localhost:8000/api/schema/

### Вариант 4: HTTPie
```bash
http POST http://localhost:8000/api/v1/auth/register/ \
  email=user@example.com \
  password=StrongPass123!
```

---

## 📋 Полный flow аутентификации

### 1️⃣ Регистрация нового пользователя

**Endpoint:** `POST /api/v1/auth/register/`

**Request:**
```json
{
  "email": "john@example.com",
  "password": "MySecurePassword123!",
  "password_confirm": "MySecurePassword123!",
  "first_name": "John",
  "last_name": "Doe",
  "phone": "+996501234567"
}
```

**Response (201 Created):**
```json
{
  "message": "Registration successful. Please check your email to verify your account.",
  "email": "john@example.com"
}
```

**Что происходит:**
- ✅ Пользователь создан с `is_active=False`
- ✅ Генерируется email verification токен
- ✅ Письмо с токеном отправляется на email (асинхронно через Celery)
- ✅ Пароль хешируется через bcrypt

**Возможные ошибки:**
```json
{
  "email": ["This email is already registered."],
  "password": ["This password is too common."],
  "password": ["Passwords do not match."]
}
```

---

### 2️⃣ Проверка доступности email (опционально)

**Endpoint:** `POST /api/v1/auth/check-email/`

**Request:**
```json
{
  "email": "john@example.com"
}
```

**Response:**
```json
{
  "available": false
}
```

или

```json
{
  "available": true
}
```

---

### 3️⃣ Проверка email (из письма)

Когда пользователь получает письмо, в нём содержится ссылка:
```
http://localhost:5173/verify-email/?token=THE_TOKEN_FROM_EMAIL
```

**Endpoint:** `POST /api/v1/auth/verify-email/`

**Request:**
```json
{
  "token": "the_verification_token_from_email"
}
```

**Response (200 OK):**
```json
{
  "message": "Email verified successfully. You can now log in.",
  "user": {
    "id": "550e8400-e29b-41d4-a716-446655440000",
    "email": "john@example.com",
    "first_name": "John",
    "last_name": "Doe",
    "full_name": "John Doe",
    "role": "user",
    "email_verified": true,
    "is_active": true,
    ...
  }
}
```

**Возможные ошибки:**
```json
{
  "token": ["Invalid or already used verification token."]
}
```

или

```json
{
  "token": ["Verification token has expired."]
}
```

---

### 4️⃣ Переотправка письма верификации

Если пользователь не получил письмо или забыл токен:

**Endpoint:** `POST /api/v1/auth/resend-verification/`

**Request:**
```json
{
  "email": "john@example.com"
}
```

**Response (200 OK):**
```json
{
  "message": "Verification email has been sent."
}
```

---

### 5️⃣ Вход в систему (получение JWT токенов)

**Endpoint:** `POST /api/v1/auth/token/`

**Request:**
```json
{
  "email": "john@example.com",
  "password": "MySecurePassword123!"
}
```

**Response (200 OK):**
```json
{
  "access": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ0b2tlbl90eXBlIjoiYWNjZXNzIiwiZXhwIjoxNjk2OTk5OTk5LCJpYXQiOjE2OTcwMDAwMDAsImp0aSI6IjU1MGU4NDAwLWUyOWItNDFkNC1hNzE2LTQ0NjY1NTQ0MDAwMCIsInVzZXJfaWQiOiI1NTBlODQwMC1lMjliLTQxZDQtYTcxNi00NDY2NTU0NDAwMDAifQ.SIGNATURE",
  "refresh": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ0b2tlbl90eXBlIjoicmVmcmVzaCIsImV4cCI6MTY5NzYwNDgwMCwiaWF0IjoxNjk3MDAwMDAwLCJqdGkiOiI1NTBlODQwMC1lMjliLTQxZDQtYTcxNi00NDY2NTU0NDAwMDAiLCJ1c2VyX2lkIjoiNTUwZTg0MDAtZTI5Yi00MWQ0LWE3MTYtNDQ2NjU1NDQwMDAwIn0.SIGNATURE"
}
```

**Что происходит:**
- ✅ Access token живёт **1 час**
- ✅ Refresh token живёт **7 дней**
- ✅ Последний вход обновляется в БД
- ✅ Используй access token в заголовке `Authorization: Bearer {access_token}`

**Возможные ошибки:**
```json
{
  "detail": "Invalid credentials."
}
```

или (если email не верифицирован)

```json
{
  "detail": "Please verify your email before logging in."
}
```

или (если попыток > 5 за час)

```json
{
  "detail": "Too many login attempts. Please try again later."
}
```

---

## 🔐 Использование токенов

### Получение информации о текущем пользователе

**Endpoint:** `GET /api/v1/auth/profile/`

**Headers:**
```
Authorization: Bearer {ACCESS_TOKEN}
Content-Type: application/json
```

**Response:**
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "email": "john@example.com",
  "first_name": "John",
  "last_name": "Doe",
  "middle_name": "",
  "full_name": "John Doe",
  "short_name": "John",
  "phone": "+996501234567",
  "bio": "",
  "avatar": null,
  "date_of_birth": null,
  "country": "",
  "city": "",
  "region": "",
  "role": "user",
  "email_verified": true,
  "is_organizer": false,
  "is_moderator": false,
  "created_at": "2024-01-15T10:30:00Z",
  "updated_at": "2024-01-15T10:35:00Z",
  "last_login_at": "2024-01-15T10:35:00Z",
  "receive_emails": true,
  "receive_notifications": true
}
```

---

### Обновление профиля

**Endpoint:** `PUT /api/v1/auth/profile/`

**Headers:**
```
Authorization: Bearer {ACCESS_TOKEN}
Content-Type: application/json
```

**Request:**
```json
{
  "first_name": "John",
  "last_name": "Doe",
  "bio": "I love volunteering!",
  "phone": "+996501234567",
  "country": "Kyrgyzstan",
  "city": "Bishkek",
  "region": "Chui",
  "date_of_birth": "1995-05-20",
  "receive_emails": true,
  "receive_notifications": true
}
```

**Response (200 OK):**
```json
{
  "message": "Profile updated successfully.",
  "user": {
    "id": "550e8400-e29b-41d4-a716-446655440000",
    "email": "john@example.com",
    "first_name": "John",
    "last_name": "Doe",
    "bio": "I love volunteering!",
    "country": "Kyrgyzstan",
    "city": "Bishkek",
    ...
  }
}
```

---

### Загрузка аватара

Для загрузки аватара нужно отправить `multipart/form-data`:

```bash
curl -X PUT http://localhost:8000/api/v1/auth/profile/ \
  -H "Authorization: Bearer {ACCESS_TOKEN}" \
  -F "avatar=@/path/to/avatar.jpg"
```

---

## 🔄 Обновление токенов

Access token живёт 1 час. Когда он истекает, используй refresh token чтобы получить новый access token:

**Endpoint:** `POST /api/v1/auth/token/refresh/`

**Headers:**
```
Content-Type: application/json
```

**Request:**
```json
{
  "refresh": "the_refresh_token_from_login"
}
```

**Response (200 OK):**
```json
{
  "access": "new_access_token_with_1_hour_lifetime",
  "refresh": "new_refresh_token_with_7_days_lifetime"
}
```

**Автоматическая ротация:**
- ✅ Старый refresh token инвалидируется
- ✅ Новый refresh token выдаётся
- ✅ Old token попадает в blacklist

---

## 🚪 Выход из системы (Logout)

**Endpoint:** `POST /api/v1/auth/logout/`

**Headers:**
```
Authorization: Bearer {ACCESS_TOKEN}
Content-Type: application/json
```

**Request:**
```json
{
  "refresh": "the_refresh_token"
}
```

**Response (200 OK):**
```json
{
  "message": "Successfully logged out."
}
```

**Что происходит:**
- ✅ Refresh token добавляется в blacklist
- ✅ Все токены пользователя инвалидируются
- ✅ User session помечается как неактивная

---

## 🔑 Смена пароля (для авторизованных пользователей)

**Endpoint:** `POST /api/v1/auth/password/change/`

**Headers:**
```
Authorization: Bearer {ACCESS_TOKEN}
Content-Type: application/json
```

**Request:**
```json
{
  "old_password": "OldPassword123!",
  "new_password": "NewPassword123!",
  "new_password_confirm": "NewPassword123!"
}
```

**Response (200 OK):**
```json
{
  "message": "Password changed successfully."
}
```

**Ошибки:**
```json
{
  "old_password": ["Current password is incorrect."]
}
```

или

```json
{
  "new_password": ["This password is too common."]
}
```

---

## 🔓 Восстановление пароля (Forgot Password)

### Шаг 1: Запрос на восстановление

**Endpoint:** `POST /api/v1/auth/password-reset/request/`

**Request:**
```json
{
  "email": "john@example.com"
}
```

**Response (200 OK):**
```json
{
  "message": "If the email exists, a password reset link will be sent."
}
```

**Что происходит:**
- ✅ Письмо с ссылкой отправляется на email
- ✅ Ссылка содержит reset токен
- ✅ Токен живёт **1 час**

Письмо содержит ссылку:
```
http://localhost:5173/reset-password/?token=THE_RESET_TOKEN
```

### Шаг 2: Подтверждение восстановления

**Endpoint:** `POST /api/v1/auth/password-reset/confirm/`

**Request:**
```json
{
  "token": "the_reset_token_from_email",
  "new_password": "NewPassword123!",
  "new_password_confirm": "NewPassword123!"
}
```

**Response (200 OK):**
```json
{
  "message": "Password reset successful. You can now log in with your new password.",
  "email": "john@example.com"
}
```

**Ошибки:**
```json
{
  "token": ["Invalid or expired password reset token."]
}
```

или

```json
{
  "new_password": ["This password is too common."]
}
```

---

## 👤 Получение публичного профиля пользователя

**Endpoint:** `GET /api/v1/auth/user/{user_id}/`

**Example:**
```bash
GET /api/v1/auth/user/550e8400-e29b-41d4-a716-446655440000/
```

**Response (200 OK):**
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "email": "john@example.com",
  "first_name": "John",
  "last_name": "Doe",
  "full_name": "John Doe",
  "short_name": "John",
  "role": "user",
  "bio": "I love volunteering!",
  ...
}
```

---

## ✅ Проверка валидности токена

**Endpoint:** `POST /api/v1/auth/verify-token/`

**Headers:**
```
Authorization: Bearer {ACCESS_TOKEN}
Content-Type: application/json
```

**Response (200 OK):**
```json
{
  "valid": true,
  "user": {
    "id": "550e8400-e29b-41d4-a716-446655440000",
    "email": "john@example.com",
    ...
  }
}
```

**Error (401 Unauthorized):**
```json
{
  "detail": "Given token not valid for any token type"
}
```

---

## 🧪 Примеры cURL для быстрого тестирования

```bash
# 1. Регистрация
curl -X POST http://localhost:8000/api/v1/auth/register/ \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "password": "TestPassword123!",
    "password_confirm": "TestPassword123!",
    "first_name": "Test",
    "last_name": "User"
  }'

# 2. Вход (получить токены)
curl -X POST http://localhost:8000/api/v1/auth/token/ \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "password": "TestPassword123!"
  }'

# 3. Получить профиль (используя access token)
ACCESS_TOKEN="your_access_token_here"
curl -X GET http://localhost:8000/api/v1/auth/profile/ \
  -H "Authorization: Bearer $ACCESS_TOKEN" \
  -H "Content-Type: application/json"

# 4. Обновить профиль
curl -X PUT http://localhost:8000/api/v1/auth/profile/ \
  -H "Authorization: Bearer $ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "first_name": "Updated",
    "last_name": "Name",
    "bio": "New bio"
  }'

# 5. Выход
curl -X POST http://localhost:8000/api/v1/auth/logout/ \
  -H "Authorization: Bearer $ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "refresh": "your_refresh_token"
  }'
```

---

## 📊 HTTP Status Codes

| Status | Meaning |
|--------|---------|
| **200** | OK — запрос успешен |
| **201** | Created — ресурс создан |
| **400** | Bad Request — ошибка в запросе (валидация) |
| **401** | Unauthorized — требуется аутентификация |
| **403** | Forbidden — доступ запрещён |
| **404** | Not Found — ресурс не найден |
| **429** | Too Many Requests — rate limit (слишком много попыток) |
| **500** | Internal Server Error — ошибка сервера |

---

## 🎯 Тестовые сценарии

### Сценарий 1: Полная регистрация и вход

```bash
# 1. Регистрация
POST /api/v1/auth/register/
→ 201 Created

# 2. Проверка письма в консоли (в development режиме)
# Найди verification token в логах

# 3. Верификация email
POST /api/v1/auth/verify-email/
→ 200 OK

# 4. Вход
POST /api/v1/auth/token/
→ 200 OK (получаешь access и refresh tokens)

# 5. Получить профиль
GET /api/v1/auth/profile/ (с access token)
→ 200 OK
```

### Сценарий 2: Обновление access token

```bash
# 1. Получил токены при входе
# access: "короткоживущий"
# refresh: "долгоживущий"

# 2. Спустя 1 час access token истекает

# 3. Используем refresh для получения нового access
POST /api/v1/auth/token/refresh/
→ 200 OK (новые access и refresh tokens)

# 4. Используем новый access token для запросов
```

### Сценарий 3: Сброс пароля

```bash
# 1. Пользователь забыл пароль
POST /api/v1/auth/password-reset/request/
→ 200 OK (письмо отправлено)

# 2. Проверь консоль/email для токена

# 3. Используй токен для сброса
POST /api/v1/auth/password-reset/confirm/
→ 200 OK

# 4. Вход с новым паролем
POST /api/v1/auth/token/
→ 200 OK
```

---

## 🐛 Debugging

### Для development режима

В `settings/local.py` уже включены:
- ✅ Debug Toolbar
- ✅ SQL query logging
- ✅ Console email backend

### Просмотр логов Celery

```bash
docker-compose logs -f celery_worker
```

### Просмотр логов Django

```bash
docker-compose logs -f backend
```

### Проверка БД

```bash
docker-compose exec postgres psql -U nachalo_user -d nachalo_db

# Посмотреть пользователей
\c nachalo_db
SELECT * FROM accounts_customuser;

# Посмотреть отправленные письма (в console backend)
SELECT * FROM django_admin_log;
```

---

## 📚 Дополнительно

- [JWT документация](https://tools.ietf.org/html/rfc7519)
- [REST Best Practices](https://restfulapi.net/)
- [Django REST Framework Auth](https://www.django-rest-framework.org/api-guide/authentication/)
- [simplejwt документация](https://django-rest-framework-simplejwt.readthedocs.io/)

---

**Успешного тестирования! 🚀**
