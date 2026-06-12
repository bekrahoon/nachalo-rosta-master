import { useState, useEffect, useCallback } from 'react';
import { MapPin, Calendar, ExternalLink, Search, Filter, Globe, Building2 } from 'lucide-react';
import apiClient from '../api/client';

const formatDate = (value) => {
  if (!value) return null;
  try {
    return new Date(value).toLocaleDateString('ru-RU');
  } catch {
    return null;
  }
};

export const Opportunities = () => {
  const [listings, setListings] = useState([]);
  const [count, setCount] = useState(0);
  const [facets, setFacets] = useState({ listing_types: [], regions: [], tags: [] });
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedType, setSelectedType] = useState('');
  const [selectedRegion, setSelectedRegion] = useState('');
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    apiClient
      .get('/aggregator/listings/facets/')
      .then((res) => setFacets(res.data))
      .catch(() => {
        // Фильтры не критичны — список объявлений работает и без них
      });
  }, []);

  const loadListings = useCallback(() => {
    setLoading(true);
    setError(null);

    const params = {};
    if (searchQuery) params.search = searchQuery;
    if (selectedType) params.listing_type = selectedType;
    if (selectedRegion) params.region = selectedRegion;

    apiClient
      .get('/aggregator/listings/', { params })
      .then((res) => {
        setListings(res.data.results || []);
        setCount(res.data.count ?? 0);
      })
      .catch(() => {
        setError('Не удалось загрузить объявления. Попробуйте позже.');
        setListings([]);
        setCount(0);
      })
      .finally(() => setLoading(false));
  }, [searchQuery, selectedType, selectedRegion]);

  useEffect(() => {
    loadListings();
  }, [loadListings]);

  const handleSearchSubmit = (e) => {
    e.preventDefault();
    loadListings();
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="hero bg-gradient-to-r from-primary to-accent rounded-lg">
        <div className="hero-content text-white text-center">
          <div>
            <h1 className="text-4xl font-bold mb-4">🌍 Возможности</h1>
            <p className="text-lg">
              Волонтёрство, хакатоны, олимпиады, гранты и форумы — собрано из реальных источников
            </p>
          </div>
        </div>
      </div>

      {/* Search & Filters */}
      <div className="card bg-base-100 shadow-lg">
        <form className="card-body space-y-4" onSubmit={handleSearchSubmit}>
          <div className="form-control">
            <div className="input-group flex gap-2">
              <input
                type="text"
                placeholder="Искать возможности..."
                className="input input-bordered w-full"
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
              />
              <button type="submit" className="btn btn-primary">
                <Search className="w-5 h-5" />
              </button>
            </div>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div className="form-control">
              <label className="label">
                <span className="label-text">Тип</span>
              </label>
              <select
                className="select select-bordered"
                value={selectedType}
                onChange={(e) => setSelectedType(e.target.value)}
              >
                <option value="">📋 Все типы</option>
                {facets.listing_types.map((type) => (
                  <option key={type.value} value={type.value}>
                    {type.label}
                  </option>
                ))}
              </select>
            </div>

            <div className="form-control">
              <label className="label">
                <span className="label-text">Регион</span>
              </label>
              <select
                className="select select-bordered"
                value={selectedRegion}
                onChange={(e) => setSelectedRegion(e.target.value)}
              >
                <option value="">Все регионы</option>
                {facets.regions.map((region) => (
                  <option key={region} value={region}>
                    {region}
                  </option>
                ))}
              </select>
            </div>
          </div>
        </form>
      </div>

      {/* Results Count */}
      <div className="text-sm text-gray-600">
        Найдено объявлений: <span className="font-bold">{count}</span>
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

      {/* Listings Grid */}
      {!loading && (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {listings.map((listing) => {
            const startDate = formatDate(listing.start_date);
            const deadline = formatDate(listing.application_deadline);

            return (
              <div key={listing.id} className="card bg-base-100 shadow-lg hover:shadow-xl transition">
                {/* Image */}
                {listing.cover_image_url ? (
                  <figure className="h-40 overflow-hidden">
                    <img
                      src={listing.cover_image_url}
                      alt={listing.title}
                      className="w-full h-full object-cover"
                      loading="lazy"
                    />
                  </figure>
                ) : (
                  <div className="bg-gradient-to-r from-primary/20 to-accent/20 h-32 flex items-center justify-center text-5xl">
                    🌱
                  </div>
                )}

                {/* Content */}
                <div className="card-body">
                  <div className="badge badge-primary badge-outline">
                    {listing.listing_type_display}
                  </div>
                  <h2 className="card-title text-lg">{listing.title}</h2>
                  {listing.description && (
                    <p className="text-gray-600 text-sm line-clamp-3">{listing.description}</p>
                  )}

                  {/* Details */}
                  <div className="space-y-2 my-4 text-sm">
                    {listing.organization_name && (
                      <div className="flex items-center gap-2">
                        <Building2 className="w-4 h-4 text-primary" />
                        <span>{listing.organization_name}</span>
                      </div>
                    )}
                    {listing.is_online ? (
                      <div className="flex items-center gap-2">
                        <Globe className="w-4 h-4 text-primary" />
                        <span>Онлайн</span>
                      </div>
                    ) : listing.region ? (
                      <div className="flex items-center gap-2">
                        <MapPin className="w-4 h-4 text-primary" />
                        <span>{listing.region}</span>
                      </div>
                    ) : null}
                    {startDate && (
                      <div className="flex items-center gap-2">
                        <Calendar className="w-4 h-4 text-primary" />
                        <span>{startDate}</span>
                      </div>
                    )}
                    {deadline && (
                      <div className="flex items-center gap-2">
                        <Calendar className="w-4 h-4 text-error" />
                        <span>Дедлайн: {deadline}</span>
                      </div>
                    )}
                  </div>

                  {/* Tags */}
                  {listing.tags?.length > 0 && (
                    <div className="flex flex-wrap gap-1 mb-2">
                      {listing.tags.map((tag) => (
                        <span key={tag.id} className="badge badge-ghost badge-sm">
                          {tag.name}
                        </span>
                      ))}
                    </div>
                  )}

                  {/* CTA */}
                  <div className="card-actions justify-end pt-2">
                    <a
                      href={listing.source_url}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="btn btn-primary btn-sm gap-1"
                    >
                      Перейти к источнику
                      <ExternalLink className="w-4 h-4" />
                    </a>
                  </div>
                </div>
              </div>
            );
          })}
        </div>
      )}

      {/* Empty State */}
      {!loading && !error && listings.length === 0 && (
        <div className="card bg-base-100 shadow-lg">
          <div className="card-body text-center py-12">
            <Filter className="w-16 h-16 mx-auto text-gray-400 mb-4" />
            <h3 className="text-lg font-semibold mb-2">Объявлений пока нет</h3>
            <p className="text-gray-600">
              Мы постоянно собираем новые волонтёрские и образовательные возможности.
              Загляните позже или измените фильтры.
            </p>
          </div>
        </div>
      )}
    </div>
  );
};

export default Opportunities;
