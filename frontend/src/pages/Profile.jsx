import { useEffect, useState } from 'react';
import { useForm } from 'react-hook-form';
import { useAuth } from '../hooks/useAuth';
import { Alert } from '../components';
import { User, Mail, Phone, MapPin, Calendar, Edit2, X } from 'lucide-react';

const formatDate = (value) => {
  if (!value) return null;
  try {
    return new Date(value).toLocaleDateString('ru-RU');
  } catch {
    return null;
  }
};

export const Profile = () => {
  const { user, updateProfile, loading, error, message, clearError, clearMessage } = useAuth();
  const [isEditing, setIsEditing] = useState(false);

  const { register, handleSubmit, reset, formState: { errors } } = useForm({
    defaultValues: user || {},
  });

  useEffect(() => {
    if (user) {
      reset(user);
    }
  }, [user, reset]);

  const onSubmit = async (data) => {
    clearError();
    const result = await updateProfile(data);
    if (!result.rejected) {
      setIsEditing(false);
    }
  };

  if (!user) {
    return <div className="text-center py-8">Загрузка профиля...</div>;
  }

  return (
    <div className="max-w-2xl mx-auto space-y-6">
      {/* Header */}
      <div className="card bg-base-100 shadow-xl">
        <div className="card-body">
          <div className="flex items-start justify-between">
            <div className="flex items-center gap-4">
              <div className="avatar placeholder">
                <div className="bg-primary text-white w-20 rounded-full flex items-center justify-center text-2xl font-bold">
                  {user?.first_name?.charAt(0) || 'U'}
                </div>
              </div>
              <div>
                <h1 className="text-3xl font-bold">{user?.full_name}</h1>
                <p className="text-gray-600">{user?.email}</p>
                <div className="badge badge-primary mt-2">
                  {user?.status_label || 'Гость'}
                </div>
              </div>
            </div>
            <button
              onClick={() => setIsEditing(!isEditing)}
              className="btn btn-ghost btn-sm"
            >
              {isEditing ? <X className="w-5 h-5" /> : <Edit2 className="w-5 h-5" />}
            </button>
          </div>

        </div>
      </div>

      {/* Alerts */}
      {error && <Alert type="error" message={error} onClose={clearError} />}
      {message && <Alert type="success" message={message} onClose={clearMessage} />}

      {/* Profile Form */}
      <div className="card bg-base-100 shadow-xl">
        <div className="card-body">
          <h2 className="card-title">Личная информация</h2>

          {isEditing ? (
            <form onSubmit={handleSubmit(onSubmit)} className="space-y-4">
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div className="form-control">
                  <label className="label">
                    <span className="label-text">Имя</span>
                  </label>
                  <input
                    type="text"
                    className="input input-bordered"
                    {...register('first_name')}
                  />
                </div>
                <div className="form-control">
                  <label className="label">
                    <span className="label-text">Фамилия</span>
                  </label>
                  <input
                    type="text"
                    className="input input-bordered"
                    {...register('last_name')}
                  />
                </div>
              </div>

              <div className="form-control">
                <label className="label">
                  <span className="label-text">Отчество</span>
                </label>
                <input
                  type="text"
                  className="input input-bordered"
                  {...register('middle_name')}
                />
              </div>

              <div className="form-control">
                <label className="label">
                  <span className="label-text">Статус-бейдж</span>
                </label>
                <input
                  type="text"
                  className="input input-bordered"
                  list="status-label-options"
                  placeholder="Гость"
                  maxLength={50}
                  {...register('status_label')}
                />
                <datalist id="status-label-options">
                  <option value="Гость" />
                  <option value="Волонтёр" />
                  <option value="Стажёр" />
                  <option value="Студент" />
                  <option value="Организатор" />
                </datalist>
              </div>

              <div className="form-control">
                <label className="label">
                  <span className="label-text">О себе</span>
                </label>
                <textarea
                  className="textarea textarea-bordered"
                  rows="4"
                  maxLength={500}
                  {...register('bio')}
                />
              </div>

              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div className="form-control">
                  <label className="label">
                    <span className="label-text">Телефон</span>
                  </label>
                  <input
                    type="tel"
                    className="input input-bordered"
                    {...register('phone')}
                  />
                </div>
                <div className="form-control">
                  <label className="label">
                    <span className="label-text">Дата рождения</span>
                  </label>
                  <input
                    type="date"
                    className="input input-bordered"
                    {...register('date_of_birth')}
                  />
                </div>
              </div>

              <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                <div className="form-control">
                  <label className="label">
                    <span className="label-text">Страна</span>
                  </label>
                  <input
                    type="text"
                    className="input input-bordered"
                    {...register('country')}
                  />
                </div>
                <div className="form-control">
                  <label className="label">
                    <span className="label-text">Город</span>
                  </label>
                  <input
                    type="text"
                    className="input input-bordered"
                    {...register('city')}
                  />
                </div>
                <div className="form-control">
                  <label className="label">
                    <span className="label-text">Регион</span>
                  </label>
                  <input
                    type="text"
                    className="input input-bordered"
                    {...register('region')}
                  />
                </div>
              </div>

              <div className="flex gap-2 justify-end pt-4">
                <button
                  type="button"
                  onClick={() => setIsEditing(false)}
                  className="btn btn-ghost"
                >
                  Отмена
                </button>
                <button
                  type="submit"
                  disabled={loading}
                  className="btn btn-primary"
                >
                  {loading ? 'Сохранение...' : 'Сохранить'}
                </button>
              </div>
            </form>
          ) : (
            <div className="space-y-4">
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div className="flex items-center gap-2">
                  <User className="w-5 h-5 text-gray-400" />
                  <div>
                    <div className="text-sm text-gray-600">Имя</div>
                    <div className="font-semibold">{user?.first_name}</div>
                  </div>
                </div>
                <div className="flex items-center gap-2">
                  <User className="w-5 h-5 text-gray-400" />
                  <div>
                    <div className="text-sm text-gray-600">Фамилия</div>
                    <div className="font-semibold">{user?.last_name}</div>
                  </div>
                </div>
              </div>

              {user?.middle_name && (
                <div className="flex items-center gap-2">
                  <User className="w-5 h-5 text-gray-400" />
                  <div>
                    <div className="text-sm text-gray-600">Отчество</div>
                    <div className="font-semibold">{user?.middle_name}</div>
                  </div>
                </div>
              )}

              <div className="flex items-center gap-2">
                <Mail className="w-5 h-5 text-gray-400" />
                <div>
                  <div className="text-sm text-gray-600">Email</div>
                  <div className="font-semibold">{user?.email}</div>
                </div>
              </div>

              {user?.phone && (
                <div className="flex items-center gap-2">
                  <Phone className="w-5 h-5 text-gray-400" />
                  <div>
                    <div className="text-sm text-gray-600">Телефон</div>
                    <div className="font-semibold">{user?.phone}</div>
                  </div>
                </div>
              )}

              {formatDate(user?.date_of_birth) && (
                <div className="flex items-center gap-2">
                  <Calendar className="w-5 h-5 text-gray-400" />
                  <div>
                    <div className="text-sm text-gray-600">Дата рождения</div>
                    <div className="font-semibold">{formatDate(user?.date_of_birth)}</div>
                  </div>
                </div>
              )}

              {(user?.city || user?.region || user?.country) && (
                <div className="flex items-center gap-2">
                  <MapPin className="w-5 h-5 text-gray-400" />
                  <div>
                    <div className="text-sm text-gray-600">Локация</div>
                    <div className="font-semibold">
                      {[user?.city, user?.region, user?.country].filter(Boolean).join(', ')}
                    </div>
                  </div>
                </div>
              )}

              {user?.bio && (
                <div>
                  <div className="text-sm text-gray-600 mb-1">О себе</div>
                  <p className="text-gray-700">{user?.bio}</p>
                </div>
              )}
            </div>
          )}
        </div>
      </div>

      {/* Quick Links */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        <a href="/portfolio" className="card bg-base-100 shadow hover:shadow-lg transition cursor-pointer">
          <div className="card-body">
            <h3 className="card-title">📄 Портфолио</h3>
            <p>Управляйте профилем и сохранёнными возможностями</p>
          </div>
        </a>
        <a href="/settings" className="card bg-base-100 shadow hover:shadow-lg transition cursor-pointer">
          <div className="card-body">
            <h3 className="card-title">⚙️ Настройки</h3>
            <p>Измените пароль и параметры конфиденциальности</p>
          </div>
        </a>
      </div>
    </div>
  );
};

export default Profile;
