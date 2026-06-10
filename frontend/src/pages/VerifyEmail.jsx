import { useEffect, useState } from 'react';
import { useSearchParams, useNavigate } from 'react-router-dom';
import { CheckCircle, AlertCircle, Loader } from 'lucide-react';
import { useAuth } from '../hooks/useAuth';

export const VerifyEmail = () => {
  const [searchParams] = useSearchParams();
  const navigate = useNavigate();
  const { verifyEmail, loading, error, message } = useAuth();
  const [status, setStatus] = useState('loading'); // loading, success, error

  useEffect(() => {
    const token = searchParams.get('token');
    
    if (!token) {
      setStatus('error');
      return;
    }

    const verify = async () => {
      const result = await verifyEmail(token);
      
      if (result.rejected) {
        setStatus('error');
      } else {
        setStatus('success');
        // Redirect to login after 3 seconds
        setTimeout(() => navigate('/login'), 3000);
      }
    };

    verify();
  }, [searchParams, verifyEmail, navigate]);

  return (
    <div className="min-h-screen bg-gradient-to-br from-primary/10 to-accent/10 flex items-center justify-center px-4">
      <div className="card bg-base-100 shadow-xl w-full max-w-md">
        <div className="card-body text-center">
          {status === 'loading' && (
            <>
              <Loader className="w-16 h-16 mx-auto text-primary animate-spin mb-4" />
              <h2 className="text-2xl font-bold mb-2">Верификация email</h2>
              <p className="text-gray-600">Пожалуйста подождите...</p>
            </>
          )}

          {status === 'success' && (
            <>
              <CheckCircle className="w-16 h-16 mx-auto text-success mb-4" />
              <h2 className="text-2xl font-bold mb-2 text-success">Email подтверждён!</h2>
              <p className="text-gray-600 mb-4">
                Ваш email успешно верифицирован. Вы будете перенаправлены на страницу входа...
              </p>
              <div className="countdown font-mono text-2xl">
                <span style={{ "--value": 3 }}></span>
              </div>
            </>
          )}

          {status === 'error' && (
            <>
              <AlertCircle className="w-16 h-16 mx-auto text-error mb-4" />
              <h2 className="text-2xl font-bold mb-2 text-error">Ошибка верификации</h2>
              <p className="text-gray-600 mb-4">
                {error || 'Ссылка верификации неверна или истекла.'}
              </p>
              <button
                onClick={() => navigate('/register')}
                className="btn btn-primary w-full"
              >
                Вернуться к регистрации
              </button>
            </>
          )}
        </div>
      </div>
    </div>
  );
};

export default VerifyEmail;
