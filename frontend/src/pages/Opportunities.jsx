import { useState, useEffect, useCallback, useRef } from 'react';
import { Search, Filter, ChevronDown } from 'lucide-react';
import apiClient from '../api/client';
import ListingCard from '../components/ListingCard';
import useSavedListings from '../hooks/useSavedListings';

export const Opportunities = () => {
  const { savedIds, toggleSave } = useSavedListings();
  const [listings, setListings] = useState([]);
  const [count, setCount] = useState(0);
  const [page, setPage] = useState(1);
  const [hasMore, setHasMore] = useState(false);
  const [facets, setFacets] = useState({ listing_types: [], regions: [], tags: [] });
  const [searchQuery, setSearchQuery] = useState('');
  const [debouncedQuery, setDebouncedQuery] = useState('');
  const [selectedType, setSelectedType] = useState('');
  const [selectedRegion, setSelectedRegion] = useState('');
  const [loading, setLoading] = useState(true);
  const [loadingMore, setLoadingMore] = useState(false);
  const [error, setError] = useState(null);
  const debounceTimer = useRef(null);

  useEffect(() => {
    apiClient
      .get('/aggregator/listings/facets/')
      .then((res) => setFacets(res.data))
      .catch(() => {});
  }, []);

  useEffect(() => {
    debounceTimer.current = setTimeout(() => {
      setDebouncedQuery(searchQuery);
    }, 400);
    return () => clearTimeout(debounceTimer.current);
  }, [searchQuery]);

  const loadListings = useCallback(() => {
    setLoading(true);
    setError(null);
    setPage(1);

    const params = {};
    if (debouncedQuery) params.search = debouncedQuery;
    if (selectedType) params.listing_type = selectedType;
    if (selectedRegion) params.region = selectedRegion;

    apiClient
      .get('/aggregator/listings/', { params })
      .then((res) => {
        const results = res.data.results || [];
        setListings(results);
        setCount(res.data.count ?? 0);
        setHasMore(!!res.data.next);
      })
      .catch(() => {
        setError('Не удалось загрузить объявления. Попробуйте позже.');
        setListings([]);
        setCount(0);
        setHasMore(false);
      })
      .finally(() => setLoading(false));
  }, [debouncedQuery, selectedType, selectedRegion]);

  useEffect(() => {
    loadListings();
  }, [loadListings]);

  const loadMore = () => {
    if (!hasMore || loadingMore) return;
    setLoadingMore(true);
    const nextPageNum = page + 1;

    const params = { page: nextPageNum };
    if (debouncedQuery) params.search = debouncedQuery;
    if (selectedType) params.listing_type = selectedType;
    if (selectedRegion) params.region = selectedRegion;

    apiClient
      .get('/aggregator/listings/', { params })
      .then((res) => {
        setListings((prev) => [...prev, ...(res.data.results || [])]);
        setPage(nextPageNum);
        setHasMore(!!res.data.next);
      })
      .catch(() => {})
      .finally(() => setLoadingMore(false));
  };

  const handleSearchSubmit = (e) => {
    e.preventDefault();
    clearTimeout(debounceTimer.current);
    setDebouncedQuery(searchQuery);
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="hero bg-gradient-to-r from-primary to-accent rounded-lg">
        <div className="hero-content text-white text-center">
          <div>
            <h1 className="text-2xl md:text-4xl font-bold mb-4">Возможности</h1>
            <p className="text-lg">
              Хакатоны, стажировки, гранты и IT-конкурсы — собрано из реальных источников
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
                <option value="">Все типы</option>
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
        Найдено: <span className="font-bold">{count}</span> | Показано: <span className="font-bold">{listings.length}</span>
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
          {listings.map((listing) => (
            <ListingCard
              key={listing.id}
              listing={listing}
              isSaved={savedIds.has(listing.id)}
              onToggleSave={toggleSave}
            />
          ))}
        </div>
      )}

      {/* Load More */}
      {!loading && hasMore && (
        <div className="flex justify-center pt-4">
          <button
            className="btn btn-outline btn-primary gap-2"
            onClick={loadMore}
            disabled={loadingMore}
          >
            {loadingMore ? (
              <span className="loading loading-spinner loading-sm" />
            ) : (
              <ChevronDown className="w-5 h-5" />
            )}
            Загрузить ещё
          </button>
        </div>
      )}

      {/* Empty State */}
      {!loading && !error && listings.length === 0 && (
        <div className="card bg-base-100 shadow-lg">
          <div className="card-body text-center py-12">
            <Filter className="w-16 h-16 mx-auto text-gray-400 mb-4" />
            <h3 className="text-lg font-semibold mb-2">Объявлений не найдено</h3>
            <p className="text-gray-600">
              Попробуйте изменить фильтры или поисковый запрос.
            </p>
          </div>
        </div>
      )}
    </div>
  );
};

export default Opportunities;
