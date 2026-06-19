import { useState, useEffect, useCallback, useRef } from 'react';
import { Link } from 'react-router-dom';
import { Sparkles, AlertCircle, RefreshCw, UserCog } from 'lucide-react';
import apiClient from '../api/client';
import ListingCard from '../components/ListingCard';
import useSavedListings from '../hooks/useSavedListings';

const POLL_INTERVAL_MS = 3000;
const MAX_POLL_ATTEMPTS = 10;

export const Recommendations = () => {
  const { savedIds, toggleSave } = useSavedListings();
  const [recommendations, setRecommendations] = useState([]);
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);
  const [error, setError] = useState(null);
  const [message, setMessage] = useState(null);
  const pollTimerRef = useRef(null);
  const pollCountRef = useRef(0);
  const prevCountRef = useRef(null);

  const stopPolling = useCallback(() => {
    if (pollTimerRef.current) {
      clearTimeout(pollTimerRef.current);
      pollTimerRef.current = null;
    }
    pollCountRef.current = 0;
  }, []);

  const loadRecommendations = useCallback(() => {
    setLoading(true);
    setError(null);

    apiClient
      .get('/recommendations/')
      .then((res) => {
        const results = res.data.results || [];
        setRecommendations(results);
        prevCountRef.current = results.length;
      })
      .catch(() => {
        setError('Не удалось загрузить рекомендации. Попробуйте позже.');
        setRecommendations([]);
      })
      .finally(() => setLoading(false));
  }, []);

  const pollForResults = useCallback(() => {
    pollCountRef.current += 1;

    if (pollCountRef.current > MAX_POLL_ATTEMPTS) {
      stopPolling();
      setRefreshing(false);
      setMessage('Рекомендации генерируются. Обновите страницу через минуту.');
      return;
    }

    apiClient
      .get('/recommendations/')
      .then((res) => {
        const results = res.data.results || [];
        if (results.length !== prevCountRef.current) {
          setRecommendations(results);
          prevCountRef.current = results.length;
          stopPolling();
          setRefreshing(false);
          setMessage('Рекомендации успешно обновлены!');
        } else {
          pollTimerRef.current = setTimeout(pollForResults, POLL_INTERVAL_MS);
        }
      })
      .catch(() => {
        pollTimerRef.current = setTimeout(pollForResults, POLL_INTERVAL_MS);
      });
  }, [stopPolling]);

  useEffect(() => {
    loadRecommendations();
    return () => stopPolling();
  }, [loadRecommendations, stopPolling]);

  const handleRefresh = () => {
    stopPolling();
    setRefreshing(true);
    setMessage(null);
    setError(null);

    apiClient
      .post('/recommendations/refresh/')
      .then(() => {
        setMessage('Генерация рекомендаций запущена...');
        pollCountRef.current = 0;
        pollTimerRef.current = setTimeout(pollForResults, POLL_INTERVAL_MS);
      })
      .catch(() => {
        setRefreshing(false);
        setError('Не удалось запустить генерацию рекомендаций.');
      });
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="hero bg-gradient-to-r from-blue-400 to-cyan-400 rounded-lg">
        <div className="hero-content text-white text-center">
          <div>
            <h1 className="text-4xl font-bold mb-4">AI Рекомендации</h1>
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
        <div className={`alert ${refreshing ? 'alert-warning' : 'alert-success'}`}>
          {refreshing && (
            <span className="loading loading-spinner loading-sm" />
          )}
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
          {refreshing ? 'Генерация...' : 'Обновить рекомендации'}
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
              <p className="text-gray-600 mb-4">
                Чтобы получить персонализированные рекомендации:
              </p>
              <ol className="text-gray-600 text-left max-w-md mx-auto space-y-2 mb-6">
                <li className="flex items-start gap-2">
                  <span className="font-bold text-primary">1.</span>
                  <span>
                    Перейдите в{' '}
                    <Link to="/profile" className="link link-primary font-medium">
                      <UserCog className="w-4 h-4 inline mr-1" />
                      Мой профиль
                    </Link>{' '}
                    и укажите ваши интересы и навыки
                  </span>
                </li>
                <li className="flex items-start gap-2">
                  <span className="font-bold text-primary">2.</span>
                  <span>
                    Вернитесь на эту страницу и нажмите{' '}
                    <strong>«Обновить рекомендации»</strong>
                  </span>
                </li>
                <li className="flex items-start gap-2">
                  <span className="font-bold text-primary">3.</span>
                  <span>AI проанализирует ваш профиль и подберёт подходящие возможности</span>
                </li>
              </ol>
              <Link to="/profile" className="btn btn-outline btn-primary gap-2">
                <UserCog className="w-4 h-4" />
                Перейти в профиль
              </Link>
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
                isSaved={savedIds.has(rec.listing.id)}
                onToggleSave={toggleSave}
              />
            ))}
          </div>
        )}
      </div>
    </div>
  );
};

export default Recommendations;
