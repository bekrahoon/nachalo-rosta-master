import { AlertCircle, CheckCircle, InfoIcon, XCircle } from 'lucide-react';

export const Alert = ({ type = 'info', message, onClose }) => {
  if (!message) return null;

  const typeClasses = {
    success: 'alert alert-success',
    error: 'alert alert-error',
    warning: 'alert alert-warning',
    info: 'alert alert-info',
  };

  const icons = {
    success: <CheckCircle className="w-5 h-5" />,
    error: <XCircle className="w-5 h-5" />,
    warning: <AlertCircle className="w-5 h-5" />,
    info: <InfoIcon className="w-5 h-5" />,
  };

  return (
    <div className={`${typeClasses[type]} shadow-lg`}>
      <span className="flex items-center gap-2">
        {icons[type]}
        {message}
      </span>
      {onClose && (
        <button
          onClick={onClose}
          className="btn btn-sm btn-ghost"
        >
          ✕
        </button>
      )}
    </div>
  );
};

export default Alert;
