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
  Opportunities,
  Portfolio,
  Recommendations,
  Teams,
  TeamDetail,
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
            <Teams />
          </ProtectedRoute>
        ),
      },
      {
        path: 'teams/create',
        element: (
          <ProtectedRoute>
            <Teams />
          </ProtectedRoute>
        ),
      },
      {
        path: 'teams/:id',
        element: (
          <ProtectedRoute>
            <TeamDetail />
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
