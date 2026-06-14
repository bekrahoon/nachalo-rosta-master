import { useState, useEffect, useCallback } from 'react';
import { useParams, Link } from 'react-router-dom';
import { MapPin, Calendar, Users, Clock, Mail, Phone, ArrowLeft } from 'lucide-react';
import apiClient from '../api/client';

const formatDateTime = (value) => {
  if (!value) return '—';
  try {
    return new Date(value).toLocaleString('ru-RU', {
      day: 'numeric',
      month: 'long',
      year: 'numeric',
      hour: '2-digit',
      minute: '2-digit',
    });
  } catch {
    return '—';
  }
};

export const EventDetail = () => {
  const { id } = useParams();
  const [event, setEvent] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [message, setMessage] = useState(null);

  const loadEvent = useCallback(() => {
    setLoading(true);
    setError(null);

    apiClient
      .get(`/events/${id}/`)
      .then((res) => setEvent(res.data))
      .catch(() => setError('Не удалось загрузить событие.'))
      .finally(() => setLoading(false));
  }, [id]);

  useEffect(() => {
    loadEvent();
  }, [loadEvent]);

  const handleJoin = () => {
    apiClient
      .post(`/events/${id}/join/`)
      .then((res) => {
        setMessage(res.data.message || 'Вы присоединились к событию!');
        loadEvent();
      })
      .catch((err) => {
        setMessage(err.response?.data?.event_id?.[0] || err.response?.data?.detail || 'Не удалось присоединиться к событию.');
      });
  };

  const handleLeave = () => {
    apiClient
      .post(`/events/${id}/leave/`)
      .then((res) => {
        setMessage(res.data.message || 'Вы покинули событие.');
        loadEvent();
      })
      .catch((err) => {
        setMessage(err.response?.data?.detail || 'Не удалось покинуть событие.');
      });
  };

  if (loading) {
    return (
      <div className="flex justify-center py-12">
        <span className="loading loading-spinner loading-lg text-primary" />
      </div>
    );
  }

  if (error || !event) {
    return (
      <div className="alert alert-error">
        <span>{error || 'Событие не найдено.'}</span>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <Link to="/events" className="btn btn-ghost btn-sm gap-2">
        <ArrowLeft className="w-4 h-4" />
        Назад к событиям
      </Link>

      {/* Header */}
      <div className="hero bg-gradient-to-r from-primary to-accent rounded-lg">
        <div className="hero-content text-white text-center">
          <div>
            <div className="badge badge-lg mb-2">{event.category_display}</div>
            <h1 className="text-3xl font-bold mb-2">{event.title}</h1>
            <p className="text-lg">{event.status_display}</p>
          </div>
        </div>
      </div>

      {message && (
        <div className="alert alert-info">
          <span>{message}</span>
        </div>
      )}

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Main info */}
        <div className="lg:col-span-2 space-y-4">
          <div className="card bg-base-100 shadow-lg">
            <div className="card-body">
              <h2 className="card-title">Описание</h2>
              <p className="text-gray-600 whitespace-pre-line">{event.description}</p>

              {event.required_skills && (
                <div className="mt-4">
                  <h3 className="font-semibold mb-1">Требуемые навыки</h3>
                  <p className="text-sm text-gray-600">{event.required_skills}</p>
                </div>
              )}
            </div>
          </div>

          <div className="card bg-base-100 shadow-lg">
            <div className="card-body">
              <h2 className="card-title">Контакты</h2>
              <div className="space-y-2 text-sm">
                {event.contact_person && <p>Контактное лицо: {event.contact_person}</p>}
                {event.contact_email && (
                  <div className="flex items-center gap-2">
                    <Mail className="w-4 h-4 text-primary" />
                    <span>{event.contact_email}</span>
                  </div>
                )}
                {event.contact_phone && (
                  <div className="flex items-center gap-2">
                    <Phone className="w-4 h-4 text-primary" />
                    <span>{event.contact_phone}</span>
                  </div>
                )}
                {!event.contact_person && !event.contact_email && !event.contact_phone && (
                  <p className="text-gray-500">Контактная информация не указана</p>
                )}
              </div>
            </div>
          </div>
        </div>

        {/* Sidebar */}
        <div className="space-y-4">
          <div className="card bg-base-100 shadow-lg">
            <div className="card-body space-y-3">
              <div className="flex items-center gap-2 text-sm">
                <Calendar className="w-4 h-4 text-primary" />
                <span>{formatDateTime(event.start_date)}</span>
              </div>
              <div className="flex items-center gap-2 text-sm">
                <Calendar className="w-4 h-4 text-primary" />
                <span>До {formatDateTime(event.end_date)}</span>
              </div>
              <div className="flex items-center gap-2 text-sm">
                <MapPin className="w-4 h-4 text-primary" />
                <span>{event.is_online ? 'Онлайн' : event.location}</span>
              </div>
              <div className="flex items-center gap-2 text-sm">
                <Clock className="w-4 h-4 text-primary" />
                <span>{event.volunteer_hours} часов волонтёрства</span>
              </div>
              <div className="flex items-center gap-2 text-sm">
                <Users className="w-4 h-4 text-primary" />
                <span>
                  {event.total_volunteers}/{event.max_volunteers} волонтёров
                </span>
              </div>

              <progress
                className="progress progress-primary w-full"
                value={event.total_volunteers}
                max={event.max_volunteers}
              />

              {event.organizer && (
                <div className="pt-2 border-t border-base-300 text-sm">
                  <div className="text-gray-600">Организатор</div>
                  <div className="font-semibold">{event.organizer.full_name || event.organizer.email}</div>
                </div>
              )}

              {event.is_user_joined ? (
                <button className="btn btn-outline btn-error w-full" onClick={handleLeave}>
                  Покинуть событие
                </button>
              ) : (
                <button
                  className="btn btn-primary w-full"
                  onClick={handleJoin}
                  disabled={event.available_slots <= 0}
                >
                  {event.available_slots <= 0 ? 'Мест нет' : 'Присоединиться'}
                </button>
              )}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default EventDetail;
