import { useEffect, useRef, useState } from 'react';
import { useNavigate, useSearchParams } from 'react-router-dom';
import { useAuth } from '../hooks/useAuth';

export const OAuthCallback = () => {
  const [searchParams] = useSearchParams();
  const navigate = useNavigate();
  const { socialLogin, isAuthenticated } = useAuth();
  const [error, setError] = useState(null);
  const called = useRef(false);

  useEffect(() => {
    if (isAuthenticated) {
      navigate('/dashboard', { replace: true });
    }
  }, [isAuthenticated, navigate]);

  useEffect(() => {
    if (called.current || isAuthenticated) return;
    called.current = true;

    const code = searchParams.get('code');
    const provider = searchParams.get('provider') || localStorage.getItem('oauth_provider');
    const redirectUri = `${window.location.origin}/auth/callback?provider=${provider}`;

    if (!code || !provider) {
      setError('Отсутствует код авторизации');
      return;
    }

    localStorage.removeItem('oauth_provider');

    socialLogin(provider, code, redirectUri).then((result) => {
      if (result.meta?.requestStatus === 'fulfilled') {
        navigate('/dashboard', { replace: true });
      } else {
        setTimeout(() => {
          if (!document.hidden) {
            setError(result.payload || 'Не удалось войти. Попробуйте снова.');
          }
        }, 2000);
      }
    });
  }, []);

  if (error && !isAuthenticated) {
    return (
      <div className="min-h-screen flex items-center justify-center px-4">
        <div className="card bg-base-100 shadow-xl w-full max-w-md">
          <div className="card-body text-center">
            <h2 className="text-xl font-bold text-error mb-2">Ошибка авторизации</h2>
            <p className="text-gray-600 mb-4">{error}</p>
            <button className="btn btn-primary" onClick={() => navigate('/login')}>
              Вернуться ко входу
            </button>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen flex items-center justify-center">
      <div className="text-center">
        <span className="loading loading-spinner loading-lg text-primary" />
        <p className="mt-4 text-gray-600">Авторизация...</p>
      </div>
    </div>
  );
};

export default OAuthCallback;
