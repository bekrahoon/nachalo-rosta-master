import { useEffect, useState } from 'react';
import { useNavigate, useSearchParams } from 'react-router-dom';
import { useAuth } from '../hooks/useAuth';
import { LoadingSpinner } from '../components';

export const OAuthCallback = () => {
  const [searchParams] = useSearchParams();
  const navigate = useNavigate();
  const { socialLogin } = useAuth();
  const [error, setError] = useState(null);

  useEffect(() => {
    const code = searchParams.get('code');
    const provider = searchParams.get('provider') || localStorage.getItem('oauth_provider');
    const redirectUri = `${window.location.origin}/auth/callback?provider=${provider}`;

    if (!code || !provider) {
      setError('Missing authorization code or provider');
      return;
    }

    localStorage.removeItem('oauth_provider');

    socialLogin(provider, code, redirectUri).then((result) => {
      if (result.meta.requestStatus === 'fulfilled') {
        navigate('/dashboard', { replace: true });
      } else {
        setError(result.payload || 'Authorization failed');
      }
    });
  }, []);

  if (error) {
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
        <LoadingSpinner />
        <p className="mt-4 text-gray-600">Авторизация...</p>
      </div>
    </div>
  );
};

export default OAuthCallback;
