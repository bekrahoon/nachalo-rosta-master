import { useState } from 'react';
import { MapPin, Calendar, Users, Search, Filter } from 'lucide-react';

export const Events = () => {
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedCategory, setSelectedCategory] = useState('all');
  const [selectedLocation, setSelectedLocation] = useState('all');

  // Placeholder events
  const events = [
    {
      id: 1,
      title: 'Очистка парка',
      category: 'environment',
      location: 'Бишкек',
      date: '2024-01-20',
      volunteers: 12,
      maxVolunteers: 20,
      description: 'Помогите очистить парк от мусора',
      image: '🌳',
    },
    {
      id: 2,
      title: 'Обучение детей программированию',
      category: 'education',
      location: 'Бишкек',
      date: '2024-01-25',
      volunteers: 5,
      maxVolunteers: 10,
      description: 'Преподавайте основы программирования детям',
      image: '💻',
    },
    {
      id: 3,
      title: 'Посещение дома престарелых',
      category: 'social',
      location: 'Токмок',
      date: '2024-01-22',
      volunteers: 8,
      maxVolunteers: 15,
      description: 'Проведите время с пожилыми людьми',
      image: '❤️',
    },
  ];

  const categories = [
    { value: 'all', label: '📋 Все категории' },
    { value: 'environment', label: '🌳 Окружающая среда' },
    { value: 'education', label: '📚 Образование' },
    { value: 'social', label: '❤️ Социальная помощь' },
    { value: 'health', label: '🏥 Здравоохранение' },
  ];

  const locations = [
    { value: 'all', label: 'Все города' },
    { value: 'bishkek', label: 'Бишкек' },
    { value: 'tokmok', label: 'Токмок' },
    { value: 'osh', label: 'Ош' },
  ];

  const filteredEvents = events.filter((event) => {
    const matchesSearch = event.title.toLowerCase().includes(searchQuery.toLowerCase());
    const matchesCategory = selectedCategory === 'all' || event.category === selectedCategory;
    const matchesLocation = selectedLocation === 'all' || event.location.toLowerCase() === selectedLocation;
    return matchesSearch && matchesCategory && matchesLocation;
  });

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="hero bg-gradient-to-r from-primary to-accent rounded-lg">
        <div className="hero-content text-white text-center">
          <div>
            <h1 className="text-4xl font-bold mb-4">📅 События & Возможности</h1>
            <p className="text-lg">Найдите волонтёрские возможности, которые вас интересуют</p>
          </div>
        </div>
      </div>

      {/* Search & Filters */}
      <div className="card bg-base-100 shadow-lg">
        <div className="card-body space-y-4">
          {/* Search */}
          <div className="form-control">
            <div className="input-group">
              <input
                type="text"
                placeholder="Искать события..."
                className="input input-bordered w-full"
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
              />
              <button className="btn btn-primary">
                <Search className="w-5 h-5" />
              </button>
            </div>
          </div>

          {/* Filters */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div className="form-control">
              <label className="label">
                <span className="label-text">Категория</span>
              </label>
              <select
                className="select select-bordered"
                value={selectedCategory}
                onChange={(e) => setSelectedCategory(e.target.value)}
              >
                {categories.map((cat) => (
                  <option key={cat.value} value={cat.value}>
                    {cat.label}
                  </option>
                ))}
              </select>
            </div>

            <div className="form-control">
              <label className="label">
                <span className="label-text">Город</span>
              </label>
              <select
                className="select select-bordered"
                value={selectedLocation}
                onChange={(e) => setSelectedLocation(e.target.value)}
              >
                {locations.map((loc) => (
                  <option key={loc.value} value={loc.value}>
                    {loc.label}
                  </option>
                ))}
              </select>
            </div>
          </div>
        </div>
      </div>

      {/* Results Count */}
      <div className="text-sm text-gray-600">
        Найдено событий: <span className="font-bold">{filteredEvents.length}</span>
      </div>

      {/* Events Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {filteredEvents.map((event) => (
          <div key={event.id} className="card bg-base-100 shadow-lg hover:shadow-xl transition">
            {/* Image */}
            <div className="bg-gradient-to-r from-primary/20 to-accent/20 h-32 flex items-center justify-center text-6xl">
              {event.image}
            </div>

            {/* Content */}
            <div className="card-body">
              <h2 className="card-title text-lg">{event.title}</h2>
              <p className="text-gray-600 text-sm">{event.description}</p>

              {/* Details */}
              <div className="space-y-2 my-4">
                <div className="flex items-center gap-2 text-sm">
                  <Calendar className="w-4 h-4 text-primary" />
                  <span>{new Date(event.date).toLocaleDateString('ru-RU')}</span>
                </div>
                <div className="flex items-center gap-2 text-sm">
                  <MapPin className="w-4 h-4 text-primary" />
                  <span>{event.location}</span>
                </div>
                <div className="flex items-center gap-2 text-sm">
                  <Users className="w-4 h-4 text-primary" />
                  <span>
                    {event.volunteers}/{event.maxVolunteers} волонтёров
                  </span>
                </div>
              </div>

              {/* Progress Bar */}
              <progress
                className="progress progress-primary w-full"
                value={event.volunteers}
                max={event.maxVolunteers}
              />

              {/* CTA */}
              <div className="card-actions justify-end pt-4">
                <button className="btn btn-primary btn-sm">
                  Присоединиться
                </button>
              </div>
            </div>
          </div>
        ))}
      </div>

      {/* Empty State */}
      {filteredEvents.length === 0 && (
        <div className="card bg-base-100 shadow-lg">
          <div className="card-body text-center py-12">
            <Filter className="w-16 h-16 mx-auto text-gray-400 mb-4" />
            <h3 className="text-lg font-semibold mb-2">Событий не найдено</h3>
            <p className="text-gray-600">
              Попробуйте изменить фильтры или поисковый запрос
            </p>
          </div>
        </div>
      )}

      {/* CTA Section */}
      <div className="card bg-gradient-to-r from-primary/10 to-accent/10">
        <div className="card-body text-center">
          <h3 className="card-title justify-center mb-4">Хотите создать своё событие?</h3>
          <p className="text-gray-600 mb-4">
            Если вы организатор, вы можете создать своё волонтёрское событие
          </p>
          <button className="btn btn-primary">Создать событие</button>
        </div>
      </div>
    </div>
  );
};

export default Events;
