import { RouterProvider } from 'react-router-dom';
import { useEffect } from 'react';
import router from './routes/routes';
import { useAuth } from './hooks/useAuth';

function App() {
  const { getProfile, isAuthenticated } = useAuth();

  // Проверяем профиль при загрузке если есть токен
  useEffect(() => {
    const token = localStorage.getItem('access_token');
    if (token && !isAuthenticated) {
      getProfile();
    }
  }, []);

  // Слушаем logout events
  useEffect(() => {
    const handleLogout = () => {
      window.location.href = '/login';
    };

    window.addEventListener('logout', handleLogout);
    return () => window.removeEventListener('logout', handleLogout);
  }, []);

  return <RouterProvider router={router} />;
}

export default App;
