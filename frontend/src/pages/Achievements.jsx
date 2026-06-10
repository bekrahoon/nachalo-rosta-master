import { Trophy, Star, Badge, Lock } from 'lucide-react';

export const Achievements = () => {
  const achievements = [
    {
      id: 1,
      name: 'Первый волонтёр',
      description: 'Завершите первое волонтёрское событие',
      icon: '🌟',
      unlocked: true,
      progress: 1,
      total: 1,
    },
    {
      id: 2,
      name: 'Волонтёр месяца',
      description: 'Накопите 20 часов волонтёрства в месяц',
      icon: '⭐',
      unlocked: false,
      progress: 8,
      total: 20,
    },
    {
      id: 3,
      name: 'Командный игрок',
      description: 'Присоединитесь к 3 командам',
      icon: '👥',
      unlocked: true,
      progress: 3,
      total: 3,
    },
    {
      id: 4,
      name: 'Помощник окружающей среды',
      description: 'Завершите 5 событий по очистке окружающей среды',
      icon: '🌳',
      unlocked: false,
      progress: 2,
      total: 5,
    },
    {
      id: 5,
      name: 'Образователь',
      description: 'Помогите 10 человекам с образованием',
      icon: '📚',
      unlocked: false,
      progress: 0,
      total: 10,
    },
    {
      id: 6,
      name: 'Легенда волонтёра',
      description: 'Накопите 100 часов волонтёрства',
      icon: '🏆',
      unlocked: false,
      progress: 8,
      total: 100,
    },
  ];

  const unlockedCount = achievements.filter((a) => a.unlocked).length;
  const totalPoints = unlockedCount * 10;

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="hero bg-gradient-to-r from-yellow-400 to-orange-400 rounded-lg">
        <div className="hero-content text-white text-center">
          <div>
            <h1 className="text-4xl font-bold mb-4">🏆 Достижения</h1>
            <p className="text-lg">Получайте награды за волонтёрскую деятельность</p>
          </div>
        </div>
      </div>

      {/* Stats */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <div className="stat bg-base-100 shadow rounded-lg">
          <div className="stat-figure text-primary">
            <Trophy className="w-8 h-8" />
          </div>
          <div className="stat-title">Разблокировано достижений</div>
          <div className="stat-value text-primary">{unlockedCount}</div>
          <div className="stat-desc">из {achievements.length}</div>
        </div>

        <div className="stat bg-base-100 shadow rounded-lg">
          <div className="stat-figure text-warning">
            <Star className="w-8 h-8" />
          </div>
          <div className="stat-title">Общие очки</div>
          <div className="stat-value text-warning">{totalPoints}</div>
          <div className="stat-desc">бонусные точки</div>
        </div>

        <div className="stat bg-base-100 shadow rounded-lg">
          <div className="stat-figure text-success">
            <Badge className="w-8 h-8" />
          </div>
          <div className="stat-title">Уровень волонтёра</div>
          <div className="stat-value text-success">Бронза</div>
          <div className="stat-desc">новичок → серебро</div>
        </div>
      </div>

      {/* Achievements Grid */}
      <div>
        <h2 className="text-2xl font-bold mb-4">Все достижения</h2>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {achievements.map((achievement) => (
            <div
              key={achievement.id}
              className={`card shadow-lg transition ${
                achievement.unlocked
                  ? 'bg-base-100 border-2 border-warning'
                  : 'bg-base-200 opacity-75'
              }`}
            >
              <div className="card-body">
                {/* Icon & Lock */}
                <div className="flex justify-between items-start mb-4">
                  <div className="text-5xl">{achievement.icon}</div>
                  {!achievement.unlocked && (
                    <Lock className="w-5 h-5 text-gray-400" />
                  )}
                  {achievement.unlocked && (
                    <Trophy className="w-5 h-5 text-warning" />
                  )}
                </div>

                {/* Title & Description */}
                <h3 className="card-title text-lg">{achievement.name}</h3>
                <p className="text-sm text-gray-600 mb-4">
                  {achievement.description}
                </p>

                {/* Progress */}
                <div className="space-y-2">
                  <div className="flex justify-between text-xs">
                    <span>Прогресс</span>
                    <span>
                      {achievement.progress}/{achievement.total}
                    </span>
                  </div>
                  <progress
                    className={`progress w-full ${
                      achievement.unlocked
                        ? 'progress-warning'
                        : 'progress-primary'
                    }`}
                    value={achievement.progress}
                    max={achievement.total}
                  />
                </div>

                {/* Status */}
                <div className="pt-4">
                  {achievement.unlocked ? (
                    <div className="badge badge-warning gap-2 w-full justify-center">
                      ✓ Разблокировано
                    </div>
                  ) : (
                    <div className="badge badge-ghost gap-2 w-full justify-center">
                      Заблокировано
                    </div>
                  )}
                </div>
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Leaderboard */}
      <div className="card bg-base-100 shadow-xl">
        <div className="card-body">
          <h2 className="card-title text-2xl mb-4">🥇 Лучшие волонтёры</h2>

          <div className="overflow-x-auto">
            <table className="table">
              <thead>
                <tr>
                  <th>Место</th>
                  <th>Волонтёр</th>
                  <th>Часы</th>
                  <th>Достижения</th>
                  <th>Уровень</th>
                </tr>
              </thead>
              <tbody>
                <tr>
                  <td>🥇 1</td>
                  <td>Алия Р.</td>
                  <td>156 часов</td>
                  <td>18/20</td>
                  <td>
                    <div className="badge badge-success">Золото</div>
                  </td>
                </tr>
                <tr>
                  <td>🥈 2</td>
                  <td>Булат К.</td>
                  <td>132 часов</td>
                  <td>16/20</td>
                  <td>
                    <div className="badge badge-secondary">Серебро</div>
                  </td>
                </tr>
                <tr>
                  <td>🥉 3</td>
                  <td>Данияр А.</td>
                  <td>108 часов</td>
                  <td>14/20</td>
                  <td>
                    <div className="badge badge-warning">Бронза</div>
                  </td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Achievements;
