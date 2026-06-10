# 🚀 FRONTEND SETUP GUIDE

Полный гайд по запуску React приложения.

## 📋 Быстрый старт

### 1. Установка зависимостей

```bash
cd frontend
npm install
```

### 2. Создание .env файла

```bash
cp .env.example .env

# .env файл содержит:
VITE_API_BASE_URL=http://localhost:8000
```

### 3. Запуск dev сервера

```bash
npm run dev

# http://localhost:5173
```

### 4. Открыть в браузере

```
http://localhost:5173
```

---

## 🔌 API Интеграция

Frontend автоматически подключается к backend API:

```javascript
// API_BASE_URL = http://localhost:8000/api/v1

// Все запросы автоматически включают:
// - Content-Type: application/json
// - Authorization: Bearer {access_token}

// При 401 автоматически:
// 1. Перехватывает запрос
// 2. Обновляет access token используя refresh token
// 3. Повторяет исходный запрос
// 4. Если обновить не удаётся → logout
```

---

## 📚 Структура проекта

```
frontend/
├── src/
│   ├── api/              # API клиент и endpoints
│   ├── components/       # Переиспользуемые компоненты
│   ├── pages/           # Страницы приложения
│   ├── store/           # Redux store
│   ├── hooks/           # Кастомные хуки
│   ├── routes/          # Router конфигурация
│   ├── App.jsx          # Главный компонент
│   ├── main.jsx         # Entry point
│   └── index.css        # Глобальные стили
├── index.html           # HTML шаблон
├── package.json         # NPM зависимости
├── vite.config.js       # Vite конфиг
├── tailwind.config.js   # Tailwind конфиг
└── .env.example         # Env template
```

---

## 🛠️ Доступные команды

```bash
# Запустить dev сервер
npm run dev

# Build для продакшена
npm run build

# Preview production build
npm run preview

# Lint проверка кода
npm run lint

# Format код с Prettier
npm run format
```

---

## 🔐 Аутентификация

### Login Flow

1. **Пользователь вводит email и пароль**
```
Form → useAuth.login() → Redux loginThunk
```

2. **Backend возвращает токены**
```
POST /api/v1/auth/token/
Response: { access, refresh }
```

3. **Токены сохраняются в localStorage**
```
localStorage.setItem('access_token', data.access)
localStorage.setItem('refresh_token', data.refresh)
```

4. **Redux store обновляется**
```
auth.user = profile data
auth.isAuthenticated = true
```

5. **Redirect на dashboard**
```
navigate('/dashboard')
```

### Protected Routes

```javascript
<ProtectedRoute>
  <Dashboard />
</ProtectedRoute>

// Если не авторизован → redirect на /login
// Если авторизован → показать компонент
```

### Token Refresh

Когда access token истекает (через 1 час):

```
1. Axios interceptor перехватывает 401
2. Отправляет refresh token на backend
3. Получает новые токены
4. Обновляет localStorage
5. Повторяет исходный запрос
```

---

## 🎨 Стилизация

### Tailwind CSS + daisyUI

```jsx
// Используем Tailwind классы
<div className="card bg-base-100 shadow">
  <div className="card-body">
    <h2 className="card-title">Заголовок</h2>
    <button className="btn btn-primary">Кнопка</button>
  </div>
</div>
```

### Кастомизация Theme

Edit `tailwind.config.js`:

```javascript
theme: {
  extend: {
    colors: {
      primary: '#0ea5e9',
      secondary: '#f97316',
      accent: '#10b981',
    },
  },
}
```

---

## 📦 Основные библиотеки

### React Router
```javascript
<BrowserRouter>
  <Routes>
    <Route path="/" element={<Home />} />
    <Route path="/login" element={<Login />} />
    <Route path="/dashboard" element={<Dashboard />} />
  </Routes>
</BrowserRouter>
```

### Redux + RTK
```javascript
const { user, isAuthenticated } = useSelector(state => state.auth)
dispatch(loginThunk({ email, password }))
```

### React Hook Form + Zod
```javascript
const { register, handleSubmit, formState: { errors } } = useForm({
  resolver: zodResolver(loginSchema),
})
```

### Axios
```javascript
apiClient.post('/auth/token/', { email, password })
// Автоматически включает Authorization header
// Обновляет токен при 401
```

---

## 🧪 Тестирование в браузере

### 1. Home Page
```
http://localhost:5173/
✓ Должна показываться главная страница
✓ Кнопки "Вход" и "Регистрация"
```

### 2. Registration
```
http://localhost:5173/register
✓ Заполнить форму с валидными данными
✓ Нажать "Зарегистрироваться"
✓ Должно показаться спасибо сообщение
```

### 3. Verification
```
http://localhost:8000/admin/
✓ Войти как администратор
✓ Найти пользователя в CustomUser
✓ Вручную изменить email_verified = True
✓ Пользователь сможет войти
```

### 4. Login
```
http://localhost:5173/login
✓ Ввести email и пароль
✓ Нажать "Вход"
✓ Должен redirect на /dashboard
```

### 5. Dashboard
```
http://localhost:5173/dashboard
✓ Видна приветственная надпись с именем
✓ Видны stats карточки
✓ Видны feature cards
```

### 6. Profile
```
http://localhost:5173/profile
✓ Видна информация пользователя
✓ Нажать Edit
✓ Отредактировать данные
✓ Нажать Save
✓ Данные обновлены
```

### 7. Logout
```
✓ Нажать на аватар в navbar
✓ Выбрать "Выход"
✓ Должен redirect на /login
✓ Tokens удалены из localStorage
```

---

## 🐛 Debugging

### DevTools

1. **Redux DevTools**
```bash
npm install @redux-devtools/extension
# Установить расширение в браузер
# Смотреть actions, state changes
```

2. **React DevTools**
```bash
# Chrome/Firefox расширение
# Инспектировать компоненты и props
```

3. **Network Tab**
```
F12 → Network
# Смотреть все API запросы
# Проверить headers и response
```

### Logs

```javascript
// В компоненте
console.log('User:', user)
console.log('Auth state:', { isAuthenticated, loading, error })

// В API клиенте
console.log('Response:', response)
```

---

## 🚨 Common Issues

### Issue: "Cannot GET /api/v1/auth/..."

**Решение:** Убедись что backend запущен:
```bash
docker-compose ps
# Должен показать backend как "Up"
```

### Issue: CORS ошибка

**Решение:** Backend CORS конфиг уже готов, убедись что:
- `FRONTEND_URL` в .env backend содержит фронтенд URL
- `CORS_ALLOWED_ORIGINS` содержит `http://localhost:5173`

### Issue: Токены не обновляются

**Решение:** Проверь:
```javascript
// В browser DevTools Console
localStorage.getItem('access_token')
localStorage.getItem('refresh_token')

// Должны быть установлены после login
```

### Issue: "Protected Route не работает"

**Решение:** Проверь что пользователь авторизован:
```javascript
// В Redux DevTools смотри auth.isAuthenticated
// Должно быть true
```

---

## 📈 Performance

### Build Optimization
```bash
npm run build
# dist/ файлы минимизированы
# ~50-100 KB главный bundle
```

### Development
```bash
npm run dev
# HMR (Hot Module Replacement)
# Fast refresh при изменении файлов
# Instant feedback
```

---

## 🔄 Обновление зависимостей

```bash
# Проверить updates
npm outdated

# Обновить все
npm update

# Обновить конкретный пакет
npm install react@latest
```

---

## 🌐 Production Deployment

### Build для продакшена

```bash
npm run build
# Создаёт dist/ папку
```

### Docker (уже настроено)

```bash
# Frontend Dockerfile уже готов
docker build -f frontend/Dockerfile -t nachalo-frontend .
docker run -p 5173:5173 nachalo-frontend
```

### Environment для продакшена

```env
VITE_API_BASE_URL=https://api.nachalo-rosta.com
VITE_ENABLE_SENTRY=true
VITE_SENTRY_DSN=https://your-sentry-dsn
```

---

## 📚 Дополнительные ресурсы

- [React Documentation](https://react.dev/)
- [Vite Documentation](https://vitejs.dev/)
- [Tailwind CSS](https://tailwindcss.com/)
- [daisyUI](https://daisyui.com/)
- [Redux Toolkit](https://redux-toolkit.js.org/)
- [React Router](https://reactrouter.com/)
- [React Hook Form](https://react-hook-form.com/)
- [Zod](https://zod.dev/)

---

**Готово! 🎉 Frontend запущен и работает с Backend API!**

Если есть вопросы, смотри:
- PHASE_2_SUMMARY.md — детальное описание
- API_TESTING_GUIDE.md — как тестировать API
- QUICKSTART.md — быстрый старт всего проекта
