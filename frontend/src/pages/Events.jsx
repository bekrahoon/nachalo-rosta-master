import { useState, useEffect, useCallback } from 'react';
import { MapPin, Calendar, Users, Search, Filter, ArrowRight } from 'lucide-react';
import { Link } from 'react-router-dom';
import apiClient from '../api/client';

const CATEGORY_ICONS = {
  environment: '🌳',
  education: '📚',
  social: '❤️',
  health: '🏥',
  culture: '🎭',
  sports: '⚽',
  other: '✨',
};

const formatDate = (value) => {
  if (!value) return '—';
  try {
    return new Date(value).toLocaleDateString('ru-RU');
  } catch {
    return '—';
  }
};

export const Events = () => {
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedCategory, setSelectedCategory] = useState('all');
  const [events, setEvents] = useState([]);
  const [count, setCount] = useState(0);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  const categories = [
    { value: 'all', label: '📋 Все категории' },
    { value: 'environment', label: '🌳 Окружающая среда' },
    { value: 'education', label: '📚 Образование' },
    { value: 'social', label: '❤️ Социальная помощь' },
    { value: 'health', label: '🏥 Здравоохранение' },
    { value: 'culture', label: '🎭 Культура и искусство' },
    { value: 'sports', label: '⚽ Спорт и активный образ жизни' },
  ];

  const loadEvents = useCallback(() => {
    setLoading(true);
    setError(null);

    const params = { status: 'upcoming' };
    if (searchQuery) params.search = searchQuery;
    if (selectedCategory !== 'all') params.category = selectedCategory;

    apiClient
      .get('/events/', { params })
      .then((res) => {
        setEvents(res.data.results || []);
        setCount(res.data.count ?? 0);
      })
      .catch(() => {
        setError('Не удалось загрузить события. Попробуйте позже.');
        setEvents([]);
        setCount(0);
      })
      .finally(() => setLoading(false));
  }, [searchQuery, selectedCategory]);

  useEffect(() => {
    loadEvents();
  }, [loadEvents]);

  const handleSearchSubmit = (e) => {
    e.preventDefault();
    loadEvents();
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="hero bg-gradient-to-r from-primary to-accent rounded-lg">
        <div className="hero-content text-white text-center">
          <div>
            <h1 className="text-4xl font-bold mb-4">📅 События & Возможности</h1>
            <p className="text-lg">Найдите волонтёрские возможности, которые вас интересуют</p>
          </div>
        </div>
      </div>

      {/* Search & Filters */}
      <div className="card bg-base-100 shadow-lg">
        <form className="card-body space-y-4" onSubmit={handleSearchSubmit}>
          {/* Search */}
          <div className="form-control">
            <div className="input-group flex gap-2">
              <input
                type="text"
                placeholder="Искать события..."
                className="input input-bordered w-full"
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
              />
              <button type="submit" className="btn btn-primary">
                <Search className="w-5 h-5" />
              </button>
            </div>
          </div>

          {/* Filters */}
          <div className="form-control">
            <label className="label">
              <span className="label-text">Категория</span>
            </label>
            <select
              className="select select-bordered"
              value={selectedCategory}
              onChange={(e) => setSelectedCategory(e.target.value)}
            >
              {categories.map((cat) => (
                <option key={cat.value} value={cat.value}>
                  {cat.label}
                </option>
              ))}
            </select>
          </div>
        </form>
      </div>

      {/* Results Count */}
      <div className="text-sm text-gray-600">
        Найдено событий: <span className="font-bold">{count}</span>
      </div>

      {/* Error */}
      {error && (
        <div className="alert alert-error">
          <span>{error}</span>
        </div>
      )}

      {/* Loading */}
      {loading && (
        <div className="flex justify-center py-12">
          <span className="loading loading-spinner loading-lg text-primary" />
        </div>
      )}

      {/* Events Grid */}
      {!loading && (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {events.map((event) => (
            <div key={event.id} className="card bg-base-100 shadow-lg hover:shadow-xl transition">
              {/* Image */}
              {event.image ? (
                <figure className="h-32 overflow-hidden">
                  <img src={event.image} alt={event.title} className="w-full h-full object-cover" loading="lazy" />
                </figure>
              ) : (
                <div className="bg-gradient-to-r from-primary/20 to-accent/20 h-32 flex items-center justify-center text-6xl">
                  {CATEGORY_ICONS[event.category] || '✨'}
                </div>
              )}

              {/* Content */}
              <div className="card-body">
                <div className="badge badge-primary badge-outline">{event.category_display}</div>
                <h2 className="card-title text-lg">{event.title}</h2>
                <p className="text-gray-600 text-sm line-clamp-3">{event.description}</p>

                {/* Details */}
                <div className="space-y-2 my-4">
                  <div className="flex items-center gap-2 text-sm">
                    <Calendar className="w-4 h-4 text-primary" />
                    <span>{formatDate(event.start_date)}</span>
                  </div>
                  <div className="flex items-center gap-2 text-sm">
                    <MapPin className="w-4 h-4 text-primary" />
                    <span>{event.is_online ? 'Онлайн' : event.location}</span>
                  </div>
                  <div className="flex items-center gap-2 text-sm">
                    <Users className="w-4 h-4 text-primary" />
                    <span>
                      {event.total_volunteers}/{event.max_volunteers} волонтёров
                    </span>
                  </div>
                </div>

                {/* Progress Bar */}
                <progress
                  className="progress progress-primary w-full"
                  value={event.total_volunteers}
                  max={event.max_volunteers}
                />

                {/* CTA */}
                <div className="card-actions justify-end pt-4">
                  <Link to={`/events/${event.id}`} className="btn btn-primary btn-sm gap-1">
                    Подробнее
                    <ArrowRight className="w-4 h-4" />
                  </Link>
                </div>
              </div>
            </div>
          ))}
        </div>
      )}

      {/* Empty State */}
      {!loading && !error && events.length === 0 && (
        <div className="card bg-base-100 shadow-lg">
          <div className="card-body text-center py-12">
            <Filter className="w-16 h-16 mx-auto text-gray-400 mb-4" />
            <h3 className="text-lg font-semibold mb-2">Событий не найдено</h3>
            <p className="text-gray-600">
              Попробуйте изменить фильтры или поисковый запрос
            </p>
          </div>
        </div>
      )}

      {/* CTA Section */}
      <div className="card bg-gradient-to-r from-primary/10 to-accent/10">
        <div className="card-body text-center">
          <h3 className="card-title justify-center mb-4">Хотите создать своё событие?</h3>
          <p className="text-gray-600 mb-4">
            Если вы организатор, вы можете создать своё волонтёрское событие
          </p>
          <button className="btn btn-primary">Создать событие</button>
        </div>
      </div>
    </div>
  );
};

export default Events;
