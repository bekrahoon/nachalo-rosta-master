import { useState, useEffect } from 'react';
import { useParams, Link } from 'react-router-dom';
import { ArrowLeft, ExternalLink, MapPin, Globe, Calendar, Building2, Bookmark } from 'lucide-react';
import apiClient from '../api/client';
import useSavedListings from '../hooks/useSavedListings';

const formatDate = (value) => {
  if (!value) return null;
  try {
    return new Date(value).toLocaleDateString('ru-RU', {
      day: 'numeric', month: 'long', year: 'numeric',
    });
  } catch {
    return null;
  }
};

export const ListingDetail = () => {
  const { id } = useParams();
  const [listing, setListing] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const { savedIds, toggleSave } = useSavedListings();

  useEffect(() => {
    setLoading(true);
    apiClient
      .get(`/aggregator/listings/${id}/`)
      .then((res) => setListing(res.data))
      .catch(() => setError('Объявление не найдено'))
      .finally(() => setLoading(false));
  }, [id]);

  if (loading) {
    return (
      <div className="flex justify-center py-20">
        <span className="loading loading-spinner loading-lg text-primary" />
      </div>
    );
  }

  if (error || !listing) {
    return (
      <div className="text-center py-20">
        <h2 className="text-2xl font-bold mb-4">{error || 'Не найдено'}</h2>
        <Link to="/opportunities" className="btn btn-primary">
          Вернуться к возможностям
        </Link>
      </div>
    );
  }

  const startDate = formatDate(listing.start_date);
  const deadline = formatDate(listing.application_deadline);
  const isSaved = savedIds.has(listing.id);

  return (
    <div className="max-w-3xl mx-auto space-y-6">
      <Link to="/opportunities" className="btn btn-ghost btn-sm gap-2">
        <ArrowLeft className="w-4 h-4" />
        Все возможности
      </Link>

      {/* Header Card */}
      <div className="card bg-base-100 shadow-xl">
        {listing.cover_image_url && (
          <figure className="h-48 md:h-64 overflow-hidden">
            <img
              src={listing.cover_image_url}
              alt={listing.title}
              className="w-full h-full object-cover"
            />
          </figure>
        )}

        <div className="card-body">
          <div className="flex items-start justify-between gap-3">
            <div>
              <div className="badge badge-primary mb-2">{listing.listing_type_display}</div>
              <h1 className="text-xl md:text-2xl font-bold">{listing.title}</h1>
            </div>
            <button
              className={`btn btn-circle btn-sm flex-shrink-0 ${isSaved ? 'btn-primary' : 'btn-ghost'}`}
              onClick={() => toggleSave(listing)}
            >
              <Bookmark className="w-4 h-4" fill={isSaved ? 'currentColor' : 'none'} />
            </button>
          </div>

          {/* Info Grid */}
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-3 mt-4">
            {listing.organization_name && (
              <div className="flex items-center gap-2 text-sm">
                <Building2 className="w-4 h-4 text-primary flex-shrink-0" />
                <span>{listing.organization_name}</span>
              </div>
            )}
            {listing.is_online ? (
              <div className="flex items-center gap-2 text-sm">
                <Globe className="w-4 h-4 text-primary flex-shrink-0" />
                <span>Онлайн</span>
              </div>
            ) : listing.region ? (
              <div className="flex items-center gap-2 text-sm">
                <MapPin className="w-4 h-4 text-primary flex-shrink-0" />
                <span>{listing.region}</span>
              </div>
            ) : null}
            {startDate && (
              <div className="flex items-center gap-2 text-sm">
                <Calendar className="w-4 h-4 text-primary flex-shrink-0" />
                <span>Начало: {startDate}</span>
              </div>
            )}
            {deadline && (
              <div className="flex items-center gap-2 text-sm">
                <Calendar className="w-4 h-4 text-error flex-shrink-0" />
                <span>Дедлайн: {deadline}</span>
              </div>
            )}
          </div>

          {/* Tags */}
          {listing.tags?.length > 0 && (
            <div className="flex flex-wrap gap-2 mt-4">
              {listing.tags.map((tag) => (
                <span key={tag.id} className="badge badge-outline">{tag.name}</span>
              ))}
            </div>
          )}
        </div>
      </div>

      {/* Description */}
      <div className="card bg-base-100 shadow-xl">
        <div className="card-body">
          <h2 className="card-title text-lg mb-2">Описание</h2>
          <p className="text-gray-700 whitespace-pre-line leading-relaxed">
            {listing.description || 'Описание отсутствует. Перейдите к источнику для полной информации.'}
          </p>
        </div>
      </div>

      {/* Source Link */}
      {listing.source_url && (
        <div className="card bg-gradient-to-r from-primary/10 to-accent/10 shadow">
          <div className="card-body py-5">
            <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4">
              <div>
                <h3 className="font-semibold">Источник</h3>
                <p className="text-sm text-gray-600 mt-1">
                  Полная информация, условия участия и подача заявки — на странице источника
                </p>
              </div>
              <a
                href={listing.source_url}
                target="_blank"
                rel="noopener noreferrer"
                className="btn btn-primary gap-2 w-full sm:w-auto"
              >
                Перейти к источнику
                <ExternalLink className="w-4 h-4" />
              </a>
            </div>
          </div>
        </div>
      )}

      {listing.source_name && (
        <p className="text-xs text-gray-400 text-center">
          Собрано из: {listing.source_name}
        </p>
      )}
    </div>
  );
};

export default ListingDetail;
