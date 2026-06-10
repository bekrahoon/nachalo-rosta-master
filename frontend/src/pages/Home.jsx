import { Link } from 'react-router-dom';
import { useAuth } from '../hooks/useAuth';
import { Sparkles, Users, Target, Zap } from 'lucide-react';

export const Home = () => {
  const { isAuthenticated } = useAuth();

  const benefits = [
    {
      icon: Sparkles,
      title: 'Персонализированные возможности',
      description: 'AI подберёт идеальные проекты по вашим интересам',
    },
    {
      icon: Users,
      title: 'Сообщество волонтёров',
      description: 'Найдите команду, разделяющую ваши ценности',
    },
    {
      icon: Target,
      title: 'Прозрачное влияние',
      description: 'Видите точное влияние вашей деятельности',
    },
    {
      icon: Zap,
      title: 'Быстрый старт',
      description: 'Начните волонтёрить за 5 минут',
    },
  ];

  return (
    <div className="space-y-0">
      {/* Hero Section */}
      <section className="hero min-h-[80vh] bg-gradient-to-br from-primary via-accent to-secondary text-white">
        <div className="hero-content text-center">
          <div className="max-w-2xl">
            <h1 className="text-6xl font-bold mb-6">
              🚀 Начало Роста: Влияние
            </h1>
            <p className="text-2xl mb-8 leading-relaxed">
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
      <section className="py-20 px-4 bg-base-100">
        <div className="container mx-auto">
          <div className="text-center mb-16">
            <h2 className="text-4xl font-bold mb-4">Почему выбирать нас?</h2>
            <p className="text-xl text-gray-600">
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
      <section className="py-20 px-4 bg-base-200">
        <div className="container mx-auto">
          <div className="text-center mb-16">
            <h2 className="text-4xl font-bold mb-4">Ключевые функции</h2>
          </div>

          <div className="space-y-12">
            {/* Feature 1 */}
            <div className="grid grid-cols-1 md:grid-cols-2 gap-8 items-center">
              <div>
                <h3 className="text-3xl font-bold mb-4">
                  🤖 AI-Рекомендации
                </h3>
                <p className="text-lg text-gray-700 mb-4">
                  Наша интеллектуальная система подбирает волонтёрские возможности,
                  которые идеально соответствуют вашим интересам, навыкам и доступному времени.
                </p>
                <ul className="space-y-2">
                  <li className="flex items-center gap-2">
                    <span className="badge badge-primary">✓</span>
                    Персонализированные рекомендации
                  </li>
                  <li className="flex items-center gap-2">
                    <span className="badge badge-primary">✓</span>
                    Постоянное улучшение алгоритма
                  </li>
                  <li className="flex items-center gap-2">
                    <span className="badge badge-primary">✓</span>
                    Расширение возможностей
                  </li>
                </ul>
              </div>
              <div className="bg-gradient-to-br from-primary/20 to-accent/20 rounded-lg h-72 flex items-center justify-center">
                <Sparkles className="w-32 h-32 text-primary opacity-50" />
              </div>
            </div>

            {/* Feature 2 */}
            <div className="grid grid-cols-1 md:grid-cols-2 gap-8 items-center">
              <div className="order-2 md:order-1 bg-gradient-to-br from-secondary/20 to-accent/20 rounded-lg h-72 flex items-center justify-center">
                <Users className="w-32 h-32 text-secondary opacity-50" />
              </div>
              <div className="order-1 md:order-2">
                <h3 className="text-3xl font-bold mb-4">
                  👥 Поиск команды
                </h3>
                <p className="text-lg text-gray-700 mb-4">
                  Найдите единомышленников и создайте команду для реализации
                  важных социальных проектов и инициатив.
                </p>
                <ul className="space-y-2">
                  <li className="flex items-center gap-2">
                    <span className="badge badge-secondary">✓</span>
                    Поиск команд по интересам
                  </li>
                  <li className="flex items-center gap-2">
                    <span className="badge badge-secondary">✓</span>
                    Фильтрация по навыкам
                  </li>
                  <li className="flex items-center gap-2">
                    <span className="badge badge-secondary">✓</span>
                    Система рейтингов
                  </li>
                </ul>
              </div>
            </div>

            {/* Feature 3 */}
            <div className="grid grid-cols-1 md:grid-cols-2 gap-8 items-center">
              <div>
                <h3 className="text-3xl font-bold mb-4">
                  🏆 Достижения & Портфолио
                </h3>
                <p className="text-lg text-gray-700 mb-4">
                  Отслеживайте прогресс, получайте награды и создавайте
                  портфолио волонтёрского опыта для карьерного роста.
                </p>
                <ul className="space-y-2">
                  <li className="flex items-center gap-2">
                    <span className="badge badge-accent">✓</span>
                    Система бейджей и наград
                  </li>
                  <li className="flex items-center gap-2">
                    <span className="badge badge-accent">✓</span>
                    Экспорт в PDF
                  </li>
                  <li className="flex items-center gap-2">
                    <span className="badge badge-accent">✓</span>
                    Интеграция с LinkedIn
                  </li>
                </ul>
              </div>
              <div className="bg-gradient-to-br from-accent/20 to-primary/20 rounded-lg h-72 flex items-center justify-center">
                <Target className="w-32 h-32 text-accent opacity-50" />
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* CTA Section */}
      <section className="py-20 px-4 bg-gradient-to-r from-primary to-accent text-white">
        <div className="container mx-auto text-center">
          <h2 className="text-4xl font-bold mb-6">
            Готовы изменить мир к лучшему?
          </h2>
          <p className="text-xl mb-8 max-w-2xl mx-auto">
            Присоединитесь к тысячам волонтёров, которые уже вносят
            положительные изменения в своих сообществах.
          </p>
          {!isAuthenticated && (
            <Link to="/register" className="btn btn-lg btn-white gap-2">
              Начать сейчас
            </Link>
          )}
        </div>
      </section>

      {/* Stats Section */}
      <section className="py-20 px-4 bg-base-100">
        <div className="container mx-auto">
          <div className="grid grid-cols-1 md:grid-cols-3 gap-8 text-center">
            <div>
              <div className="text-5xl font-bold text-primary mb-2">5000+</div>
              <p className="text-xl text-gray-600">Волонтёров</p>
            </div>
            <div>
              <div className="text-5xl font-bold text-secondary mb-2">200+</div>
              <p className="text-xl text-gray-600">Проектов</p>
            </div>
            <div>
              <div className="text-5xl font-bold text-accent mb-2">50000+</div>
              <p className="text-xl text-gray-600">Часов волонтёрства</p>
            </div>
          </div>
        </div>
      </section>
    </div>
  );
};

export default Home;
