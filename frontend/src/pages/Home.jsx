import { Link } from 'react-router-dom';
import { useAuth } from '../hooks/useAuth';
import { Sparkles, Users, Target, Zap } from 'lucide-react';

export const Home = () => {
  const { isAuthenticated } = useAuth();

  const benefits = [
    {
      icon: Sparkles,
      title: 'AI-подбор возможностей',
      description: 'Умный алгоритм подберёт стипендии, гранты и стажировки под ваш профиль',
    },
    {
      icon: Users,
      title: 'Совместные заявки',
      description: 'Найдите напарников для хакатонов, конкурсов и проектов из каталога',
    },
    {
      icon: Target,
      title: 'Агрегатор возможностей',
      description: 'Гранты, стажировки, хакатоны и волонтёрство из 30+ источников в одном месте',
    },
    {
      icon: Zap,
      title: 'Центральная Азия и мир',
      description: 'Фокус на Кыргызстане, Казахстане, Узбекистане и международных программах',
    },
  ];

  return (
    <div className="space-y-0">
      {/* Hero Section */}
      <section className="hero min-h-[60vh] md:min-h-[80vh] bg-gradient-to-br from-primary via-accent to-secondary text-white px-4">
        <div className="hero-content text-center">
          <div className="max-w-2xl">
            <h1 className="text-3xl sm:text-4xl md:text-6xl font-bold mb-4 md:mb-6">
              Начало Роста: Влияние
            </h1>
            <p className="text-lg sm:text-xl md:text-2xl mb-6 md:mb-8 leading-relaxed">
              Платформа для молодёжного волонтёрства, социальных инициатив
              и развития в Центральной Азии
            </p>
            <div className="flex gap-4 justify-center flex-wrap">
              {isAuthenticated ? (
                <Link to="/dashboard" className="btn btn-lg btn-white gap-2">
                  Перейти в дашборд
                </Link>
              ) : (
                <>
                  <Link to="/register" className="btn btn-lg btn-white gap-2">
                    Начать волонтёрить
                  </Link>
                  <Link to="/login" className="btn btn-lg btn-outline btn-white">
                    Вход
                  </Link>
                </>
              )}
            </div>
          </div>
        </div>
      </section>

      {/* Benefits Section */}
      <section className="py-12 md:py-20 px-4 bg-base-100">
        <div className="container mx-auto">
          <div className="text-center mb-8 md:mb-16">
            <h2 className="text-2xl md:text-4xl font-bold mb-4">Почему выбирать нас?</h2>
            <p className="text-base md:text-xl text-gray-600">
              Всё что нужно для успешного волонтёрства в одной платформе
            </p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
            {benefits.map((benefit) => {
              const Icon = benefit.icon;
              return (
                <div key={benefit.title} className="card bg-base-200 shadow-lg">
                  <div className="card-body">
                    <div className="flex items-start gap-4">
                      <div className="bg-primary/20 p-3 rounded-lg flex-shrink-0">
                        <Icon className="w-8 h-8 text-primary" />
                      </div>
                      <div>
                        <h3 className="card-title text-xl mb-2">
                          {benefit.title}
                        </h3>
                        <p className="text-gray-600">{benefit.description}</p>
                      </div>
                    </div>
                  </div>
                </div>
              );
            })}
          </div>
        </div>
      </section>

      {/* Features Section */}
      <section className="py-12 md:py-20 px-4 bg-base-200">
        <div className="container mx-auto">
          <div className="text-center mb-8 md:mb-16">
            <h2 className="text-2xl md:text-4xl font-bold mb-4">Ключевые функции</h2>
          </div>

          <div className="space-y-12">
            {/* Feature 1 */}
            <div className="grid grid-cols-1 md:grid-cols-2 gap-8 items-center">
              <div>
                <h3 className="text-xl md:text-3xl font-bold mb-4">
                  AI-Рекомендации
                </h3>
                <p className="text-lg text-gray-700 mb-4">
                  Укажите интересы и навыки в профиле — AI подберёт подходящие
                  гранты, стипендии, хакатоны и стажировки из каталога.
                </p>
                <ul className="space-y-2">
                  <li className="flex items-center gap-2">
                    <span className="badge badge-primary">✓</span>
                    Персональный подбор по профилю
                  </li>
                  <li className="flex items-center gap-2">
                    <span className="badge badge-primary">✓</span>
                    30+ источников из Центральной Азии и мира
                  </li>
                  <li className="flex items-center gap-2">
                    <span className="badge badge-primary">✓</span>
                    Автоматическое обновление каталога
                  </li>
                </ul>
              </div>
              <div className="bg-gradient-to-br from-primary/20 to-accent/20 rounded-lg h-48 md:h-72 flex items-center justify-center">
                <Sparkles className="w-20 h-20 md:w-32 md:h-32 text-primary opacity-50" />
              </div>
            </div>

            {/* Feature 2 */}
            <div className="grid grid-cols-1 md:grid-cols-2 gap-8 items-center">
              <div className="order-2 md:order-1 bg-gradient-to-br from-secondary/20 to-accent/20 rounded-lg h-48 md:h-72 flex items-center justify-center">
                <Users className="w-20 h-20 md:w-32 md:h-32 text-secondary opacity-50" />
              </div>
              <div className="order-1 md:order-2">
                <h3 className="text-xl md:text-3xl font-bold mb-4">
                  Совместные заявки
                </h3>
                <p className="text-lg text-gray-700 mb-4">
                  Найдите напарников и соберите команду для участия
                  в хакатонах, конкурсах и проектах из каталога возможностей.
                </p>
                <ul className="space-y-2">
                  <li className="flex items-center gap-2">
                    <span className="badge badge-secondary">+</span>
                    Привязка к возможностям из каталога
                  </li>
                  <li className="flex items-center gap-2">
                    <span className="badge badge-secondary">+</span>
                    Поиск по нужным навыкам
                  </li>
                  <li className="flex items-center gap-2">
                    <span className="badge badge-secondary">+</span>
                    Быстрое присоединение к команде
                  </li>
                </ul>
              </div>
            </div>

            {/* Feature 3 */}
            <div className="grid grid-cols-1 md:grid-cols-2 gap-8 items-center">
              <div>
                <h3 className="text-xl md:text-3xl font-bold mb-4">
                  Каталог возможностей
                </h3>
                <p className="text-lg text-gray-700 mb-4">
                  Все возможности собраны из реальных источников — Telegram-каналов,
                  сайтов организаций и RSS-фидов. Каждая ссылка ведёт на оригинал.
                </p>
                <ul className="space-y-2">
                  <li className="flex items-center gap-2">
                    <span className="badge badge-accent">✓</span>
                    Гранты, стипендии, стажировки
                  </li>
                  <li className="flex items-center gap-2">
                    <span className="badge badge-accent">✓</span>
                    Хакатоны, конкурсы, форумы
                  </li>
                  <li className="flex items-center gap-2">
                    <span className="badge badge-accent">✓</span>
                    Фильтры по типу, региону и тегам
                  </li>
                </ul>
              </div>
              <div className="bg-gradient-to-br from-accent/20 to-primary/20 rounded-lg h-48 md:h-72 flex items-center justify-center">
                <Target className="w-20 h-20 md:w-32 md:h-32 text-accent opacity-50" />
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* CTA Section */}
      <section className="py-12 md:py-20 px-4 bg-gradient-to-r from-primary to-accent text-white">
        <div className="container mx-auto text-center">
          <h2 className="text-2xl md:text-4xl font-bold mb-6">
            Готовы начать?
          </h2>
          <p className="text-xl mb-8 max-w-2xl mx-auto">
            Зарегистрируйтесь, заполните профиль — и AI подберёт
            лучшие возможности для вашего роста и развития.
          </p>
          {!isAuthenticated && (
            <Link to="/register" className="btn btn-lg btn-white gap-2">
              Начать сейчас
            </Link>
          )}
        </div>
      </section>

      {/* Stats Section */}
      <section className="py-12 md:py-20 px-4 bg-base-100">
        <div className="container mx-auto">
          <div className="grid grid-cols-3 gap-4 md:gap-8 text-center">
            <div>
              <div className="text-3xl md:text-5xl font-bold text-primary mb-2">140+</div>
              <p className="text-sm md:text-xl text-gray-600">Возможностей</p>
            </div>
            <div>
              <div className="text-3xl md:text-5xl font-bold text-secondary mb-2">30+</div>
              <p className="text-sm md:text-xl text-gray-600">Источников</p>
            </div>
            <div>
              <div className="text-3xl md:text-5xl font-bold text-accent mb-2">5+</div>
              <p className="text-sm md:text-xl text-gray-600">Стран ЦА</p>
            </div>
          </div>
        </div>
      </section>
    </div>
  );
};

export default Home;
