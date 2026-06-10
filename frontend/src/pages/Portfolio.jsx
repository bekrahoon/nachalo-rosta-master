import { FileDown, Download, Share2 } from 'lucide-react';

export const Portfolio = () => {
  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="hero bg-gradient-to-r from-purple-400 to-pink-400 rounded-lg">
        <div className="hero-content text-white text-center">
          <div>
            <h1 className="text-4xl font-bold mb-4">📄 Волонтёрское портфолио</h1>
            <p className="text-lg">Экспортируйте ваш опыт в профессиональный формат</p>
          </div>
        </div>
      </div>

      {/* Current Portfolio Preview */}
      <div className="card bg-base-100 shadow-xl">
        <div className="card-body">
          <h2 className="card-title mb-6">📋 Ваше портфолио</h2>

          {/* Stats */}
          <div className="grid grid-cols-3 gap-4 mb-6">
            <div className="stat bg-base-200 rounded-lg p-4">
              <div className="stat-title text-sm">Всего часов</div>
              <div className="stat-value text-2xl">156 ч</div>
            </div>
            <div className="stat bg-base-200 rounded-lg p-4">
              <div className="stat-title text-sm">Событий</div>
              <div className="stat-value text-2xl">24</div>
            </div>
            <div className="stat bg-base-200 rounded-lg p-4">
              <div className="stat-title text-sm">Достижений</div>
              <div className="stat-value text-2xl">18</div>
            </div>
          </div>

          {/* Recent Activities */}
          <h3 className="font-semibold mb-4">Последние события</h3>
          <div className="space-y-3">
            {[
              {
                title: 'Очистка парка',
                date: '15 Янв 2024',
                hours: 4,
                category: '🌳',
              },
              {
                title: 'Обучение детей',
                date: '12 Янв 2024',
                hours: 6,
                category: '📚',
              },
              {
                title: 'Посещение дома престарелых',
                date: '10 Янв 2024',
                hours: 3,
                category: '❤️',
              },
            ].map((activity, index) => (
              <div
                key={index}
                className="flex items-center justify-between p-4 bg-base-200 rounded-lg"
              >
                <div className="flex-1">
                  <div className="flex items-center gap-2 mb-1">
                    <span className="text-2xl">{activity.category}</span>
                    <h4 className="font-semibold">{activity.title}</h4>
                  </div>
                  <p className="text-sm text-gray-600">{activity.date}</p>
                </div>
                <div className="text-right">
                  <div className="font-bold text-primary">{activity.hours}ч</div>
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* Export Options */}
      <div className="card bg-base-100 shadow-xl">
        <div className="card-body">
          <h2 className="card-title mb-6">📥 Экспортировать портфолио</h2>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {/* PDF Export */}
            <div className="card bg-base-200 cursor-pointer hover:shadow-lg transition">
              <div className="card-body">
                <div className="text-4xl mb-2">📄</div>
                <h3 className="card-title text-lg">PDF документ</h3>
                <p className="text-sm text-gray-600 mb-4">
                  Профессиональный PDF файл с вашим портфолио
                </p>
                <button className="btn btn-primary gap-2">
                  <Download className="w-5 h-5" />
                  Скачать PDF
                </button>
              </div>
            </div>

            {/* Word Export */}
            <div className="card bg-base-200 cursor-pointer hover:shadow-lg transition">
              <div className="card-body">
                <div className="text-4xl mb-2">📝</div>
                <h3 className="card-title text-lg">Word документ</h3>
                <p className="text-sm text-gray-600 mb-4">
                  Редактируемый Word файл для дальнейших правок
                </p>
                <button className="btn btn-primary gap-2">
                  <Download className="w-5 h-5" />
                  Скачать DOCX
                </button>
              </div>
            </div>

            {/* LinkedIn Export */}
            <div className="card bg-base-200 cursor-pointer hover:shadow-lg transition">
              <div className="card-body">
                <div className="text-4xl mb-2">🔗</div>
                <h3 className="card-title text-lg">LinkedIn интеграция</h3>
                <p className="text-sm text-gray-600 mb-4">
                  Экспортируйте прямо в профиль LinkedIn
                </p>
                <button className="btn btn-primary gap-2">
                  <Share2 className="w-5 h-5" />
                  Отправить в LinkedIn
                </button>
              </div>
            </div>

            {/* Share Link */}
            <div className="card bg-base-200 cursor-pointer hover:shadow-lg transition">
              <div className="card-body">
                <div className="text-4xl mb-2">🔐</div>
                <h3 className="card-title text-lg">Поделиться ссылкой</h3>
                <p className="text-sm text-gray-600 mb-4">
                  Создайте ссылку для просмотра портфолио
                </p>
                <button className="btn btn-primary gap-2">
                  <Share2 className="w-5 h-5" />
                  Создать ссылку
                </button>
              </div>
            </div>
          </div>
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
                placeholder="Опытный волонтёр"
                className="input input-bordered"
                defaultValue="Мой волонтёрский путь"
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
                defaultValue="Я увлечённый волонтёр с опытом в экологических и образовательных проектах."
              />
            </div>

            <div className="form-control">
              <label className="label cursor-pointer">
                <span className="label-text">Показывать личные данные</span>
                <input type="checkbox" className="checkbox" defaultChecked />
              </label>
            </div>

            <button className="btn btn-primary">Сохранить изменения</button>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Portfolio;
