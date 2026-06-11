import { useState, useEffect } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { useForm } from 'react-hook-form';
import { z } from 'zod';
import { zodResolver } from '@hookform/resolvers/zod';
import { Mail, Lock, User, Phone, CheckCircle } from 'lucide-react';
import { useAuth } from '../hooks/useAuth';
import { Alert } from '../components';

// Валидация формы
const registerSchema = z.object({
  email: z.string().email('Введите корректный email'),
  first_name: z.string().min(2, 'Имя должно быть минимум 2 символа'),
  last_name: z.string().min(2, 'Фамилия должна быть минимум 2 символа'),
  phone: z.string().optional(),
  password: z
    .string()
    .min(12, 'Пароль должен быть минимум 12 символов')
    .regex(/[A-Z]/, 'Пароль должен содержать большую букву')
    .regex(/[0-9]/, 'Пароль должен содержать цифру')
    .regex(/[!@#$%^&*]/, 'Пароль должен содержать спецсимвол'),
  password_confirm: z.string(),
}).refine((data) => data.password === data.password_confirm, {
  message: 'Пароли не совпадают',
  path: ['password_confirm'],
});

export const Register = () => {
  const navigate = useNavigate();
  const { register, loading, error, message, isAuthenticated } = useAuth();
  const [registrationSuccess, setRegistrationSuccess] = useState(false);
  const [registeredEmail, setRegisteredEmail] = useState('');
  const [localError, setLocalError] = useState(null);

  const {
    register: registerField,
    handleSubmit,
    formState: { errors },
    reset,
  } = useForm({
    resolver: zodResolver(registerSchema),
  });

  useEffect(() => {
    if (isAuthenticated) {
      navigate('/dashboard', { replace: true });
    }
  }, [isAuthenticated, navigate]);

  const onSubmit = async (data) => {
    setLocalError(null);

    const result = await register(data);

    if (result.meta.requestStatus === 'rejected') {
      setLocalError(result.payload);
    } else {
      setRegistrationSuccess(true);
      setRegisteredEmail(data.email);
      reset();
    }
  };

  if (registrationSuccess) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-primary/10 to-accent/10 flex items-center justify-center px-4">
        <div className="card bg-base-100 shadow-xl w-full max-w-md">
          <div className="card-body text-center">
            <CheckCircle className="w-16 h-16 mx-auto text-success mb-4" />
            <h2 className="text-2xl font-bold mb-2">Регистрация успешна!</h2>
            <p className="text-gray-600 mb-6">
              Аккаунт <strong>{registeredEmail}</strong> создан. Теперь вы можете войти.
            </p>
            <Link to="/login" className="btn btn-primary w-full">
              Перейти ко входу
            </Link>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-primary/10 to-accent/10 flex items-center justify-center px-4 py-8">
      <div className="card bg-base-100 shadow-xl w-full max-w-md">
        <div className="card-body">
          {/* Header */}
          <div className="text-center mb-6">
            <h1 className="text-3xl font-bold mb-2">🚀 Начало Роста</h1>
            <p className="text-gray-600">Регистрация нового аккаунта</p>
          </div>

          {/* Alerts */}
          {(error || localError) && (
            <Alert type="error" message={error || localError} />
          )}
          {message && (
            <Alert type="success" message={message} />
          )}

          {/* Form */}
          <form onSubmit={handleSubmit(onSubmit)} className="space-y-3">
            {/* First Name */}
            <div className="form-control">
              <label className="label">
                <span className="label-text font-medium text-sm">Имя</span>
              </label>
              <input
                type="text"
                placeholder="Иван"
                className="input input-bordered w-full input-sm"
                {...registerField('first_name')}
              />
              {errors.first_name && (
                <label className="label">
                  <span className="label-text-alt text-error text-xs">
                    {errors.first_name.message}
                  </span>
                </label>
              )}
            </div>

            {/* Last Name */}
            <div className="form-control">
              <label className="label">
                <span className="label-text font-medium text-sm">Фамилия</span>
              </label>
              <input
                type="text"
                placeholder="Иванов"
                className="input input-bordered w-full input-sm"
                {...registerField('last_name')}
              />
              {errors.last_name && (
                <label className="label">
                  <span className="label-text-alt text-error text-xs">
                    {errors.last_name.message}
                  </span>
                </label>
              )}
            </div>

            {/* Email */}
            <div className="form-control">
              <label className="label">
                <span className="label-text font-medium text-sm">Email</span>
              </label>
              <input
                type="email"
                placeholder="you@example.com"
                className="input input-bordered w-full input-sm"
                {...registerField('email')}
              />
              {errors.email && (
                <label className="label">
                  <span className="label-text-alt text-error text-xs">
                    {errors.email.message}
                  </span>
                </label>
              )}
            </div>

            {/* Phone (optional) */}
            <div className="form-control">
              <label className="label">
                <span className="label-text font-medium text-sm">Телефон (опционально)</span>
              </label>
              <input
                type="tel"
                placeholder="+996 700 123 456"
                className="input input-bordered w-full input-sm"
                {...registerField('phone')}
              />
            </div>

            {/* Password */}
            <div className="form-control">
              <label className="label">
                <span className="label-text font-medium text-sm">Пароль</span>
              </label>
              <input
                type="password"
                placeholder="••••••••"
                className="input input-bordered w-full input-sm"
                {...registerField('password')}
              />
              {errors.password && (
                <label className="label">
                  <span className="label-text-alt text-error text-xs">
                    {errors.password.message}
                  </span>
                </label>
              )}
              <label className="label">
                <span className="label-text-alt text-xs text-gray-500">
                  Минимум 12 символов, буква, цифра, спецсимвол
                </span>
              </label>
            </div>

            {/* Password Confirm */}
            <div className="form-control">
              <label className="label">
                <span className="label-text font-medium text-sm">Подтвердить пароль</span>
              </label>
              <input
                type="password"
                placeholder="••••••••"
                className="input input-bordered w-full input-sm"
                {...registerField('password_confirm')}
              />
              {errors.password_confirm && (
                <label className="label">
                  <span className="label-text-alt text-error text-xs">
                    {errors.password_confirm.message}
                  </span>
                </label>
              )}
            </div>

            {/* Terms */}
            <label className="label cursor-pointer">
              <input type="checkbox" className="checkbox checkbox-sm" />
              <span className="label-text text-xs">
                Согласен с{' '}
                <a href="#" className="link link-primary">
                  условиями использования
                </a>
              </span>
            </label>

            {/* Submit Button */}
            <button
              type="submit"
              disabled={loading}
              className="btn btn-primary w-full btn-sm mt-2"
            >
              {loading ? 'Регистрация...' : 'Зарегистрироваться'}
            </button>
          </form>

          {/* Login Link */}
          <p className="text-center text-xs mt-4">
            Уже есть аккаунт?{' '}
            <Link to="/login" className="link link-primary font-semibold">
              Вход
            </Link>
          </p>
        </div>
      </div>
    </div>
  );
};

export default Register;
