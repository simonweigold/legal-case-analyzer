import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { Navbar } from '../Navbar';
import { Button } from '../ui/button';
import { AuthModal } from '../Auth/AuthModal';
import { useAuth } from '../../contexts/AuthContext';

// Super minimal landing page: just the Navbar inside an app-like container.
// Matches the original App header styling and leaves the rest of the screen blank.
export const LandingPage: React.FC = () => {
  const { isAuthenticated } = useAuth();
  const navigate = useNavigate();
  const [authModalOpen, setAuthModalOpen] = useState(false);
  const [authMode, setAuthMode] = useState<'login' | 'register'>('login');

  const handleOpen = (mode: 'login' | 'register') => {
    setAuthMode(mode);
    setAuthModalOpen(true);
  };

  const handleClose = () => {
    setAuthModalOpen(false);
    // After modal closes, if authenticated go to /causa
    if (isAuthenticated) {
      navigate('/causa');
    }
  };

  // If user already authenticated and hits landing, kick them to app
  if (isAuthenticated) {
    // Navigate on next tick to avoid rendering during existing commit
    setTimeout(() => navigate('/causa'), 0);
  }

  return (
    <div className="h-screen flex flex-col bg-background">
      <Navbar sessionId={null} onClearSession={() => {}} isStreaming={false} loading={false} />
      <div className="flex-1 flex items-center justify-center text-muted-foreground select-none">
        {/*Grid with two columns and grey borders for every grid field. The first column is 1/3 wide. The second 2/3*/}
        <div className="grid grid-cols-[1fr_3fr_1fr] border-b border-border w-full h-full">
            <div className="">
                <div className="grid grid-rows-[1fr_2fr] border-r border-border h-full">
                  <div className="p-12 text-2xl border-b border-border h-full flex items-center justify-center leading-snug">
                    Welcome to CAUSA AI, an agentic AI web app for analyzing court decisions with ease
                  </div>
                    <div className="p-2 bg-muted/30 diagonal-lines">
                      Column 1 Row 2 Shaded
                    </div>
                </div>
            </div>
            <div className="">
                Placeholder
            </div>
            <div className="grid grid-rows-[2fr_1fr] border-l border-border h-full">
                <div className="p-12 text-2xl h-full flex flex-col gap-8 items-center justify-center border-b border-border leading-snug">
                  <div className="max-w-sm">
                    Start by uploading your case or create an account to save and revisit your legal analysis sessions
                  </div>
                </div>
                <div className="p-2 bg-muted/30 diagonal-lines flex items-center justify-center text-sm text-muted-foreground">
                  <div className="flex gap-6">
                    <Button
                      variant="outline"
                      size="sm"
                      onClick={() => handleOpen('login')}
                      className="w-28 bg-white hover:bg-blue-50 hover:border-blue-200"
                    >
                      Sign In
                    </Button>
                    <Button
                      variant="outline"
                      size="sm"
                      onClick={() => handleOpen('register')}
                      className="w-28 bg-white hover:bg-blue-50 hover:border-blue-200"
                    >
                      Sign Up
                    </Button>
                  </div>
                </div>
            </div>
        </div>
      </div>
      <div className="grid place-items-center p-4 text-xs text-muted-foreground">
        © {new Date().getFullYear()} CAUSA AI
      </div>
      <AuthModal
        open={authModalOpen}
        onClose={handleClose}
        mode={authMode}
        onModeChange={setAuthMode}
      />
    </div>
  );
};
