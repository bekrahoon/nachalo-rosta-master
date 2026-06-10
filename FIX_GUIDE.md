# 🚀 ПОЛНОЕ РЕШЕНИЕ ДЛЯ ПРОБЛЕМЫ С РЕГИСТРАЦИЕЙ

## ✅ ЧТО БЫЛО ИСПРАВЛЕНО:

### 1. Nginx конфиг
- ✅ Удалён HTTPS редирект (вызывал `Location: https://...`)
- ✅ Добавлен правильный прокси для `/api/v1/`
- ✅ HTTP only для локальной разработки

### 2. Django CORS
- ✅ Добавлены origins: `localhost:8080`, `127.0.0.1:8080`
- ✅ SECURE_SSL_REDIRECT = False

### 3. Frontend конфиг
- ✅ VITE_API_BASE_URL=/api/v1 (уже правильно)
- ✅ frontend/src/api/client.js исправлен

---

## 🔧 ИНСТРУКЦИЯ ПО ЗАПУСКУ:

### Шаг 1: Скопируй исправленные файлы в свой проект

```bash
# Скопируй из текущей директории в твой проект
# nginx/conf.d/default.conf - исправленный
# .env - исправленный
# backend/config/settings/base.py - исправленный CORS
```

### Шаг 2: Перезапусти контейнеры

```bash
cd ~/Загрузки/nachalo-rosta-FULL/nachalo-rosta

# Полный перезапуск
docker compose down -v
docker compose up -d
sleep 20
```

### Шаг 3: Проверь что контейнеры запущены

```bash
docker compose ps
```

Все должны быть в статусе `Up`.

### Шаг 4: Проверь логи

```bash
# Nginx
docker compose logs nginx | tail -10

# Backend
docker compose logs backend | tail -10

# Celery
docker compose logs celery_worker | tail -10
```

### Шаг 5: Тестирование

Открой `http://localhost:8080/register` в браузере.

**Ожидается:**
1. ✅ Страница загружается нормально
2. ✅ Запрос идёт на `http://localhost:8080/api/v1/auth/register/` (НЕ HTTPS!)
3. ✅ Status 201 Created
4. ✅ Письмо приходит на email

---

## 🧪 ЕСЛИ ВСЁ ЕЩЁ НЕ РАБОТАЕТ:

### Проверь сертификат

```bash
# Удали SSL файлы (они самоподписанные и мешают)
rm -f nginx/ssl/*

# Или просто не используй HTTPS для development
```

### Проверь что фронтенд использует HTTP

В браузере (F12 → Network) запрос должен быть:
```
POST http://localhost:8080/api/v1/auth/register/  ✅
```

НЕ:
```
POST https://localhost/api/v1/auth/register/  ❌
```

### Проверь curl напрямую

```bash
curl -X POST http://localhost:8000/api/v1/auth/register/ \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","password":"Test123!@#SuperLong","password_confirm":"Test123!@#SuperLong","first_name":"Test","last_name":"User"}' \
  -v 2>&1 | grep "HTTP"
```

Должно быть: `HTTP/1.1 201 Created`

---

## 📋 CHECKLIST:

- [ ] Скопировал исправленные файлы
- [ ] `docker compose down -v`
- [ ] `docker compose up -d`
- [ ] Дождался 20 секунд загрузки
- [ ] `docker compose ps` - все Up
- [ ] Открыл `http://localhost:8080/register`
- [ ] Попробовал зарегистрироваться
- [ ] Проверил email

---

**После этого должно работать!** 🎉

Если ещё есть проблемы - дай мне логи:
```bash
docker compose logs backend nginx celery_worker | tail -100
```
