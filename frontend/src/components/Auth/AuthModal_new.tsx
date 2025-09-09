// components/Auth/AuthModal.tsx
import React, { useState, Fragment } from 'react';
import { Dialog, Transition } from '@headlessui/react';
import { X } from 'lucide-react';
import { LoginForm } from './LoginForm';
import { RegisterForm } from './RegisterForm';

interface AuthModalProps {
  open: boolean;
  onClose: () => void;
  mode: 'login' | 'register';
  onModeChange: (mode: 'login' | 'register') => void;
}

export function AuthModal({ open, onClose, mode, onModeChange }: AuthModalProps) {
  const handleSuccess = () => {
    onClose();
  };

  const switchToLogin = () => onModeChange('login');
  const switchToRegister = () => onModeChange('register');

  return (
    <Transition appear show={open} as={Fragment}>
      <Dialog as="div" className="relative z-50" onClose={onClose}>
        <Transition.Child
          as={Fragment}
          enter="ease-out duration-300"
          enterFrom="opacity-0"
          enterTo="opacity-100"
          leave="ease-in duration-200"
          leaveFrom="opacity-100"
          leaveTo="opacity-0"
        >
          <div className="fixed inset-0 bg-black/25" />
        </Transition.Child>

        <div className="fixed inset-0 overflow-y-auto">
          <div className="flex min-h-full items-center justify-center p-4 text-center">
            <Transition.Child
              as={Fragment}
              enter="ease-out duration-300"
              enterFrom="opacity-0 scale-95"
              enterTo="opacity-100 scale-100"
              leave="ease-in duration-200"
              leaveFrom="opacity-100 scale-100"
              leaveTo="opacity-0 scale-95"
            >
              <Dialog.Panel className="w-full max-w-md transform overflow-hidden rounded-2xl bg-card text-card-foreground shadow-xl transition-all border border-border">
                <div className="relative p-6">
                  <button
                    onClick={onClose}
                    className="absolute right-4 top-4 btn btn-ghost h-8 w-8 p-0 text-muted-foreground hover:text-foreground"
                  >
                    <X className="w-4 h-4" />
                  </button>

                  <div className="mb-6">
                    <Dialog.Title
                      as="h3"
                      className="text-2xl font-semibold text-center text-foreground"
                    >
                      {mode === 'login' ? 'Welcome back' : 'Create account'}
                    </Dialog.Title>
                    <p className="text-sm text-muted-foreground text-center mt-2">
                      {mode === 'login'
                        ? 'Sign in to your account to continue'
                        : 'Sign up to save your conversations'
                      }
                    </p>
                  </div>

                  {mode === 'login' ? (
                    <LoginForm
                      onSuccess={handleSuccess}
                      onSwitchToRegister={switchToRegister}
                    />
                  ) : (
                    <RegisterForm
                      onSuccess={handleSuccess}
                      onSwitchToLogin={switchToLogin}
                    />
                  )}
                </div>
              </Dialog.Panel>
            </Transition.Child>
          </div>
        </div>
      </Dialog>
    </Transition>
  );
}
