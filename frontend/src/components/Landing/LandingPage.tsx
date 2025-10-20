import React, { useState, useRef } from 'react';
import { useNavigate } from 'react-router-dom';
import { Navbar } from '../Navbar';
import { Button } from '../ui/button';
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
        text: `${textInput.trim()}\n\nPlease analyze this legal text.`
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
      <div className="flex-1 flex items-center justify-center text-muted-foreground select-none">
        {/*Grid with two columns and grey borders for every grid field. The first column is 1/3 wide. The second 2/3*/}
        <div className="grid grid-cols-[1fr_3fr] border-b border-border w-full h-full">
            <div className="">
                <div className="grid grid-rows-[1fr_2fr] border-r border-border h-full">
                  <div className="p-12 text-2xl border-b border-border h-full flex items-center justify-center leading-snug">
                    Welcome to CLERK, an agentic AI web app for analyzing court decisions with ease
                  </div>
                  <div className="diagonal-lines">
                  </div>
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
            {/*
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
            */}
        </div>
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
