import React, { useState, useRef, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { Navbar } from '../Navbar';
import { AuthModal } from '../Auth/AuthModal';
import { useAuth } from '../../contexts/AuthContext';
import { Textarea } from '../ui/textarea';
import { Upload, FileText, Type } from 'lucide-react';

// Super minimal landing page: just the Navbar inside an app-like container.
// Matches the original App header styling and leaves the rest of the screen blank.
export const LandingPage: React.FC = () => {
  const { isAuthenticated } = useAuth();
  const navigate = useNavigate();
  const [authModalOpen, setAuthModalOpen] = useState(false);
  const [authMode, setAuthMode] = useState<'login' | 'register'>('login');
  const [uploadedFile, setUploadedFile] = useState<File | null>(null);
  const [textInput, setTextInput] = useState('');
  const [dragActive, setDragActive] = useState(false);
  const [hoveredSection, setHoveredSection] = useState<'upload' | 'text' | null>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);
  const pendingAnalysisRef = useRef<{source:'pdf'|'text'; text:string; filename?:string} | null>(null);
  const [isPortrait, setIsPortrait] = useState(() =>
    typeof window !== 'undefined'
      ? window.matchMedia('(orientation: portrait)').matches
      : true
  );

  useEffect(() => {
    if (typeof window === 'undefined') return;
    const mq = window.matchMedia('(orientation: portrait)');
    const handler = (e: MediaQueryListEvent) => setIsPortrait(e.matches);
    // Use addEventListener if available, else fallback
    if (mq.addEventListener) {
      mq.addEventListener('change', handler);
    } else {
      // @ts-ignore - Safari <14
      mq.addListener(handler);
    }
    return () => {
      if (mq.removeEventListener) {
        mq.removeEventListener('change', handler);
      } else {
        // @ts-ignore
        mq.removeListener(handler);
      }
    };
  }, []);

  const handleOpen = (mode: 'login' | 'register') => {
    setAuthMode(mode);
    setAuthModalOpen(true);
  };

  const handleClose = () => {
    setAuthModalOpen(false);
    if (isAuthenticated) {
      if (pendingAnalysisRef.current) {
        navigate('/clerk', { state: { pendingAnalysis: pendingAnalysisRef.current } });
        pendingAnalysisRef.current = null;
      } else {
        navigate('/clerk');
      }
    }
  };

  // If user already authenticated and hits landing, kick them to app
  if (isAuthenticated && !authModalOpen && !uploadedFile && !textInput) {
    // Passive redirect only if no staged input; avoid interfering with in-progress landing actions
    setTimeout(() => navigate('/clerk'), 0);
  }

  const handleDrag = (e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    if (e.type === 'dragenter' || e.type === 'dragover') {
      setDragActive(true);
      setDragActive(true);
    } else if (e.type === 'dragleave') {
      setDragActive(false);
    }
  };

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    setDragActive(false);
    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      const file = e.dataTransfer.files[0];
      if (file.type === 'application/pdf') {
        setUploadedFile(file);
      }
    }
  };

  const handleFileInput = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) {
      const file = e.target.files[0];
      if (file.type === 'application/pdf') {
        setUploadedFile(file);
      }
    }
  };

  const hasContent = !!uploadedFile || textInput.trim().length > 0;

  const triggerAnalysis = () => {
    if (!hasContent) return;
    // Build pending analysis payload similar to InputSidebar formatting
    if (uploadedFile) {
      pendingAnalysisRef.current = {
        source: 'pdf',
        filename: uploadedFile.name,
        text: `[Document: ${uploadedFile.name}]\n\nPlease analyze this legal document.`
      };
    } else {
      pendingAnalysisRef.current = {
        source: 'text',
        text: `${textInput.trim()}`
      };
    }

    if (!isAuthenticated) {
      // Prompt sign up first
      setAuthMode('register');
      setAuthModalOpen(true);
      return;
    }
    // Navigate directly with state
    navigate('/clerk', { state: { pendingAnalysis: pendingAnalysisRef.current } });
    pendingAnalysisRef.current = null;
  };

  return (
    <div className="h-screen flex flex-col bg-background">
      <Navbar sessionId={null} onClearSession={() => {}} isStreaming={false} loading={false} />
      <div className="flex-1 w-full select-none">
        {isPortrait ? (
          <div className="flex flex-col gap-8 px-6 py-12 items-center">
            <div className="text-xl leading-snug max-w-md text-foreground mb-4 text-center">
              <p>
                Welcome to CLERK, an <span className="font-bold text-primary">Open Source AI Agent</span> for Analyzing Court Decisions with Ease
              </p>
            </div>
            <div className="w-full">
              <video
                className="w-full h-auto rounded-md shadow-sm"
                src="/demo.mov"
                playsInline
                autoPlay
                muted
                loop
                controls
                preload="metadata"
              >
                Your browser does not support the video tag.
              </video>
            </div>
          </div>
        ) : (
          <div className="grid grid-cols-[1fr_3fr] border-b border-border w-full h-full">
            <div className="">
              <div className="grid grid-rows-[1fr_2fr] border-r border-border h-full">
                <div className="p-12 text-2xl border-b border-border h-full flex items-center justify-center leading-snug text-foreground">
                  <div className="max-w-md">
                    <p>
                      Welcome to CLERK, an <span className="font-bold text-primary">Open Source AI Agent</span> for Analyzing Court Decisions with Ease
                    </p>
                  </div>
                </div>
                <div className="diagonal-lines" />
              </div>
            </div>
            <div className="flex items-center justify-center p-12 bg-blue-animation">
              <video
                className="max-w-full max-h-full"
                src="/demo.mov"
                playsInline
                autoPlay
                muted
                loop
                controls
                preload="metadata"
              >
                Your browser does not support the video tag.
              </video>
            </div>
          </div>
        )}
      </div>
      <div className="grid place-items-center p-4 text-xs text-muted-foreground">
        © {new Date().getFullYear()} CLERK
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
