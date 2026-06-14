import { useState, useEffect, useCallback } from 'react';
import { Sparkles, AlertCircle, RefreshCw } from 'lucide-react';
import apiClient from '../api/client';
import ListingCard from '../components/ListingCard';

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
              Персонализированные возможности с других платформ на основе ваших интересов
            </p>
          </div>
        </div>
      </div>

      {/* Info Card */}
      <div className="alert alert-info">
        <AlertCircle className="w-6 h-6" />
        <span>
          Эти рекомендации основаны на вашем профиле, интересах и навыках
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
          Рекомендуемые возможности
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
                «Обновить рекомендации» — AI подберёт подходящие возможности.
              </p>
            </div>
          </div>
        )}

        {!loading && recommendations.length > 0 && (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {recommendations.map((rec) => (
              <ListingCard
                key={rec.id}
                listing={rec.listing}
                matchScore={rec.match_score}
                reason={rec.reason}
              />
            ))}
          </div>
        )}
      </div>
    </div>
  );
};

export default Recommendations;
