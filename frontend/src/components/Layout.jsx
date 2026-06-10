import { Outlet } from 'react-router-dom';
import Navbar from './Navbar';

export const Layout = () => {
  return (
    <div className="min-h-screen bg-base-200 flex flex-col">
      <Navbar />
      <main className="flex-1 container mx-auto px-4 py-8">
        <Outlet />
      </main>
      
      {/* Footer */}
      <footer className="bg-base-100 border-t border-base-300 mt-12">
        <div className="container mx-auto px-4 py-8">
          <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
            <div>
              <h3 className="font-bold text-lg mb-2">Начало Роста: Влияние</h3>
              <p className="text-sm text-gray-600">
                Платформа для молодёжного волонтёрства и развития
              </p>
            </div>
            <div>
              <h4 className="font-bold mb-2">Ссылки</h4>
              <ul className="text-sm space-y-1">
                <li><a href="#" className="link link-hover">О проекте</a></li>
                <li><a href="#" className="link link-hover">Контакты</a></li>
                <li><a href="#" className="link link-hover">Помощь</a></li>
              </ul>
            </div>
            <div>
              <h4 className="font-bold mb-2">Политика</h4>
              <ul className="text-sm space-y-1">
                <li><a href="#" className="link link-hover">Приватность</a></li>
                <li><a href="#" className="link link-hover">Условия использования</a></li>
              </ul>
            </div>
          </div>
          <div className="border-t border-base-300 mt-8 pt-8 text-center text-sm text-gray-600">
            <p>&copy; 2024 Начало Роста. Все права защищены.</p>
          </div>
        </div>
      </footer>
    </div>
  );
};

export default Layout;
