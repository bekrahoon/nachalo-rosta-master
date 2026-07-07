import { Loader } from 'lucide-react';

export const LoadingSpinner = () => {
  return (
    <div className="flex items-center justify-center min-h-screen">
      <div className="text-center">
        <Loader className="w-12 h-12 animate-spin mx-auto text-primary mb-4" />
        <p className="text-lg text-gray-600">Загрузка...</p>
      </div>
    </div>
  );
};

export default LoadingSpinner;
