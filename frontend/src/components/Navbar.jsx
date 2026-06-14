import { Link, useNavigate } from 'react-router-dom';
import { Menu, LogOut, User, Settings } from 'lucide-react';
import { useAuth } from '../hooks/useAuth';

export const Navbar = () => {
  const navigate = useNavigate();
  const { isAuthenticated, user, logout } = useAuth();

  const handleLogout = async () => {
    await logout();
    navigate('/login');
  };

  return (
    <div className="navbar bg-base-100 shadow-sm sticky top-0 z-50">
      <div className="flex-1">
        <Link to="/" className="btn btn-ghost normal-case text-xl">
          🚀 Начало Роста
        </Link>

        {isAuthenticated && (
          <div className="hidden md:flex gap-1 ml-4">
            <Link to="/dashboard" className="btn btn-ghost btn-sm">
              Главная
            </Link>
            <Link to="/opportunities" className="btn btn-ghost btn-sm">
              Возможности
            </Link>
            <Link to="/recommendations" className="btn btn-ghost btn-sm">
              AI Рекомендации
            </Link>
          </div>
        )}
      </div>

      <div className="flex-none">
        {isAuthenticated ? (
          <div className="dropdown dropdown-end">
            <label tabIndex={0} className="btn btn-ghost btn-circle avatar">
              <div className="w-10 rounded-full bg-primary text-white flex items-center justify-center font-bold">
                {user?.first_name?.charAt(0) || 'U'}
              </div>
            </label>
            <ul
              tabIndex={0}
              className="dropdown-content z-[1] menu p-2 shadow bg-base-100 rounded-box w-52"
            >
              <li className="menu-title">
                <span>{user?.full_name || user?.email}</span>
              </li>
              <li>
                <Link to="/profile" className="flex items-center gap-2">
                  <User className="w-4 h-4" />
                  Мой профиль
                </Link>
              </li>
              <li>
                <Link to="/settings" className="flex items-center gap-2">
                  <Settings className="w-4 h-4" />
                  Настройки
                </Link>
              </li>
              <li>
                <button
                  onClick={handleLogout}
                  className="flex items-center gap-2 text-error"
                >
                  <LogOut className="w-4 h-4" />
                  Выход
                </button>
              </li>
            </ul>
          </div>
        ) : (
          <div className="gap-2 flex">
            <Link to="/login" className="btn btn-sm btn-ghost">
              Вход
            </Link>
            <Link to="/register" className="btn btn-sm btn-primary">
              Регистрация
            </Link>
          </div>
        )}
      </div>
    </div>
  );
};

export default Navbar;
