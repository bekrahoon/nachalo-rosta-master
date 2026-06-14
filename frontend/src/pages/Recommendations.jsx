import { useState, useEffect, useCallback } from 'react';
import { Link } from 'react-router-dom';
import { Sparkles, Heart, AlertCircle, ArrowRight, RefreshCw } from 'lucide-react';
import apiClient from '../api/client';

const formatDate = (value) => {
  if (!value) return null;
  try {
    return new Date(value).toLocaleDateString('ru-RU');
  } catch {
    return null;
  }
};

export const Recommendations = () => {
  const [recommendations, setRecommendations] = useState([]);
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);
  const [error, setError] = useState(null);
  const [message, setMessage] = useState(null);

  const loadRecommendations = useCallback(() => {
    setLoading(true);
    setError(null);

    apiClient
      .get('/recommendations/')
      .then((res) => setRecommendations(res.data.results || []))
      .catch(() => {
        setError('Не удалось загрузить рекомендации. Попробуйте позже.');
        setRecommendations([]);
      })
      .finally(() => setLoading(false));
  }, []);

  useEffect(() => {
    loadRecommendations();
  }, [loadRecommendations]);

  const handleRefresh = () => {
    setRefreshing(true);
    setMessage(null);

    apiClient
      .post('/recommendations/refresh/')
      .then((res) => {
        setMessage(res.data.message || 'Генерация рекомендаций запущена.');
      })
      .catch(() => {
        setError('Не удалось запустить генерацию рекомендаций.');
      })
      .finally(() => setRefreshing(false));
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="hero bg-gradient-to-r from-blue-400 to-cyan-400 rounded-lg">
        <div className="hero-content text-white text-center">
          <div>
            <h1 className="text-4xl font-bold mb-4">🤖 AI Рекомендации</h1>
            <p className="text-lg">
              Персонализированные волонтёрские возможности на основе ваших интересов
            </p>
          </div>
        </div>
      </div>

      {/* Info Card */}
      <div className="alert alert-info">
        <AlertCircle className="w-6 h-6" />
        <span>
          Эти рекомендации основаны на вашем профиле, интересах и истории волонтёрства
        </span>
      </div>

      {message && (
        <div className="alert alert-success">
          <span>{message}</span>
        </div>
      )}

      {error && (
        <div className="alert alert-error">
          <span>{error}</span>
        </div>
      )}

      {/* Refresh */}
      <div className="flex justify-end">
        <button className="btn btn-primary gap-2" onClick={handleRefresh} disabled={refreshing}>
          <RefreshCw className={`w-4 h-4 ${refreshing ? 'animate-spin' : ''}`} />
          {refreshing ? 'Запуск...' : 'Обновить рекомендации'}
        </button>
      </div>

      {/* Recommendations List */}
      <div>
        <h2 className="text-2xl font-bold mb-4">
          <Sparkles className="w-6 h-6 inline mr-2" />
          Рекомендуемые события
        </h2>

        {loading && (
          <div className="flex justify-center py-12">
            <span className="loading loading-spinner loading-lg text-primary" />
          </div>
        )}

        {!loading && recommendations.length === 0 && (
          <div className="card bg-base-100 shadow-lg">
            <div className="card-body text-center py-12">
              <Sparkles className="w-16 h-16 mx-auto text-gray-400 mb-4" />
              <h3 className="text-lg font-semibold mb-2">Рекомендаций пока нет</h3>
              <p className="text-gray-600">
                Заполните профиль с вашими интересами и навыками, затем нажмите
                «Обновить рекомендации» — AI подберёт подходящие мероприятия.
              </p>
            </div>
          </div>
        )}

        {!loading && recommendations.length > 0 && (
          <div className="space-y-4">
            {recommendations.map((rec) => {
              const event = rec.event || {};
              const startDate = formatDate(event.start_date);
              const matchScore = Math.round(rec.match_score ?? 0);

              return (
                <div key={rec.id} className="card bg-base-100 shadow-lg hover:shadow-xl transition">
                  <div className="card-body">
                    <div className="flex justify-between items-start mb-4">
                      <div className="flex-1">
                        <h3 className="card-title text-lg">{event.title}</h3>
                        {rec.reason && (
                          <p className="text-sm text-gray-600 flex items-center gap-1 mt-2">
                            <Heart className="w-4 h-4 text-error" />
                            {rec.reason}
                          </p>
                        )}
                      </div>

                      {/* Match Score */}
                      <div className="flex flex-col items-center">
                        <div className="radial-progress text-primary" style={{ '--value': matchScore }}>
                          {matchScore}%
                        </div>
                        <span className="text-xs text-gray-600 mt-1">совпадение</span>
                      </div>
                    </div>

                    {/* Details */}
                    <div className="grid grid-cols-2 md:grid-cols-4 gap-4 py-4 border-y border-base-300">
                      <div>
                        <div className="text-xs text-gray-600">Дата</div>
                        <div className="font-semibold text-sm">{startDate || '—'}</div>
                      </div>
                      <div>
                        <div className="text-xs text-gray-600">Локация</div>
                        <div className="font-semibold text-sm">
                          {event.is_online ? 'Онлайн' : event.location || '—'}
                        </div>
                      </div>
                      <div>
                        <div className="text-xs text-gray-600">Часы</div>
                        <div className="font-semibold text-sm">{event.volunteer_hours ?? 0} часов</div>
                      </div>
                      <div>
                        <div className="text-xs text-gray-600">Соответствие</div>
                        <div className="font-semibold text-sm text-primary">{matchScore}%</div>
                      </div>
                    </div>

                    {/* Actions */}
                    <div className="card-actions justify-end pt-4">
                      <Link to={`/events/${event.id}`} className="btn btn-primary btn-sm gap-1">
                        Подробнее
                        <ArrowRight className="w-4 h-4" />
                      </Link>
                    </div>
                  </div>
                </div>
              );
            })}
          </div>
        )}
      </div>
    </div>
  );
};

export default Recommendations;
