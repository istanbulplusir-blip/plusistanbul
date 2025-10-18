'use client';

import React, { useState, createContext, useContext, ReactNode } from 'react';
import { X, CheckCircle, AlertCircle, Info, AlertTriangle } from 'lucide-react';

export type ToastType = 'success' | 'error' | 'warning' | 'info';

export interface Toast {
  id: string;
  type: ToastType;
  title: string;
  message?: string;
  duration?: number;
  action?: {
    label: string;
    onClick: () => void;
  };
}

interface ToastContextType {
  toasts: Toast[];
  addToast: (toast: Omit<Toast, 'id'>) => void;
  removeToast: (id: string) => void;
  clearToasts: () => void;
  showToast: (message: string, type?: ToastType) => void;
}

const ToastContext = createContext<ToastContextType | undefined>(undefined);

export const useToast = () => {
  const context = useContext(ToastContext);
  if (!context) {
    throw new Error('useToast must be used within a ToastProvider');
  }
  return context;
};

interface ToastProviderProps {
  children: ReactNode;
}

export const ToastProvider: React.FC<ToastProviderProps> = ({ children }) => {
  const [toasts, setToasts] = useState<Toast[]>([]);

  const addToast = (toast: Omit<Toast, 'id'>) => {
    const id = Math.random().toString(36).substr(2, 9);
    const newToast: Toast = {
      ...toast,
      id,
      duration: toast.duration ?? 5000,
    };

    setToasts(prev => [...prev, newToast]);

    // Auto remove after duration
    if (newToast.duration && newToast.duration > 0) {
      setTimeout(() => {
        removeToast(id);
      }, newToast.duration);
    }
  };

  const removeToast = (id: string) => {
    setToasts(prev => prev.filter(toast => toast.id !== id));
  };

  const clearToasts = () => {
    setToasts([]);
  };

  const showToast = (message: string, type: ToastType = 'info') => {
    addToast({
      type,
      title: message,
      message: '',
    });
  };

  return (
    <ToastContext.Provider value={{ toasts, addToast, removeToast, clearToasts, showToast }}>
      {children}
      <ToastContainer />
    </ToastContext.Provider>
  );
};

const ToastContainer: React.FC = () => {
  const { toasts, removeToast } = useToast();

  const getToastIcon = (type: ToastType) => {
    switch (type) {
      case 'success':
        return <CheckCircle className="h-5 w-5 text-green-500" />;
      case 'error':
        return <AlertCircle className="h-5 w-5 text-red-500" />;
      case 'warning':
        return <AlertTriangle className="h-5 w-5 text-yellow-500" />;
      case 'info':
        return <Info className="h-5 w-5 text-blue-500" />;
      default:
        return <Info className="h-5 w-5 text-blue-500" />;
    }
  };

  const getToastStyles = (type: ToastType) => {
    const baseStyles = "flex items-start gap-3 p-4 rounded-lg shadow-lg border-l-4 transform transition-all duration-300 ease-in-out";
    
    switch (type) {
      case 'success':
        return `${baseStyles} bg-green-50 dark:bg-green-900/20 border-green-500 text-green-800 dark:text-green-200`;
      case 'error':
        return `${baseStyles} bg-red-50 dark:bg-red-900/20 border-red-500 text-red-800 dark:text-red-200`;
      case 'warning':
        return `${baseStyles} bg-yellow-50 dark:bg-yellow-900/20 border-yellow-500 text-yellow-800 dark:text-yellow-200`;
      case 'info':
        return `${baseStyles} bg-blue-50 dark:bg-blue-900/20 border-blue-500 text-blue-800 dark:text-blue-200`;
      default:
        return `${baseStyles} bg-gray-50 dark:bg-gray-900/20 border-gray-500 text-gray-800 dark:text-gray-200`;
    }
  };

  if (toasts.length === 0) return null;

  return (
    <div className="fixed top-4 right-4 z-50 space-y-2 max-w-sm">
      {toasts.map((toast) => (
        <div
          key={toast.id}
          className={`${getToastStyles(toast.type)} animate-slide-in`}
          role="alert"
          aria-live="assertive"
        >
          <div className="flex-shrink-0">
            {getToastIcon(toast.type)}
          </div>
          
          <div className="flex-1 min-w-0">
            <p className="text-sm font-medium">{toast.title}</p>
            {toast.message && (
              <p className="text-sm mt-1 opacity-90">{toast.message}</p>
            )}
            {toast.action && (
              <button
                onClick={toast.action.onClick}
                className="mt-2 px-3 py-1 text-xs font-medium bg-white/20 dark:bg-black/20 rounded-md hover:bg-white/30 dark:hover:bg-black/30 transition-colors"
              >
                {toast.action.label}
              </button>
            )}
          </div>
          
          <button
            onClick={() => removeToast(toast.id)}
            className="flex-shrink-0 ml-2 p-1 rounded-md hover:bg-black/10 dark:hover:bg-white/10 transition-colors"
            aria-label="Close notification"
          >
            <X className="h-4 w-4" />
          </button>
        </div>
      ))}
    </div>
  );
};

// Toast helper functions
export const toast = {
  success: () => {
    if (typeof window !== 'undefined') {
      // This will be called from components that use useToast
      console.warn('toast.success called outside of ToastProvider. Use useToast hook instead.');
    }
  },
  error: () => {
    if (typeof window !== 'undefined') {
      console.warn('toast.error called outside of ToastProvider. Use useToast hook instead.');
    }
  },
  warning: () => {
    if (typeof window !== 'undefined') {
      console.warn('toast.warning called outside of ToastProvider. Use useToast hook instead.');
    }
  },
  info: () => {
    if (typeof window !== 'undefined') {
      console.warn('toast.info called outside of ToastProvider. Use useToast hook instead.');
    }
  },
}; 