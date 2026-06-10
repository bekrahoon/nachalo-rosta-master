import { Sparkles, Heart, AlertCircle, ArrowRight } from 'lucide-react';

export const Recommendations = () => {
  const recommendations = [
    {
      id: 1,
      title: 'Очистка парка в выходные',
      reason: 'Вам нравятся экологические проекты',
      match: 92,
      date: '20 Янв 2024',
      location: 'Бишкек',
      hours: 4,
    },
    {
      id: 2,
      title: 'Обучение программированию детей',
      reason: 'У вас есть навыки программирования',
      match: 88,
      date: '25 Янв 2024',
      location: 'Онлайн',
      hours: 6,
    },
    {
      id: 3,
      title: 'Помощь в библиотеке',
      reason: 'Вы интересуетесь образованием',
      match: 85,
      date: '22 Янв 2024',
      location: 'Бишкек',
      hours: 3,
    },
  ];

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="hero bg-gradient-to-r from-blue-400 to-cyan-400 rounded-lg">
        <div className="hero-content text-white text-center">
          <div>
            <h1 className="text-4xl font-bold mb-4">🤖 AI Рекомендации</h1>
            <p className="text-lg">
              Персонализированные волонтёрские возможности на основе ваших интересов
            </p>
          </div>
        </div>
      </div>

      {/* Info Card */}
      <div className="alert alert-info">
        <AlertCircle className="w-6 h-6" />
        <span>
          Эти рекомендации основаны на вашем профиле, интересах и истории волонтёрства
        </span>
      </div>

      {/* How It Works */}
      <div className="card bg-base-100 shadow-xl">
        <div className="card-body">
          <h2 className="card-title mb-4">⚙️ Как работают рекомендации?</h2>
          <p className="text-gray-600 mb-4">
            Наш AI анализирует:
          </p>
          <ul className="space-y-2 text-sm">
            <li className="flex items-center gap-2">
              <span className="badge badge-primary">1</span>
              Ваши интересы и навыки из профиля
            </li>
            <li className="flex items-center gap-2">
              <span className="badge badge-primary">2</span>
              Историю участия в событиях
            </li>
            <li className="flex items-center gap-2">
              <span className="badge badge-primary">3</span>
              Ваши достижения и специализацию
            </li>
            <li className="flex items-center gap-2">
              <span className="badge badge-primary">4</span>
              Доступное время и предпочтения по локации
            </li>
          </ul>
        </div>
      </div>

      {/* Recommendations List */}
      <div>
        <h2 className="text-2xl font-bold mb-4">
          <Sparkles className="w-6 h-6 inline mr-2" />
          Рекомендуемые события
        </h2>

        <div className="space-y-4">
          {recommendations.map((rec) => (
            <div key={rec.id} className="card bg-base-100 shadow-lg hover:shadow-xl transition">
              <div className="card-body">
                <div className="flex justify-between items-start mb-4">
                  <div className="flex-1">
                    <h3 className="card-title text-lg">{rec.title}</h3>
                    <p className="text-sm text-gray-600 flex items-center gap-1 mt-2">
                      <Heart className="w-4 h-4 text-error" />
                      {rec.reason}
                    </p>
                  </div>

                  {/* Match Score */}
                  <div className="flex flex-col items-center">
                    <div className="radial-progress text-primary" style={{ "--value": rec.match }}>
                      {rec.match}%
                    </div>
                    <span className="text-xs text-gray-600 mt-1">совпадение</span>
                  </div>
                </div>

                {/* Details */}
                <div className="grid grid-cols-2 md:grid-cols-4 gap-4 py-4 border-y border-base-300">
                  <div>
                    <div className="text-xs text-gray-600">Дата</div>
                    <div className="font-semibold text-sm">{rec.date}</div>
                  </div>
                  <div>
                    <div className="text-xs text-gray-600">Локация</div>
                    <div className="font-semibold text-sm">{rec.location}</div>
                  </div>
                  <div>
                    <div className="text-xs text-gray-600">Часы</div>
                    <div className="font-semibold text-sm">{rec.hours} часов</div>
                  </div>
                  <div>
                    <div className="text-xs text-gray-600">Соответствие</div>
                    <div className="font-semibold text-sm text-primary">{rec.match}%</div>
                  </div>
                </div>

                {/* Actions */}
                <div className="card-actions justify-end pt-4">
                  <button className="btn btn-ghost btn-sm">Подробнее</button>
                  <button className="btn btn-primary btn-sm gap-1">
                    Присоединиться
                    <ArrowRight className="w-4 h-4" />
                  </button>
                </div>
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Preferences */}
      <div className="card bg-base-100 shadow-xl">
        <div className="card-body">
          <h2 className="card-title mb-4">⚙️ Предпочтения рекомендаций</h2>

          <div className="space-y-4">
            <div className="form-control">
              <label className="label">
                <span className="label-text">Предпочитаемые категории</span>
              </label>
              <div className="space-y-2">
                {['🌳 Окружающая среда', '📚 Образование', '❤️ Социальная помощь', '🏥 Здравоохранение'].map(
                  (cat) => (
                    <label key={cat} className="label cursor-pointer">
                      <span className="label-text">{cat}</span>
                      <input type="checkbox" className="checkbox" defaultChecked />
                    </label>
                  )
                )}
              </div>
            </div>

            <div className="form-control">
              <label className="label">
                <span className="label-text">Максимум часов в неделю</span>
              </label>
              <input
                type="range"
                min="0"
                max="40"
                defaultValue="20"
                className="range"
              />
              <div className="flex justify-between text-xs px-2 pt-2">
                <span>0 часов</span>
                <span>40 часов</span>
              </div>
            </div>

            <div className="form-control">
              <label className="label">
                <span className="label-text">Предпочитаемая локация</span>
              </label>
              <select className="select select-bordered">
                <option>Бишкек</option>
                <option>Токмок</option>
                <option>Ош</option>
                <option>Онлайн</option>
                <option>Любая</option>
              </select>
            </div>

            <button className="btn btn-primary">Сохранить предпочтения</button>
          </div>
        </div>
      </div>

      {/* CTA */}
      <div className="card bg-gradient-to-r from-blue-400/10 to-cyan-400/10 border-2 border-blue-400">
        <div className="card-body text-center">
          <h3 className="card-title justify-center">🎯 Хотите лучшие рекомендации?</h3>
          <p className="text-gray-600">
            Заполните подробный профиль с вашими интересами и навыками для более точных рекомендаций
          </p>
          <button className="btn btn-primary">Обновить профиль</button>
        </div>
      </div>
    </div>
  );
};

export default Recommendations;
