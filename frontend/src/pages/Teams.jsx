import { useState, useEffect, useCallback, useRef } from 'react';
import { Link } from 'react-router-dom';
import { HeartHandshake, Plus, Search, Crown, Users, UserPlus, LogOut, ExternalLink } from 'lucide-react';
import apiClient from '../api/client';

export const Teams = () => {
  const [teams, setTeams] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [searchQuery, setSearchQuery] = useState('');
  const [debouncedQuery, setDebouncedQuery] = useState('');
  const [showCreateModal, setShowCreateModal] = useState(false);
  const [creating, setCreating] = useState(false);
  const [actionTeamId, setActionTeamId] = useState(null);
  const [newTeam, setNewTeam] = useState({
    name: '',
    description: '',
    requirements: '',
    max_members: '',
    listing: '',
  });
  const [listings, setListings] = useState([]);
  const [listingsLoading, setListingsLoading] = useState(false);
  const debounceTimer = useRef(null);

  useEffect(() => {
    debounceTimer.current = setTimeout(() => {
      setDebouncedQuery(searchQuery);
    }, 400);
    return () => clearTimeout(debounceTimer.current);
  }, [searchQuery]);

  const loadTeams = useCallback(() => {
    setLoading(true);
    setError(null);

    const params = {};
    if (debouncedQuery) params.search = debouncedQuery;

    apiClient
      .get('/teams/', { params })
      .then((res) => {
        const data = res.data;
        setTeams(Array.isArray(data) ? data : data.results || []);
      })
      .catch(() => {
        setError('Не удалось загрузить заявки. Попробуйте позже.');
        setTeams([]);
      })
      .finally(() => setLoading(false));
  }, [debouncedQuery]);

  useEffect(() => {
    loadTeams();
  }, [loadTeams]);

  const loadListings = () => {
    if (listings.length > 0) return;
    setListingsLoading(true);
    apiClient
      .get('/aggregator/listings/', { params: { page_size: 100 } })
      .then((res) => {
        const data = res.data;
        setListings(Array.isArray(data) ? data : data.results || []);
      })
      .catch(() => {
        // silently fail, listing selection is optional
      })
      .finally(() => setListingsLoading(false));
  };

  const handleSearchSubmit = (e) => {
    e.preventDefault();
    clearTimeout(debounceTimer.current);
    setDebouncedQuery(searchQuery);
  };

  const handleCreateTeam = async (e) => {
    e.preventDefault();
    setCreating(true);
    const payload = {
      name: newTeam.name,
      description: newTeam.description,
      requirements: newTeam.requirements,
    };
    if (newTeam.max_members) payload.max_members = parseInt(newTeam.max_members, 10);
    if (newTeam.listing) payload.listing = newTeam.listing;
    try {
      await apiClient.post('/teams/', payload);
      setShowCreateModal(false);
      setNewTeam({ name: '', description: '', requirements: '', max_members: '', listing: '' });
      loadTeams();
    } catch (err) {
      setError(err.response?.data?.detail || 'Не удалось создать заявку');
    } finally {
      setCreating(false);
    }
  };

  const handleJoinTeam = async (teamId) => {
    setActionTeamId(teamId);
    try {
      await apiClient.post(`/teams/${teamId}/join/`);
      loadTeams();
    } catch (err) {
      setError(err.response?.data?.detail || 'Не удалось присоединиться');
    } finally {
      setActionTeamId(null);
    }
  };

  const handleLeaveTeam = async (teamId) => {
    setActionTeamId(teamId);
    try {
      await apiClient.post(`/teams/${teamId}/leave/`);
      loadTeams();
    } catch (err) {
      setError(err.response?.data?.detail || 'Не удалось покинуть команду');
    } finally {
      setActionTeamId(null);
    }
  };

  const openCreateModal = () => {
    loadListings();
    setShowCreateModal(true);
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="hero bg-gradient-to-r from-secondary to-primary rounded-lg">
        <div className="hero-content text-white text-center">
          <div>
            <h1 className="text-4xl font-bold mb-4">
              <HeartHandshake className="inline w-10 h-10 mr-2 mb-1" />
              Совместные заявки
            </h1>
            <p className="text-lg">
              Найдите напарников для хакатонов, конкурсов и проектов
            </p>
          </div>
        </div>
      </div>

      {/* Search & Create */}
      <div className="card bg-base-100 shadow-lg">
        <div className="card-body">
          <div className="flex flex-col md:flex-row gap-4">
            <form className="flex-1 flex gap-2" onSubmit={handleSearchSubmit}>
              <input
                type="text"
                placeholder="Искать заявки..."
                className="input input-bordered w-full"
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
              />
              <button type="submit" className="btn btn-primary">
                <Search className="w-5 h-5" />
              </button>
            </form>
            <button
              className="btn btn-accent gap-2"
              onClick={openCreateModal}
            >
              <Plus className="w-5 h-5" />
              Создать заявку
            </button>
          </div>
        </div>
      </div>

      {/* Error */}
      {error && (
        <div className="alert alert-error">
          <span>{error}</span>
          <button className="btn btn-sm btn-ghost" onClick={() => setError(null)}>
            x
          </button>
        </div>
      )}

      {/* Loading */}
      {loading && (
        <div className="flex justify-center py-12">
          <span className="loading loading-spinner loading-lg text-primary" />
        </div>
      )}

      {/* Teams Grid */}
      {!loading && teams.length > 0 && (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {teams.map((team) => {
            const isActing = actionTeamId === team.id;

            return (
              <div key={team.id} className="card bg-base-100 shadow-lg hover:shadow-xl transition-shadow">
                <div className="card-body">
                  <div className="flex items-start justify-between">
                    <div className="flex items-center gap-3">
                      <div className="w-12 h-12 rounded-full bg-primary/20 flex items-center justify-center">
                        <HeartHandshake className="w-6 h-6 text-primary" />
                      </div>
                      <div>
                        <Link
                          to={`/teams/${team.id}`}
                          className="card-title text-lg hover:text-primary transition-colors"
                        >
                          {team.name}
                        </Link>
                        <div className="flex items-center gap-1 text-sm text-gray-500">
                          <Crown className="w-3 h-3" />
                          <span>{team.leader?.full_name || team.leader?.email}</span>
                        </div>
                      </div>
                    </div>
                    <div className={`badge ${team.status === 'active' ? 'badge-success' : 'badge-ghost'}`}>
                      {team.status_display}
                    </div>
                  </div>

                  {team.listing && (
                    <div className="mt-2 bg-base-200 rounded-lg px-3 py-2 flex items-center gap-2">
                      <ExternalLink className="w-4 h-4 text-secondary flex-shrink-0" />
                      <div className="min-w-0">
                        <div className="text-sm font-medium truncate">{team.listing.title}</div>
                        {team.listing.listing_type_display && (
                          <span className="badge badge-secondary badge-xs">{team.listing.listing_type_display}</span>
                        )}
                      </div>
                    </div>
                  )}

                  <p className="text-gray-600 text-sm mt-2 line-clamp-2">
                    {team.description}
                  </p>

                  {team.requirements && (
                    <div className="mt-2 text-xs text-gray-500 bg-base-200 rounded-lg px-3 py-2">
                      <span className="font-semibold">Нужные навыки:</span> {team.requirements}
                    </div>
                  )}

                  <div className="flex items-center gap-4 mt-3 text-sm text-gray-500 flex-wrap">
                    <div className="flex items-center gap-1">
                      <Users className="w-4 h-4" />
                      <span>
                        {team.members_count}{team.max_members ? ` / ${team.max_members}` : ''} участников
                      </span>
                    </div>
                    {team.max_members && team.members_count >= team.max_members && (
                      <span className="badge badge-error badge-sm">Мест нет</span>
                    )}
                  </div>

                  <div className="card-actions justify-end mt-4">
                    <Link
                      to={`/teams/${team.id}`}
                      className="btn btn-sm btn-outline btn-primary"
                    >
                      Подробнее
                    </Link>

                    {team.is_leader && (
                      <span className="badge badge-primary gap-1 py-3">
                        <Crown className="w-3 h-3" />
                        Вы лидер
                      </span>
                    )}

                    {!team.is_leader && team.is_member && (
                      <button
                        className="btn btn-sm btn-outline btn-error gap-1"
                        onClick={() => handleLeaveTeam(team.id)}
                        disabled={isActing}
                      >
                        {isActing ? (
                          <span className="loading loading-spinner loading-xs" />
                        ) : (
                          <LogOut className="w-4 h-4" />
                        )}
                        Покинуть
                      </button>
                    )}

                    {!team.is_leader && !team.is_member && (
                      <button
                        className="btn btn-sm btn-primary gap-1"
                        onClick={() => handleJoinTeam(team.id)}
                        disabled={isActing}
                      >
                        {isActing ? (
                          <span className="loading loading-spinner loading-xs" />
                        ) : (
                          <UserPlus className="w-4 h-4" />
                        )}
                        Присоединиться
                      </button>
                    )}
                  </div>
                </div>
              </div>
            );
          })}
        </div>
      )}

      {/* Empty State */}
      {!loading && !error && teams.length === 0 && (
        <div className="card bg-base-100 shadow-lg">
          <div className="card-body text-center py-12">
            <HeartHandshake className="w-16 h-16 mx-auto text-gray-400 mb-4" />
            <h3 className="text-lg font-semibold mb-2">Заявок пока нет</h3>
            <p className="text-gray-600 mb-4">
              Станьте первым -- создайте заявку и начните собирать команду!
            </p>
            <button
              className="btn btn-primary gap-2 mx-auto"
              onClick={openCreateModal}
            >
              <Plus className="w-5 h-5" />
              Создать заявку
            </button>
          </div>
        </div>
      )}

      {/* Create Team Modal */}
      {showCreateModal && (
        <dialog className="modal modal-open">
          <div className="modal-box">
            <h3 className="font-bold text-lg mb-4">Создать заявку на совместное участие</h3>
            <form onSubmit={handleCreateTeam}>
              <div className="form-control mb-4">
                <label className="label">
                  <span className="label-text">Название</span>
                </label>
                <input
                  type="text"
                  className="input input-bordered"
                  placeholder="Например: Команда для хакатона Digital Bridge"
                  value={newTeam.name}
                  onChange={(e) => setNewTeam({ ...newTeam, name: e.target.value })}
                  required
                  maxLength={200}
                />
              </div>
              <div className="form-control mb-4">
                <label className="label">
                  <span className="label-text">Привязать к возможности</span>
                  <span className="label-text-alt text-gray-400">необязательно</span>
                </label>
                {listingsLoading ? (
                  <div className="flex items-center gap-2 py-2">
                    <span className="loading loading-spinner loading-sm" />
                    <span className="text-sm text-gray-500">Загрузка возможностей...</span>
                  </div>
                ) : listings.length > 0 ? (
                  <select
                    className="select select-bordered w-full"
                    value={newTeam.listing}
                    onChange={(e) => setNewTeam({ ...newTeam, listing: e.target.value })}
                  >
                    <option value="">-- Без привязки --</option>
                    {listings.map((l) => (
                      <option key={l.id} value={l.id}>
                        {l.title}{l.listing_type_display ? ` (${l.listing_type_display})` : ''}
                      </option>
                    ))}
                  </select>
                ) : (
                  <input
                    type="text"
                    className="input input-bordered"
                    placeholder="ID возможности (UUID) или оставьте пустым"
                    value={newTeam.listing}
                    onChange={(e) => setNewTeam({ ...newTeam, listing: e.target.value })}
                  />
                )}
              </div>
              <div className="form-control mb-4">
                <label className="label">
                  <span className="label-text">Описание</span>
                </label>
                <textarea
                  className="textarea textarea-bordered h-24"
                  placeholder="Расскажите, чем будет заниматься команда..."
                  value={newTeam.description}
                  onChange={(e) => setNewTeam({ ...newTeam, description: e.target.value })}
                  required
                />
              </div>
              <div className="form-control mb-4">
                <label className="label">
                  <span className="label-text">Какие навыки нужны?</span>
                  <span className="label-text-alt text-gray-400">необязательно</span>
                </label>
                <textarea
                  className="textarea textarea-bordered h-20"
                  placeholder="Например: Python, дизайн, управление проектами..."
                  value={newTeam.requirements}
                  onChange={(e) => setNewTeam({ ...newTeam, requirements: e.target.value })}
                />
              </div>
              <div className="form-control mb-6">
                <label className="label">
                  <span className="label-text">Макс. количество участников</span>
                  <span className="label-text-alt text-gray-400">необязательно</span>
                </label>
                <input
                  type="number"
                  className="input input-bordered"
                  placeholder="Без ограничений"
                  min={2}
                  value={newTeam.max_members}
                  onChange={(e) => setNewTeam({ ...newTeam, max_members: e.target.value })}
                />
              </div>
              <div className="modal-action">
                <button
                  type="button"
                  className="btn btn-ghost"
                  onClick={() => {
                    setShowCreateModal(false);
                    setNewTeam({ name: '', description: '', requirements: '', max_members: '', listing: '' });
                  }}
                >
                  Отмена
                </button>
                <button
                  type="submit"
                  className="btn btn-primary gap-2"
                  disabled={creating || !newTeam.name || !newTeam.description}
                >
                  {creating ? (
                    <span className="loading loading-spinner loading-sm" />
                  ) : (
                    <Plus className="w-5 h-5" />
                  )}
                  Создать
                </button>
              </div>
            </form>
          </div>
          <form method="dialog" className="modal-backdrop">
            <button onClick={() => setShowCreateModal(false)}>close</button>
          </form>
        </dialog>
      )}
    </div>
  );
};

export default Teams;
