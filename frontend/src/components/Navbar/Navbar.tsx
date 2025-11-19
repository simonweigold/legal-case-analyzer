// components/Navbar/Navbar.tsx
import React from 'react';
import { Link } from 'react-router-dom';

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
    <header className="border-b border-border bg-background px-6 py-4">
      <div className="flex items-center justify-between">
        <Link to="/" className="flex items-center cursor-pointer">
          <div className="w-0 h-8 bg-primary rounded flex items-center justify-center">
            <div className="w-2 h-2 bg-white rounded-full"></div>
          </div>
          <h1 className="clerk-logo">CLERK</h1>
        </Link>
        <div>
          <Link to="/about" className="text-sm text-muted-foreground hover:text-foreground">
            About
          </Link>
        </div>
      </div>
    </header>
  );
}