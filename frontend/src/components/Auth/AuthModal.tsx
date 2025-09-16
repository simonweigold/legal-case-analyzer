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
              <Dialog.Panel className="w-full max-w-md transform overflow-hidden rounded-causa-lg bg-white text-dark shadow-xl transition-all border border-gray/20">
                <div className="relative p-8">
                  <button
                    onClick={onClose}
                    className="absolute right-4 top-4 p-1 text-gray hover:text-dark transition-colors"
                  >
                    <X className="w-5 h-5" />
                  </button>

                  <div className="mb-8">
                    <Dialog.Title
                      as="h3"
                      className="text-h2 text-center text-dark"
                    >
                      {mode === 'login' ? 'Welcome back' : 'Join CAUSA AI'}
                    </Dialog.Title>
                    <p className="text-body text-gray-dark text-center mt-3">
                      {mode === 'login'
                        ? 'Sign in to access your legal analysis history'
                        : 'Create your account to save legal analysis sessions'
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
