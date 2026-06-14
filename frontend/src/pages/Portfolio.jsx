import { useState, useEffect, useCallback } from 'react';
import { Save, Bookmark, ExternalLink } from 'lucide-react';
import apiClient from '../api/client';

export const Portfolio = () => {
  const [portfolio, setPortfolio] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [message, setMessage] = useState(null);

  const [title, setTitle] = useState('');
  const [description, setDescription] = useState('');
  const [isPublic, setIsPublic] = useState(true);
  const [saving, setSaving] = useState(false);

  const loadPortfolio = useCallback(() => {
    setLoading(true);
    setError(null);

    apiClient
      .get('/portfolio/')
      .then((res) => {
        setPortfolio(res.data);
        setTitle(res.data.profile?.title || '');
        setDescription(res.data.profile?.description || '');
        setIsPublic(res.data.profile?.is_public ?? true);
      })
      .catch(() => setError('Не удалось загрузить портфолио. Попробуйте позже.'))
      .finally(() => setLoading(false));
  }, []);

  useEffect(() => {
    loadPortfolio();
  }, [loadPortfolio]);

  const handleSave = () => {
    setSaving(true);
    setMessage(null);

    apiClient
      .patch('/portfolio/profile/', {
        title,
        description,
        is_public: isPublic,
      })
      .then((res) => {
        setMessage('Изменения сохранены.');
        setPortfolio((prev) => (prev ? { ...prev, profile: res.data } : prev));
      })
      .catch(() => setError('Не удалось сохранить изменения.'))
      .finally(() => setSaving(false));
  };

  const handleRemoveSaved = (listingId) => {
    apiClient
      .delete(`/portfolio/saved/${listingId}/`)
      .then(() => {
        setPortfolio((prev) =>
          prev
            ? { ...prev, saved_listings: prev.saved_listings.filter((s) => s.listing.id !== listingId) }
            : prev
        );
      })
      .catch(() => setError('Не удалось убрать программу из сохранённых.'));
  };

  if (loading) {
    return (
      <div className="flex justify-center py-12">
        <span className="loading loading-spinner loading-lg text-primary" />
      </div>
    );
  }

  const savedListings = portfolio?.saved_listings || [];

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="hero bg-gradient-to-r from-purple-400 to-pink-400 rounded-lg">
        <div className="hero-content text-white text-center">
          <div>
            <h1 className="text-4xl font-bold mb-4">📄 Волонтёрское портфолио</h1>
            <p className="text-lg">Ваш профиль и сохранённые программы</p>
          </div>
        </div>
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

      {/* Saved Listings */}
      <div className="card bg-base-100 shadow-xl">
        <div className="card-body">
          <h2 className="card-title mb-4">
            <Bookmark className="w-5 h-5" />
            Сохранённые программы
          </h2>

          {savedListings.length > 0 ? (
            <div className="space-y-3">
              {savedListings.map((saved) => (
                <div
                  key={saved.id}
                  className="flex items-center justify-between p-4 bg-base-200 rounded-lg gap-4"
                >
                  <div className="flex-1">
                    <div className="badge badge-secondary badge-outline mb-1">
                      {saved.listing.listing_type_display}
                    </div>
                    <h4 className="font-semibold">{saved.listing.title}</h4>
                    {saved.listing.organization_name && (
                      <p className="text-sm text-gray-600">{saved.listing.organization_name}</p>
                    )}
                  </div>
                  <div className="flex items-center gap-2">
                    <a
                      href={saved.listing.source_url}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="btn btn-secondary btn-sm gap-1"
                    >
                      Перейти
                      <ExternalLink className="w-4 h-4" />
                    </a>
                    <button
                      className="btn btn-ghost btn-sm"
                      onClick={() => handleRemoveSaved(saved.listing.id)}
                    >
                      Убрать
                    </button>
                  </div>
                </div>
              ))}
            </div>
          ) : (
            <p className="text-gray-600 text-sm">
              Пока нет сохранённых программ. Нажмите на значок закладки на карточке возможности,
              чтобы добавить её сюда.
            </p>
          )}
        </div>
      </div>

      {/* Portfolio Customization */}
      <div className="card bg-base-100 shadow-xl">
        <div className="card-body">
          <h2 className="card-title mb-4">🎨 Кастомизация</h2>

          <div className="space-y-4">
            <div className="form-control">
              <label className="label">
                <span className="label-text">Заголовок портфолио</span>
              </label>
              <input
                type="text"
                placeholder="Мой волонтёрский путь"
                className="input input-bordered"
                value={title}
                onChange={(e) => setTitle(e.target.value)}
              />
            </div>

            <div className="form-control">
              <label className="label">
                <span className="label-text">Описание</span>
              </label>
              <textarea
                className="textarea textarea-bordered"
                placeholder="Расскажите о себе"
                rows="4"
                value={description}
                onChange={(e) => setDescription(e.target.value)}
              />
            </div>

            <div className="form-control">
              <label className="label cursor-pointer">
                <span className="label-text">Показывать личные данные</span>
                <input
                  type="checkbox"
                  className="checkbox"
                  checked={isPublic}
                  onChange={(e) => setIsPublic(e.target.checked)}
                />
              </label>
            </div>

            <button className="btn btn-primary gap-2" onClick={handleSave} disabled={saving}>
              <Save className="w-4 h-4" />
              {saving ? 'Сохранение...' : 'Сохранить изменения'}
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Portfolio;
