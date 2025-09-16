// components/Auth/LoginForm.tsx
import React, { useState } from 'react';
import { Eye, EyeOff } from 'lucide-react';
import { useAuth } from '../../contexts/AuthContext';
import { cn } from '../../lib/utils';

interface LoginFormProps {
  onSwitchToRegister: () => void;
  onSuccess?: () => void;
}

export function LoginForm({ onSwitchToRegister, onSuccess }: LoginFormProps) {
  const { login, isLoading, error, clearError } = useAuth();
  const [formData, setFormData] = useState({
    username: '',
    password: '',
  });
  const [showPassword, setShowPassword] = useState(false);
  const [formErrors, setFormErrors] = useState<Record<string, string>>({});

  const validateForm = () => {
    const errors: Record<string, string> = {};
    
    if (!formData.username.trim()) {
      errors.username = 'Email is required';
    } else if (!/\S+@\S+\.\S+/.test(formData.username)) {
      errors.username = 'Email is invalid';
    }
    
    if (!formData.password) {
      errors.password = 'Password is required';
    }
    
    setFormErrors(errors);
    return Object.keys(errors).length === 0;
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    clearError();
    
    if (!validateForm()) {
      return;
    }

    try {
      await login(formData);
      onSuccess?.();
    } catch (error) {
      // Error is handled by the auth context
    }
  };

  const handleChange = (field: string) => (e: React.ChangeEvent<HTMLInputElement>) => {
    setFormData(prev => ({ ...prev, [field]: e.target.value }));
    if (formErrors[field]) {
      setFormErrors(prev => ({ ...prev, [field]: '' }));
    }
  };

  return (
    <div>
      <form onSubmit={handleSubmit} className="space-y-6">
        {error && (
          <div className="bg-red-50 border border-red-200 rounded-causa p-4">
            <p className="text-small text-red-600">{error}</p>
          </div>
        )}

        <div className="space-y-4">
          <div>
            <label htmlFor="email" className="block text-body text-dark mb-2">
              Email
            </label>
            <input
              id="email"
              type="email"
              value={formData.username}
              onChange={handleChange('username')}
              className={cn(
                "causa-input w-full",
                formErrors.username && "border-red-500"
              )}
              placeholder="Enter your email"
              disabled={isLoading}
            />
            {formErrors.username && (
              <p className="text-small text-red-500 mt-1">{formErrors.username}</p>
            )}
          </div>

          <div>
            <label htmlFor="password" className="block text-body text-dark mb-2">
              Password
            </label>
            <div className="relative">
              <input
                id="password"
                type={showPassword ? 'text' : 'password'}
                value={formData.password}
                onChange={handleChange('password')}
                className={cn(
                  "causa-input w-full pr-12",
                  formErrors.password && "border-red-500"
                )}
                placeholder="Enter your password"
                disabled={isLoading}
              />
              <button
                type="button"
                onClick={() => setShowPassword(!showPassword)}
                className="absolute right-3 top-1/2 transform -translate-y-1/2 text-gray hover:text-dark"
                disabled={isLoading}
              >
                {showPassword ? <EyeOff className="w-4 h-4" /> : <Eye className="w-4 h-4" />}
              </button>
            </div>
            {formErrors.password && (
              <p className="text-small text-red-500 mt-1">{formErrors.password}</p>
            )}
          </div>
        </div>

        <button
          type="submit"
          disabled={isLoading}
          className={cn(
            "causa-btn causa-btn-primary w-full",
            isLoading && "opacity-50 cursor-not-allowed"
          )}
        >
          {isLoading ? (
            <div className="flex items-center justify-center">
              <div className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin mr-2" />
              Signing in...
            </div>
          ) : (
            'Sign In'
          )}
        </button>

        <div className="text-center">
          <p className="text-body text-gray-dark">
            Don't have an account?{' '}
            <button
              type="button"
              onClick={onSwitchToRegister}
              className="text-brand font-medium hover:underline"
              disabled={isLoading}
            >
              Create account
            </button>
          </p>
        </div>
      </form>
    </div>
  );
}
