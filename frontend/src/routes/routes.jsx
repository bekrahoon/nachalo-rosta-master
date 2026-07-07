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
  ListingDetail,
  OAuthCallback,
} from '../pages';
import StaticPage from '../pages/StaticPage';

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
        path: 'auth/callback',
        element: <OAuthCallback />,
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
        path: 'opportunities/:id',
        element: (
          <ProtectedRoute>
            <ListingDetail />
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
        path: 'about',
        element: <StaticPage type="about" />,
      },
      {
        path: 'contacts',
        element: <StaticPage type="contacts" />,
      },
      {
        path: 'help',
        element: <StaticPage type="help" />,
      },
      {
        path: 'privacy',
        element: <StaticPage type="privacy" />,
      },
      {
        path: 'terms',
        element: <StaticPage type="terms" />,
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
