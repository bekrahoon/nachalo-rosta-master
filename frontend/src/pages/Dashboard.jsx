import { useEffect } from 'react';
import { useAuth } from '../hooks/useAuth';
import { Link } from 'react-router-dom';
import { TrendingUp, Bookmark, Globe } from 'lucide-react';
import { subscribeToPush } from '../utils/pushNotifications';

export const Dashboard = () => {
  const { user, getProfile } = useAuth();

  useEffect(() => {
    if (!user) {
      getProfile();
    }
  }, [user, getProfile]);

  useEffect(() => {
    subscribeToPush();
  }, []);

  const features = [
    {
      icon: Globe,
      title: 'Возможности',
      description: 'Хакатоны, стажировки, гранты и IT-программы из реальных источников',
      href: '/opportunities',
    },
    {
      icon: TrendingUp,
      title: 'AI Рекомендации',
      description: 'AI подберёт IT-возможности под ваш профиль',
      href: '/recommendations',
    },
    {
      icon: Bookmark,
      title: 'Избранное',
      description: 'Сохранённые возможности в одном месте',
      href: '/portfolio',
    },
  ];

  return (
    <div className="space-y-8">
      {/* Welcome Section */}
      <section className="hero bg-gradient-to-r from-primary to-accent rounded-lg shadow-lg">
        <div className="hero-content text-white text-center">
          <div>
            <h1 className="text-5xl font-bold mb-4">
              Добро пожаловать, {user?.first_name}! 👋
            </h1>
            <p className="text-xl mb-6 max-w-2xl">
              Начните свой путь в мире IT. Найдите возможности,
              которые соответствуют вашим интересам и ценностям.
            </p>
            <div className="flex gap-4 justify-center">
              <Link to="/opportunities" className="btn btn-outline btn-white">
                Найти возможности
              </Link>
              <Link to="/profile" className="btn btn-white">
                Завершить профиль
              </Link>
            </div>
          </div>
        </div>
      </section>

      {/* Features Grid */}
      <section>
        <h2 className="text-3xl font-bold mb-8">Начните работу</h2>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          {features.map((feature) => {
            const Icon = feature.icon;
            return (
              <Link
                key={feature.href}
                to={feature.href}
                className="card bg-base-100 hover:shadow-lg transition-shadow cursor-pointer"
              >
                <div className="card-body">
                  <div className="flex items-start gap-4">
                    <div className="bg-primary/10 p-3 rounded-lg">
                      <Icon className="w-6 h-6 text-primary" />
                    </div>
                    <div className="flex-1">
                      <h3 className="card-title text-lg">{feature.title}</h3>
                      <p className="text-sm text-gray-600 mt-2">
                        {feature.description}
                      </p>
                    </div>
                  </div>
                </div>
              </Link>
            );
          })}
        </div>
      </section>

      {/* CTA Section */}
      <section className="bg-gradient-to-r from-primary/10 to-accent/10 rounded-lg p-8 text-center">
        <h2 className="text-2xl font-bold mb-4">Не знаете с чего начать?</h2>
        <p className="text-gray-600 mb-6 max-w-2xl mx-auto">
          Наши AI-рекомендации помогут вам найти подходящие IT-возможности
          на основе ваших интересов и навыков.
        </p>
        <Link to="/recommendations" className="btn btn-primary">
          Получить рекомендации
        </Link>
      </section>
    </div>
  );
};

export default Dashboard;
