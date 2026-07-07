import apiClient from './client';

// Регистрация
export const registerUser = async (data) => {
  const response = await apiClient.post('/auth/register/', data);
  return response.data;
};

// Проверка email доступности
export const checkEmailAvailability = async (email) => {
  const response = await apiClient.post('/auth/check-email/', { email });
  return response.data;
};

// Вход (получение токенов)
export const loginUser = async (email, password) => {
  const response = await apiClient.post('/auth/token/', { email, password });
  return response.data;
};

// Обновление access token
export const refreshToken = async (refreshToken) => {
  const response = await apiClient.post('/auth/token/refresh/', {
    refresh: refreshToken,
  });
  return response.data;
};

// Выход (logout)
export const logoutUser = async (refreshToken) => {
  const response = await apiClient.post('/auth/logout/', {
    refresh: refreshToken,
  });
  return response.data;
};

// Получить профиль текущего пользователя
export const getProfile = async () => {
  const response = await apiClient.get('/auth/profile/');
  return response.data;
};

// Обновить профиль
export const updateProfile = async (data) => {
  const response = await apiClient.put('/auth/profile/', data);
  return response.data;
};

// Изменить пароль
export const changePassword = async (data) => {
  const response = await apiClient.post('/auth/password/change/', data);
  return response.data;
};

// Запрос на сброс пароля
export const requestPasswordReset = async (email) => {
  const response = await apiClient.post('/auth/password-reset/request/', { email });
  return response.data;
};

// Подтверждение сброса пароля
export const confirmPasswordReset = async (data) => {
  const response = await apiClient.post('/auth/password-reset/confirm/', data);
  return response.data;
};

// Проверить валидность токена
export const verifyToken = async () => {
  const response = await apiClient.post('/auth/verify-token/');
  return response.data;
};

// Получить публичный профиль пользователя
export const getUserProfile = async (userId) => {
  const response = await apiClient.get(`/auth/user/${userId}/`);
  return response.data;
};

// Social OAuth
export const getSocialAuthConfig = async () => {
  const response = await apiClient.get('/auth/social-config/');
  return response.data;
};

export const socialLogin = async (provider, code, redirectUri) => {
  const response = await apiClient.post(`/auth/social/${provider}/`, {
    code,
    redirect_uri: redirectUri,
  });
  return response.data;
};
