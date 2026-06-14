import { useCallback, useEffect, useState } from 'react';
import apiClient from '../api/client';

export const useSavedListings = () => {
  const [savedIds, setSavedIds] = useState(new Set());

  const loadSaved = useCallback(() => {
    apiClient
      .get('/portfolio/saved/')
      .then((res) => {
        const ids = (res.data || []).map((item) => item.listing.id);
        setSavedIds(new Set(ids));
      })
      .catch(() => {
        // Не критично — кнопка сохранения просто не будет отражать статус
      });
  }, []);

  useEffect(() => {
    loadSaved();
  }, [loadSaved]);

  const toggleSave = useCallback((listing) => {
    const isSaved = savedIds.has(listing.id);

    if (isSaved) {
      setSavedIds((prev) => {
        const next = new Set(prev);
        next.delete(listing.id);
        return next;
      });
      apiClient.delete(`/portfolio/saved/${listing.id}/`).catch(() => loadSaved());
    } else {
      setSavedIds((prev) => new Set(prev).add(listing.id));
      apiClient.post('/portfolio/saved/', { listing: listing.id }).catch(() => loadSaved());
    }
  }, [savedIds, loadSaved]);

  return { savedIds, toggleSave };
};

export default useSavedListings;
