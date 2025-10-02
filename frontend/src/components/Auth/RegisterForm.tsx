// components/Auth/RegisterForm.tsx
import React, { useState } from 'react';
import { Eye, EyeOff } from 'lucide-react';
import { useAuth } from '../../contexts/AuthContext';
import { cn } from '../../lib/utils';

interface RegisterFormProps {
  onSwitchToLogin: () => void;
  onSuccess?: () => void;
}

export function RegisterForm({ onSwitchToLogin, onSuccess }: RegisterFormProps) {
  const { register, isLoading, error, clearError } = useAuth();
  const [formData, setFormData] = useState({
    email: '',
    password: '',
    confirmPassword: '',
    name: '',
  });
  const [showPassword, setShowPassword] = useState(false);
  const [showConfirmPassword, setShowConfirmPassword] = useState(false);
  const [formErrors, setFormErrors] = useState<Record<string, string>>({});

  const validateForm = () => {
    const errors: Record<string, string> = {};
    
    if (!formData.email.trim()) {
      errors.email = 'Email is required';
    } else if (!/\S+@\S+\.\S+/.test(formData.email)) {
      errors.email = 'Email is invalid';
    }
    
    if (!formData.password) {
      errors.password = 'Password is required';
    } else if (formData.password.length < 8) {
      errors.password = 'Password must be at least 8 characters';
    }
    
    if (!formData.confirmPassword) {
      errors.confirmPassword = 'Please confirm your password';
    } else if (formData.password !== formData.confirmPassword) {
      errors.confirmPassword = 'Passwords do not match';
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
      await register({
        email: formData.email,
        password: formData.password,
        name: formData.name || undefined,
      });
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

        <div className="space-y-6">
          <div>
            <label htmlFor="name" className="block text-body text-dark mb-2">
              Full Name (Optional)
            </label>
            <input
              id="name"
              type="text"
              value={formData.name}
              onChange={handleChange('name')}
              className="causa-input w-full"
              placeholder="Enter your full name"
              disabled={isLoading}
            />
          </div>

          <div>
            <label htmlFor="email" className="block text-body text-dark mb-2">
              Email
            </label>
            <input
              id="email"
              type="email"
              value={formData.email}
              onChange={handleChange('email')}
              className={cn(
                "causa-input w-full",
                formErrors.email && "border-red-500"
              )}
              placeholder="Enter your email"
              disabled={isLoading}
            />
            {formErrors.email && (
              <p className="text-small text-red-500 mt-1">{formErrors.email}</p>
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
                placeholder="Create a password"
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
            {formErrors.password ? (
              <p className="text-small text-red-500 mt-1">{formErrors.password}</p>
            ) : (
              <p className="text-small text-gray mt-1">Must be at least 8 characters</p>
            )}
          </div>

          <div>
            <label htmlFor="confirmPassword" className="block text-body text-dark mb-2">
              Confirm Password
            </label>
            <div className="relative">
              <input
                id="confirmPassword"
                type={showConfirmPassword ? 'text' : 'password'}
                value={formData.confirmPassword}
                onChange={handleChange('confirmPassword')}
                className={cn(
                  "causa-input w-full pr-12",
                  formErrors.confirmPassword && "border-red-500"
                )}
                placeholder="Confirm your password"
                disabled={isLoading}
              />
              <button
                type="button"
                onClick={() => setShowConfirmPassword(!showConfirmPassword)}
                className="absolute right-3 top-1/2 transform -translate-y-1/2 text-gray hover:text-dark"
                disabled={isLoading}
              >
                {showConfirmPassword ? <EyeOff className="w-4 h-4" /> : <Eye className="w-4 h-4" />}
              </button>
            </div>
            {formErrors.confirmPassword && (
              <p className="text-small text-red-500 mt-1">{formErrors.confirmPassword}</p>
            )}
          </div>
        </div>

        <button
          type="submit"
          disabled={isLoading}
          className={cn(
            "w-full bg-white text-gray-700 border border-gray-300 hover:bg-gray-50 px-4 py-3 rounded-lg font-medium transition-colors",
            isLoading && "opacity-50 cursor-not-allowed"
          )}
        >
          {isLoading ? (
            <div className="flex items-center justify-center">
              <div className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin mr-2" />
              Creating account...
            </div>
          ) : (
            'Create Account'
          )}
        </button>

        <div className="text-center">
          <p className="text-body text-gray-dark">
            Already have an account?{' '}
            <button
              type="button"
              onClick={onSwitchToLogin}
              className="text-brand font-medium hover:underline"
              disabled={isLoading}
            >
              Sign in
            </button>
          </p>
        </div>
      </form>
    </div>
  );
}
