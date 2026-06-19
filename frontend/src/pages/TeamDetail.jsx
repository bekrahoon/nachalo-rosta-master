import { useState, useEffect, useCallback } from 'react';
import { useParams, Link, useNavigate } from 'react-router-dom';
import {
  Users, Crown, Clock, ArrowLeft, UserPlus, LogOut,
  Shield, Trash2, Edit3, Check, X,
} from 'lucide-react';
import apiClient from '../api/client';
import { useAuth } from '../hooks/useAuth';

export const TeamDetail = () => {
  const { id } = useParams();
  const navigate = useNavigate();
  const { user } = useAuth();
  const [team, setTeam] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [actionLoading, setActionLoading] = useState(false);
  const [editing, setEditing] = useState(false);
  const [editData, setEditData] = useState({ name: '', description: '', requirements: '', max_members: '' });
  const [showDeleteConfirm, setShowDeleteConfirm] = useState(false);

  const fetchTeam = useCallback(() => {
    return apiClient.get(`/teams/${id}/`).then((res) => {
      setTeam(res.data);
      setEditData({
        name: res.data.name,
        description: res.data.description,
        requirements: res.data.requirements || '',
        max_members: res.data.max_members ?? '',
      });
      return res.data;
    });
  }, [id]);

  useEffect(() => {
    setLoading(true);
    fetchTeam()
      .catch(() => setError('Команда не найдена'))
      .finally(() => setLoading(false));
  }, [fetchTeam]);

  const isLeader = user && team?.leader?.id === user.id;
  const isMember = user && team?.members?.some((m) => m.user?.id === user.id);

  const handleJoin = async () => {
    setActionLoading(true);
    try {
      await apiClient.post(`/teams/${id}/join/`);
      await fetchTeam();
    } catch (err) {
      setError(err.response?.data?.detail || 'Не удалось присоединиться');
    } finally {
      setActionLoading(false);
    }
  };

  const handleLeave = async () => {
    setActionLoading(true);
    try {
      await apiClient.post(`/teams/${id}/leave/`);
      await fetchTeam();
    } catch (err) {
      setError(err.response?.data?.detail || 'Не удалось покинуть команду');
    } finally {
      setActionLoading(false);
    }
  };

  const handleUpdate = async (e) => {
    e.preventDefault();
    setActionLoading(true);
    const payload = {
      name: editData.name,
      description: editData.description,
      requirements: editData.requirements,
      max_members: editData.max_members ? parseInt(editData.max_members, 10) : null,
    };
    try {
      await apiClient.patch(`/teams/${id}/`, payload);
      await fetchTeam();
      setEditing(false);
    } catch (err) {
      setError(err.response?.data?.detail || 'Не удалось обновить');
    } finally {
      setActionLoading(false);
    }
  };

  const handleDelete = async () => {
    setActionLoading(true);
    try {
      await apiClient.delete(`/teams/${id}/`);
      navigate('/teams');
    } catch (err) {
      setError(err.response?.data?.detail || 'Не удалось удалить команду');
      setActionLoading(false);
    }
  };

  const getRoleBadge = (role) => {
    if (role === 'leader')
      return (
        <span className="badge badge-warning badge-sm gap-1">
          <Crown className="w-3 h-3" /> Лидер
        </span>
      );
    if (role === 'moderator')
      return (
        <span className="badge badge-info badge-sm gap-1">
          <Shield className="w-3 h-3" /> Модератор
        </span>
      );
    return <span className="badge badge-ghost badge-sm">Участник</span>;
  };

  if (loading) {
    return (
      <div className="flex justify-center py-20">
        <span className="loading loading-spinner loading-lg text-primary" />
      </div>
    );
  }

  if (error && !team) {
    return (
      <div className="text-center py-20">
        <h2 className="text-2xl font-bold mb-4">{error}</h2>
        <Link to="/teams" className="btn btn-primary">
          Вернуться к командам
        </Link>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <Link to="/teams" className="btn btn-ghost btn-sm gap-2">
        <ArrowLeft className="w-4 h-4" />
        Все команды
      </Link>

      {error && (
        <div className="alert alert-error">
          <span>{error}</span>
          <button className="btn btn-sm btn-ghost" onClick={() => setError(null)}>
            x
          </button>
        </div>
      )}

      {/* Team Header */}
      <div className="card bg-base-100 shadow-lg">
        <div className="card-body">
          {editing ? (
            <form onSubmit={handleUpdate} className="space-y-4">
              <div className="form-control">
                <label className="label">
                  <span className="label-text">Название</span>
                </label>
                <input
                  type="text"
                  className="input input-bordered"
                  value={editData.name}
                  onChange={(e) => setEditData({ ...editData, name: e.target.value })}
                  required
                />
              </div>
              <div className="form-control">
                <label className="label">
                  <span className="label-text">Описание</span>
                </label>
                <textarea
                  className="textarea textarea-bordered h-24"
                  value={editData.description}
                  onChange={(e) => setEditData({ ...editData, description: e.target.value })}
                  required
                />
              </div>
              <div className="form-control">
                <label className="label">
                  <span className="label-text">Требования к участникам</span>
                </label>
                <textarea
                  className="textarea textarea-bordered h-20"
                  placeholder="Например: знание английского, опыт в дизайне..."
                  value={editData.requirements}
                  onChange={(e) => setEditData({ ...editData, requirements: e.target.value })}
                />
              </div>
              <div className="form-control">
                <label className="label">
                  <span className="label-text">Макс. количество участников</span>
                </label>
                <input
                  type="number"
                  className="input input-bordered"
                  placeholder="Без ограничений"
                  min={2}
                  value={editData.max_members}
                  onChange={(e) => setEditData({ ...editData, max_members: e.target.value })}
                />
              </div>
              <div className="flex gap-2">
                <button type="submit" className="btn btn-primary btn-sm gap-1" disabled={actionLoading}>
                  {actionLoading ? <span className="loading loading-spinner loading-xs" /> : <Check className="w-4 h-4" />}
                  Сохранить
                </button>
                <button
                  type="button"
                  className="btn btn-ghost btn-sm gap-1"
                  onClick={() => {
                    setEditing(false);
                    setEditData({
                      name: team.name,
                      description: team.description,
                      requirements: team.requirements || '',
                      max_members: team.max_members ?? '',
                    });
                  }}
                >
                  <X className="w-4 h-4" /> Отмена
                </button>
              </div>
            </form>
          ) : (
            <>
              <div className="flex items-start justify-between flex-wrap gap-4">
                <div className="flex items-center gap-4">
                  {team.avatar ? (
                    <img src={team.avatar} alt={team.name} className="w-16 h-16 rounded-full object-cover" />
                  ) : (
                    <div className="w-16 h-16 rounded-full bg-primary/20 flex items-center justify-center">
                      <Users className="w-8 h-8 text-primary" />
                    </div>
                  )}
                  <div>
                    <h1 className="text-3xl font-bold">{team.name}</h1>
                    <div className="flex items-center gap-2 mt-1 text-gray-500">
                      <Crown className="w-4 h-4 text-warning" />
                      <span>{team.leader?.full_name || team.leader?.email}</span>
                      <span className={`badge badge-sm ${team.status === 'active' ? 'badge-success' : 'badge-ghost'}`}>
                        {team.status_display}
                      </span>
                    </div>
                  </div>
                </div>

                <div className="flex gap-2 flex-wrap">
                  {isLeader && (
                    <>
                      <button className="btn btn-sm btn-outline gap-1" onClick={() => setEditing(true)}>
                        <Edit3 className="w-4 h-4" /> Редактировать
                      </button>
                      <button className="btn btn-sm btn-outline btn-error gap-1" onClick={() => setShowDeleteConfirm(true)}>
                        <Trash2 className="w-4 h-4" /> Удалить
                      </button>
                    </>
                  )}
                  {!isLeader && !isMember && (() => {
                    const isFull = team.max_members && (team.members?.length || 0) >= team.max_members;
                    return (
                      <button className="btn btn-sm btn-primary gap-1" onClick={handleJoin} disabled={actionLoading || isFull}>
                        {actionLoading ? <span className="loading loading-spinner loading-xs" /> : <UserPlus className="w-4 h-4" />}
                        {isFull ? 'Мест нет' : 'Вступить в команду'}
                      </button>
                    );
                  })()}
                  {!isLeader && isMember && (
                    <button className="btn btn-sm btn-outline btn-error gap-1" onClick={handleLeave} disabled={actionLoading}>
                      {actionLoading ? <span className="loading loading-spinner loading-xs" /> : <LogOut className="w-4 h-4" />}
                      Покинуть
                    </button>
                  )}
                </div>
              </div>

              <p className="text-gray-700 mt-4 whitespace-pre-line">{team.description}</p>

              {team.requirements && (
                <div className="mt-4 bg-base-200 rounded-lg p-4">
                  <h3 className="font-semibold text-sm mb-1">Требования к участникам</h3>
                  <p className="text-gray-600 text-sm whitespace-pre-line">{team.requirements}</p>
                </div>
              )}

              <div className="flex items-center gap-6 mt-4 text-sm text-gray-500 flex-wrap">
                <div className="flex items-center gap-1">
                  <Users className="w-4 h-4" />
                  <span>
                    {team.members?.length || 0}{team.max_members ? ` / ${team.max_members}` : ''} участников
                  </span>
                </div>
                {team.max_members && (team.members?.length || 0) >= team.max_members && (
                  <span className="badge badge-error badge-sm">Набор закрыт</span>
                )}
                <div className="flex items-center gap-1">
                  <Clock className="w-4 h-4" />
                  <span>{Math.round(team.total_hours || 0)} часов волонтёрства</span>
                </div>
                <div className="text-xs">
                  Создана: {new Date(team.created_at).toLocaleDateString('ru-RU')}
                </div>
              </div>
            </>
          )}
        </div>
      </div>

      {/* Members */}
      <div className="card bg-base-100 shadow-lg">
        <div className="card-body">
          <h2 className="card-title text-xl mb-4">
            <Users className="w-5 h-5" />
            Участники ({team.members?.length || 0})
          </h2>

          {team.members && team.members.length > 0 ? (
            <div className="space-y-3">
              {team.members.map((member) => (
                <div key={member.id} className="flex items-center justify-between p-3 rounded-lg bg-base-200">
                  <div className="flex items-center gap-3">
                    {member.user?.avatar ? (
                      <img src={member.user.avatar} alt="" className="w-10 h-10 rounded-full object-cover" />
                    ) : (
                      <div className="w-10 h-10 rounded-full bg-primary/20 flex items-center justify-center font-bold text-primary">
                        {(member.user?.full_name || member.user?.email || '?').charAt(0).toUpperCase()}
                      </div>
                    )}
                    <div>
                      <div className="font-medium">
                        {member.user?.full_name || member.user?.email}
                      </div>
                      <div className="text-xs text-gray-500">
                        {new Date(member.joined_at).toLocaleDateString('ru-RU')}
                      </div>
                    </div>
                  </div>
                  {getRoleBadge(member.role)}
                </div>
              ))}
            </div>
          ) : (
            <p className="text-gray-500 text-center py-4">В команде пока нет участников</p>
          )}
        </div>
      </div>

      {/* Delete Confirmation */}
      {showDeleteConfirm && (
        <dialog className="modal modal-open">
          <div className="modal-box">
            <h3 className="font-bold text-lg">Удалить команду?</h3>
            <p className="py-4">
              Вы уверены, что хотите удалить команду &laquo;{team.name}&raquo;? Это действие нельзя отменить.
            </p>
            <div className="modal-action">
              <button className="btn btn-ghost" onClick={() => setShowDeleteConfirm(false)}>Отмена</button>
              <button className="btn btn-error gap-1" onClick={handleDelete} disabled={actionLoading}>
                {actionLoading ? <span className="loading loading-spinner loading-sm" /> : <Trash2 className="w-4 h-4" />}
                Удалить
              </button>
            </div>
          </div>
          <form method="dialog" className="modal-backdrop">
            <button onClick={() => setShowDeleteConfirm(false)}>close</button>
          </form>
        </dialog>
      )}
    </div>
  );
};

export default TeamDetail;
