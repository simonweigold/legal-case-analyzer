// components/Navbar/Navbar.tsx
import React from 'react';
import { RotateCcw, Activity } from 'lucide-react';
import { cn } from '../../lib/utils';

export interface NavbarProps {
  sessionId: string | null;
  onClearSession: () => void;
  isStreaming: boolean;
  loading: boolean;
}

export function Navbar({
  sessionId,
  onClearSession,
  isStreaming,
  loading
}: NavbarProps) {
  return (
    <nav className="h-16 px-6 flex items-center justify-between bg-white">
      {/* Left side - CAUSA AI Logo */}
      <div className="flex items-center space-x-4">
        <div className="flex items-center space-x-3">
          <div className="w-10 h-10 bg-brand text-white rounded-causa flex items-center justify-center">
            <span className="text-body font-bold">CA</span>
          </div>
          <h1 className="causa-logo text-xl">CAUSA AI</h1>
        </div>
      </div>

      {/* Center - Status */}
      <div className="flex items-center space-x-3">
        {(loading || isStreaming) && (
          <div className="flex items-center space-x-2 text-gray">
            <Activity className="w-4 h-4 animate-pulse" />
            <span className="text-small">
              {isStreaming ? 'Analyzing...' : 'Processing...'}
            </span>
          </div>
        )}
        {sessionId && typeof sessionId === 'string' && (
          <span className="text-xs text-gray px-2 py-1 bg-light rounded-causa border border-gray/20">
            Session: {sessionId.slice(-8)}
          </span>
        )}
      </div>

      {/* Right side - Actions */}
      <div className="flex items-center space-x-3">
        <button
          className="p-2 text-dark hover:text-gray transition-colors"
          title="Menu"
        >
          <svg className="w-5 h-5" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
            <path d="M3 12h18M3 6h18M3 18h18" />
          </svg>
        </button>
        {sessionId && (
          <button
            onClick={onClearSession}
            disabled={loading || isStreaming}
            className={cn(
              "p-2 text-dark hover:text-gray transition-colors rounded-causa",
              (loading || isStreaming) && "opacity-50 cursor-not-allowed"
            )}
            title="Clear Session"
          >
            <RotateCcw className="w-4 h-4" />
          </button>
        )}
      </div>
    </nav>
  );
}