import { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { Menu, LogOut, User, Settings, X, Globe, Sparkles, HeartHandshake, Bookmark, LayoutDashboard } from 'lucide-react';
import { useAuth } from '../hooks/useAuth';

export const Navbar = () => {
  const navigate = useNavigate();
  const { isAuthenticated, user, logout } = useAuth();
  const [mobileOpen, setMobileOpen] = useState(false);

  const handleLogout = async () => {
    setMobileOpen(false);
    await logout();
    navigate('/login');
  };

  const navLinks = [
    { to: '/dashboard', label: 'Главная', icon: LayoutDashboard },
    { to: '/opportunities', label: 'Возможности', icon: Globe },
    { to: '/recommendations', label: 'AI Рекомендации', icon: Sparkles },
    { to: '/teams', label: 'Найти команду', icon: HeartHandshake },
    { to: '/portfolio', label: 'Избранное', icon: Bookmark },
  ];

  return (
    <>
      <div className="navbar bg-base-100 shadow-sm sticky top-0 z-50">
        <div className="flex-1 gap-2">
          {isAuthenticated && (
            <button
              className="btn btn-ghost btn-sm md:hidden"
              onClick={() => setMobileOpen(!mobileOpen)}
            >
              {mobileOpen ? <X className="w-5 h-5" /> : <Menu className="w-5 h-5" />}
            </button>
          )}

          <Link to="/" className="btn btn-ghost normal-case text-lg sm:text-xl px-2">
            Начало Роста
          </Link>

          {isAuthenticated && (
            <div className="hidden md:flex gap-1 ml-2">
              {navLinks.map((link) => (
                <Link key={link.to} to={link.to} className="btn btn-ghost btn-sm text-sm">
                  {link.label}
                </Link>
              ))}
            </div>
          )}
        </div>

        <div className="flex-none">
          {isAuthenticated ? (
            <div className="dropdown dropdown-end">
              <label tabIndex={0} className="btn btn-ghost btn-circle avatar" onClick={() => setMobileOpen(false)}>
                {user?.avatar ? (
                  <img src={user.avatar} alt="" className="w-10 h-10 rounded-full object-cover" />
                ) : (
                  <div className="w-10 h-10 rounded-full bg-primary text-white grid place-items-center font-bold text-lg">
                    {user?.first_name?.charAt(0) || 'U'}
                  </div>
                )}
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

      {/* Mobile menu */}
      {isAuthenticated && mobileOpen && (
        <div className="md:hidden bg-base-100 border-b shadow-lg sticky top-16 z-40">
          <ul className="menu menu-compact p-2">
            {navLinks.map((link) => {
              const Icon = link.icon;
              return (
                <li key={link.to}>
                  <Link
                    to={link.to}
                    className="flex items-center gap-3 py-3"
                    onClick={() => setMobileOpen(false)}
                  >
                    <Icon className="w-5 h-5" />
                    {link.label}
                  </Link>
                </li>
              );
            })}
          </ul>
        </div>
      )}
    </>
  );
};

export default Navbar;
