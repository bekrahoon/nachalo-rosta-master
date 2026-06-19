import { useState, useEffect, useCallback } from 'react';
import { Bookmark, ExternalLink } from 'lucide-react';
import apiClient from '../api/client';

export const Portfolio = () => {
  const [savedListings, setSavedListings] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  const loadSaved = useCallback(() => {
    setLoading(true);
    setError(null);

    apiClient
      .get('/portfolio/')
      .then((res) => {
        setSavedListings(res.data.saved_listings || []);
      })
      .catch(() => setError('Не удалось загрузить избранное.'))
      .finally(() => setLoading(false));
  }, []);

  useEffect(() => {
    loadSaved();
  }, [loadSaved]);

  const handleRemove = (listingId) => {
    apiClient
      .delete(`/portfolio/saved/${listingId}/`)
      .then(() => {
        setSavedListings((prev) => prev.filter((s) => s.listing.id !== listingId));
      })
      .catch(() => setError('Не удалось убрать из избранного.'));
  };

  return (
    <div className="space-y-6">
      <div className="hero bg-gradient-to-r from-purple-400 to-pink-400 rounded-lg">
        <div className="hero-content text-white text-center">
          <div>
            <h1 className="text-4xl font-bold mb-4">
              <Bookmark className="inline w-10 h-10 mr-2 mb-1" />
              Избранное
            </h1>
            <p className="text-lg">
              Сохранённые возможности — нажмите закладку на карточке, чтобы добавить сюда
            </p>
          </div>
        </div>
      </div>

      {error && (
        <div className="alert alert-error">
          <span>{error}</span>
        </div>
      )}

      {loading && (
        <div className="flex justify-center py-12">
          <span className="loading loading-spinner loading-lg text-primary" />
        </div>
      )}

      {!loading && savedListings.length > 0 && (
        <div className="space-y-3">
          {savedListings.map((saved) => (
            <div
              key={saved.id}
              className="card bg-base-100 shadow-lg"
            >
              <div className="card-body flex-row items-center justify-between gap-4 py-4">
                <div className="flex-1 min-w-0">
                  <div className="badge badge-secondary badge-outline mb-1">
                    {saved.listing.listing_type_display}
                  </div>
                  <h4 className="font-semibold truncate">{saved.listing.title}</h4>
                  {saved.listing.organization_name && (
                    <p className="text-sm text-gray-600">{saved.listing.organization_name}</p>
                  )}
                  {saved.listing.region && (
                    <p className="text-xs text-gray-400">{saved.listing.region}</p>
                  )}
                </div>
                <div className="flex items-center gap-2 flex-shrink-0">
                  {saved.listing.source_url && (
                    <a
                      href={saved.listing.source_url}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="btn btn-secondary btn-sm gap-1"
                    >
                      Перейти
                      <ExternalLink className="w-4 h-4" />
                    </a>
                  )}
                  <button
                    className="btn btn-ghost btn-sm"
                    onClick={() => handleRemove(saved.listing.id)}
                  >
                    Убрать
                  </button>
                </div>
              </div>
            </div>
          ))}
        </div>
      )}

      {!loading && savedListings.length === 0 && (
        <div className="card bg-base-100 shadow-lg">
          <div className="card-body text-center py-12">
            <Bookmark className="w-16 h-16 mx-auto text-gray-400 mb-4" />
            <h3 className="text-lg font-semibold mb-2">Пока ничего не сохранено</h3>
            <p className="text-gray-600">
              Нажмите на значок закладки на карточке возможности,
              чтобы добавить её в избранное.
            </p>
          </div>
        </div>
      )}
    </div>
  );
};

export default Portfolio;
