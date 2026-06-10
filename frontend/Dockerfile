FROM node:20-alpine

WORKDIR /app

# Копируем package.json
COPY package.json ./

# Устанавливаем зависимости
RUN npm install

# Копируем исходный код
COPY . .

# Expose порт
EXPOSE 5173

# Запуск dev-сервера
CMD ["npm", "run", "dev", "--", "--host"]
