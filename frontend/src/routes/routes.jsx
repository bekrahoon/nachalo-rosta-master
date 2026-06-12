import { createBrowserRouter } from 'react-router-dom';
import Layout from '../components/Layout';
import { ProtectedRoute } from '../components/ProtectedRoute';
import {
  Home,
  Login,
  Register,
  Dashboard,
  Profile,
  Settings,
  Events,
  Opportunities,
  Achievements,
  Portfolio,
  Recommendations,
} from '../pages';

export const router = createBrowserRouter([
  {
    path: '/',
    element: <Layout />,
    errorElement: <div className="text-center py-8">Страница не найдена</div>,
    children: [
      {
        index: true,
        element: <Home />,
      },
      {
        path: 'login',
        element: <Login />,
      },
      {
        path: 'register',
        element: <Register />,
      },
      {
        path: 'dashboard',
        element: (
          <ProtectedRoute>
            <Dashboard />
          </ProtectedRoute>
        ),
      },
      {
        path: 'profile',
        element: (
          <ProtectedRoute>
            <Profile />
          </ProtectedRoute>
        ),
      },
      {
        path: 'settings',
        element: (
          <ProtectedRoute>
            <Settings />
          </ProtectedRoute>
        ),
      },
      {
        path: 'events',
        element: (
          <ProtectedRoute>
            <Events />
          </ProtectedRoute>
        ),
      },
      {
        path: 'opportunities',
        element: (
          <ProtectedRoute>
            <Opportunities />
          </ProtectedRoute>
        ),
      },
      {
        path: 'recommendations',
        element: (
          <ProtectedRoute>
            <Recommendations />
          </ProtectedRoute>
        ),
      },
      {
        path: 'achievements',
        element: (
          <ProtectedRoute>
            <Achievements />
          </ProtectedRoute>
        ),
      },
      {
        path: 'portfolio',
        element: (
          <ProtectedRoute>
            <Portfolio />
          </ProtectedRoute>
        ),
      },
      {
        path: 'teams',
        element: (
          <ProtectedRoute>
            <div className="text-center py-8">
              <h2 className="text-2xl font-bold mb-4">👥 Команды</h2>
              <p className="text-gray-600">Функция в разработке</p>
            </div>
          </ProtectedRoute>
        ),
      },
      {
        path: 'forgot-password',
        element: (
          <div className="text-center py-8">
            <h2 className="text-2xl font-bold mb-4">🔐 Сброс пароля</h2>
            <p className="text-gray-600">Функция в разработке</p>
          </div>
        ),
      },
    ],
  },
]);

export default router;
