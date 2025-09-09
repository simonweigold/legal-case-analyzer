// components/Navbar/Navbar.tsx
import React from 'react';
import { Sun, Moon, RotateCcw, Activity } from 'lucide-react';
import { cn } from '../../lib/utils';

export interface NavbarProps {
  darkMode: boolean;
  onThemeToggle: () => void;
  sessionId: string | null;
  onClearSession: () => void;
  isStreaming: boolean;
  loading: boolean;
}

export function Navbar({
  darkMode,
  onThemeToggle,
  sessionId,
  onClearSession,
  isStreaming,
  loading
}: NavbarProps) {
  return (
    <nav className="h-14 px-4 flex items-center justify-between bg-card border-b border-border">
      {/* Left side - Logo/Title */}
      <div className="flex items-center space-x-3">
        <div className="flex items-center space-x-2">
          <div className="w-8 h-8 bg-primary text-primary-foreground rounded-lg flex items-center justify-center">
            <span className="text-sm font-bold">LA</span>
          </div>
          <h1 className="text-lg font-semibold text-foreground">Legal Analyzer</h1>
        </div>
      </div>

      {/* Center - Status */}
      <div className="flex items-center space-x-2">
        {(loading || isStreaming) && (
          <div className="flex items-center space-x-2 text-muted-foreground">
            <Activity className="w-4 h-4 animate-pulse" />
            <span className="text-sm">
              {isStreaming ? 'Streaming...' : 'Processing...'}
            </span>
          </div>
        )}
        {sessionId && (
          <span className="text-xs text-muted-foreground px-2 py-1 bg-muted rounded">
            Session: {sessionId.slice(-8)}
          </span>
        )}
      </div>

      {/* Right side - Actions */}
      <div className="flex items-center space-x-2">
        {sessionId && (
          <button
            onClick={onClearSession}
            disabled={loading || isStreaming}
            className={cn(
              "btn btn-ghost h-8 w-8 p-0",
              (loading || isStreaming) && "opacity-50 cursor-not-allowed"
            )}
            title="Clear Session"
          >
            <RotateCcw className="w-4 h-4" />
          </button>
        )}
        
        <button
          onClick={onThemeToggle}
          className="btn btn-ghost h-8 w-8 p-0"
          title={darkMode ? 'Switch to Light Mode' : 'Switch to Dark Mode'}
        >
          {darkMode ? (
            <Sun className="w-4 h-4" />
          ) : (
            <Moon className="w-4 h-4" />
          )}
        </button>
      </div>
    </nav>
  );
}