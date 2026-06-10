import { useState } from 'react';
import { useForm } from 'react-hook-form';
import { useAuth } from '../hooks/useAuth';
import { Alert } from '../components';
import { Lock, Bell, Shield, LogOut } from 'lucide-react';

export const Settings = () => {
  const { changePassword, logout, loading, error, message, clearError, clearMessage } = useAuth();
  const [activeTab, setActiveTab] = useState('password');
  
  const {
    register,
    handleSubmit,
    reset,
    formState: { errors },
  } = useForm();

  const onPasswordSubmit = async (data) => {
    clearError();
    const result = await changePassword(data);
    if (!result.rejected) {
      reset();
    }
  };

  const handleLogout = async () => {
    if (window.confirm('Вы уверены что хотите выйти?')) {
      await logout();
    }
  };

  return (
    <div className="max-w-4xl mx-auto space-y-6">
      {/* Header */}
      <div className="card bg-base-100 shadow-xl">
        <div className="card-body">
          <h1 className="text-3xl font-bold">⚙️ Настройки</h1>
          <p className="text-gray-600">Управляйте параметрами вашего аккаунта</p>
        </div>
      </div>

      {/* Alerts */}
      {error && <Alert type="error" message={error} onClose={clearError} />}
      {message && <Alert type="success" message={message} onClose={clearMessage} />}

      {/* Tabs */}
      <div className="card bg-base-100 shadow-xl">
        <div className="card-body">
          <div className="tabs tabs-lifted">
            <input
              type="radio"
              name="settings_tabs"
              className="tab"
              label="🔐 Пароль"
              checked={activeTab === 'password'}
              onChange={() => setActiveTab('password')}
            />
            <div className="tab-content bg-base-100 border-base-300 rounded-box p-6">
              {activeTab === 'password' && (
                <form onSubmit={handleSubmit(onPasswordSubmit)} className="space-y-4 max-w-md">
                  <div className="form-control">
                    <label className="label">
                      <span className="label-text">Текущий пароль</span>
                    </label>
                    <input
                      type="password"
                      className="input input-bordered"
                      {...register('old_password', {
                        required: 'Введите текущий пароль',
                      })}
                    />
                    {errors.old_password && (
                      <label className="label">
                        <span className="label-text-alt text-error">
                          {errors.old_password.message}
                        </span>
                      </label>
                    )}
                  </div>

                  <div className="form-control">
                    <label className="label">
                      <span className="label-text">Новый пароль</span>
                    </label>
                    <input
                      type="password"
                      className="input input-bordered"
                      {...register('new_password', {
                        required: 'Введите новый пароль',
                        minLength: {
                          value: 12,
                          message: 'Пароль должен быть минимум 12 символов',
                        },
                      })}
                    />
                    {errors.new_password && (
                      <label className="label">
                        <span className="label-text-alt text-error">
                          {errors.new_password.message}
                        </span>
                      </label>
                    )}
                  </div>

                  <div className="form-control">
                    <label className="label">
                      <span className="label-text">Подтвердить пароль</span>
                    </label>
                    <input
                      type="password"
                      className="input input-bordered"
                      {...register('new_password_confirm', {
                        required: 'Подтвердите пароль',
                      })}
                    />
                    {errors.new_password_confirm && (
                      <label className="label">
                        <span className="label-text-alt text-error">
                          {errors.new_password_confirm.message}
                        </span>
                      </label>
                    )}
                  </div>

                  <button
                    type="submit"
                    disabled={loading}
                    className="btn btn-primary w-full"
                  >
                    {loading ? 'Сохранение...' : 'Изменить пароль'}
                  </button>
                </form>
              )}
            </div>

            <input
              type="radio"
              name="settings_tabs"
              className="tab"
              label="🔔 Уведомления"
              checked={activeTab === 'notifications'}
              onChange={() => setActiveTab('notifications')}
            />
            <div className="tab-content bg-base-100 border-base-300 rounded-box p-6">
              {activeTab === 'notifications' && (
                <div className="space-y-4 max-w-md">
                  <div className="form-control">
                    <label className="label cursor-pointer">
                      <span className="label-text">📧 Получать уведомления по email</span>
                      <input type="checkbox" className="checkbox" defaultChecked />
                    </label>
                  </div>

                  <div className="form-control">
                    <label className="label cursor-pointer">
                      <span className="label-text">🔔 Push-уведомления</span>
                      <input type="checkbox" className="checkbox" defaultChecked />
                    </label>
                  </div>

                  <div className="form-control">
                    <label className="label cursor-pointer">
                      <span className="label-text">💬 Уведомления о сообщениях</span>
                      <input type="checkbox" className="checkbox" defaultChecked />
                    </label>
                  </div>

                  <button className="btn btn-primary w-full">Сохранить</button>
                </div>
              )}
            </div>

            <input
              type="radio"
              name="settings_tabs"
              className="tab"
              label="🛡️ Безопасность"
              checked={activeTab === 'security'}
              onChange={() => setActiveTab('security')}
            />
            <div className="tab-content bg-base-100 border-base-300 rounded-box p-6">
              {activeTab === 'security' && (
                <div className="space-y-4 max-w-md">
                  <div className="card bg-base-200">
                    <div className="card-body">
                      <h3 className="card-title text-lg">Активные сессии</h3>
                      <p className="text-sm text-gray-600">Управляйте своими активными сессиями</p>
                      <button className="btn btn-sm btn-outline">Посмотреть сессии</button>
                    </div>
                  </div>

                  <div className="card bg-base-200">
                    <div className="card-body">
                      <h3 className="card-title text-lg">Двухфакторная аутентификация</h3>
                      <p className="text-sm text-gray-600">Добавьте дополнительный уровень защиты</p>
                      <button className="btn btn-sm btn-outline">Включить 2FA</button>
                    </div>
                  </div>
                </div>
              )}
            </div>
          </div>
        </div>
      </div>

      {/* Danger Zone */}
      <div className="card bg-error/10 border border-error shadow-xl">
        <div className="card-body">
          <h2 className="card-title text-error">⚠️ Опасная зона</h2>
          
          <div className="space-y-4">
            <div>
              <h3 className="font-semibold mb-2">Выход из аккаунта</h3>
              <p className="text-sm text-gray-600 mb-4">
                Завершить все сессии и выйти из аккаунта
              </p>
              <button
                onClick={handleLogout}
                className="btn btn-error btn-outline"
              >
                <LogOut className="w-5 h-5" />
                Выход
              </button>
            </div>

            <div className="divider" />

            <div>
              <h3 className="font-semibold text-error mb-2">Удалить аккаунт</h3>
              <p className="text-sm text-gray-600 mb-4">
                Это действие необратимо. Все ваши данные будут удалены.
              </p>
              <button className="btn btn-error" disabled>
                Удалить аккаунт (скоро)
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Settings;
