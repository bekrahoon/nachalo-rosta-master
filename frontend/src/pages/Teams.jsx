import { useState, useEffect, useCallback, useRef } from 'react';
import { Link } from 'react-router-dom';
import { Users, Plus, Search, Crown, Clock, UserPlus, LogOut } from 'lucide-react';
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
  const [newTeam, setNewTeam] = useState({ name: '', description: '', requirements: '', max_members: '' });
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
        setError('Не удалось загрузить команды. Попробуйте позже.');
        setTeams([]);
      })
      .finally(() => setLoading(false));
  }, [debouncedQuery]);

  useEffect(() => {
    loadTeams();
  }, [loadTeams]);

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
    try {
      await apiClient.post('/teams/', payload);
      setShowCreateModal(false);
      setNewTeam({ name: '', description: '', requirements: '', max_members: '' });
      loadTeams();
    } catch (err) {
      setError(err.response?.data?.detail || 'Не удалось создать команду');
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

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="hero bg-gradient-to-r from-secondary to-primary rounded-lg">
        <div className="hero-content text-white text-center">
          <div>
            <h1 className="text-4xl font-bold mb-4">
              <Users className="inline w-10 h-10 mr-2 mb-1" />
              Команды
            </h1>
            <p className="text-lg">
              Найдите единомышленников или создайте свою команду для волонтёрских проектов
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
                placeholder="Искать команды..."
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
              onClick={() => setShowCreateModal(true)}
            >
              <Plus className="w-5 h-5" />
              Создать команду
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
                      {team.avatar ? (
                        <img
                          src={team.avatar}
                          alt={team.name}
                          className="w-12 h-12 rounded-full object-cover"
                        />
                      ) : (
                        <div className="w-12 h-12 rounded-full bg-primary/20 flex items-center justify-center">
                          <Users className="w-6 h-6 text-primary" />
                        </div>
                      )}
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

                  <p className="text-gray-600 text-sm mt-2 line-clamp-2">
                    {team.description}
                  </p>

                  <div className="flex items-center gap-4 mt-3 text-sm text-gray-500 flex-wrap">
                    <div className="flex items-center gap-1">
                      <Users className="w-4 h-4" />
                      <span>
                        {team.members_count}{team.max_members ? ` / ${team.max_members}` : ''} участников
                      </span>
                    </div>
                    <div className="flex items-center gap-1">
                      <Clock className="w-4 h-4" />
                      <span>{Math.round(team.total_hours || 0)} ч</span>
                    </div>
                    {team.max_members && team.members_count >= team.max_members && (
                      <span className="badge badge-error badge-sm">Мест нет</span>
                    )}
                  </div>

                  {team.requirements && (
                    <div className="mt-2 text-xs text-gray-500 bg-base-200 rounded-lg px-3 py-2">
                      <span className="font-semibold">Требования:</span> {team.requirements}
                    </div>
                  )}

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
                        Вступить
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
            <Users className="w-16 h-16 mx-auto text-gray-400 mb-4" />
            <h3 className="text-lg font-semibold mb-2">Команд пока нет</h3>
            <p className="text-gray-600 mb-4">
              Станьте первым — создайте команду и начните собирать единомышленников!
            </p>
            <button
              className="btn btn-primary gap-2 mx-auto"
              onClick={() => setShowCreateModal(true)}
            >
              <Plus className="w-5 h-5" />
              Создать команду
            </button>
          </div>
        </div>
      )}

      {/* Create Team Modal */}
      {showCreateModal && (
        <dialog className="modal modal-open">
          <div className="modal-box">
            <h3 className="font-bold text-lg mb-4">Создать команду</h3>
            <form onSubmit={handleCreateTeam}>
              <div className="form-control mb-4">
                <label className="label">
                  <span className="label-text">Название команды</span>
                </label>
                <input
                  type="text"
                  className="input input-bordered"
                  placeholder="Например: Зелёный город"
                  value={newTeam.name}
                  onChange={(e) => setNewTeam({ ...newTeam, name: e.target.value })}
                  required
                  maxLength={200}
                />
              </div>
              <div className="form-control mb-4">
                <label className="label">
                  <span className="label-text">Описание</span>
                </label>
                <textarea
                  className="textarea textarea-bordered h-24"
                  placeholder="Расскажите о целях и деятельности команды..."
                  value={newTeam.description}
                  onChange={(e) => setNewTeam({ ...newTeam, description: e.target.value })}
                  required
                />
              </div>
              <div className="form-control mb-4">
                <label className="label">
                  <span className="label-text">Требования к участникам</span>
                  <span className="label-text-alt text-gray-400">необязательно</span>
                </label>
                <textarea
                  className="textarea textarea-bordered h-20"
                  placeholder="Например: знание английского, опыт в дизайне, возраст 16+..."
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
                    setNewTeam({ name: '', description: '', requirements: '', max_members: '' });
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
