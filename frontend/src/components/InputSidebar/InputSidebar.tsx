// components/InputSidebar/InputSidebar.tsx
import React, { useState, useRef } from 'react';
import { Upload, FileText, Type } from 'lucide-react';
import { Button } from '../ui/button';
import { Textarea } from '../ui/textarea';
import { ToolSelector } from './ToolSelector';

export interface InputSidebarProps {
  open: boolean;
  onToggle: () => void;
  onTextSubmit: (text: string, source: 'text' | 'pdf', filename?: string, tools?: string[]) => void;
  isProcessing?: boolean;
}

export function InputSidebar({ open, onToggle, onTextSubmit, isProcessing = false }: InputSidebarProps) {
  const [dragActive, setDragActive] = useState(false);
  const [uploadedFile, setUploadedFile] = useState<string | null>(null);
  const [textInput, setTextInput] = useState("");
  const [hoveredSection, setHoveredSection] = useState<'upload' | 'text' | null>(null);
  const [selectedTools, setSelectedTools] = useState<string[]>([]);
  const fileInputRef = useRef<HTMLInputElement>(null);

  const handleDrag = (e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    if (e.type === "dragenter" || e.type === "dragover") {
      setDragActive(true);
    } else if (e.type === "dragleave") {
      setDragActive(false);
    }
  };

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    setDragActive(false);
    
    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      const file = e.dataTransfer.files[0];
      if (file.type === "application/pdf") {
        setUploadedFile(file.name);
      }
    }
  };

  const handleFileInput = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) {
      const file = e.target.files[0];
      if (file.type === "application/pdf") {
        setUploadedFile(file.name);
      }
    }
  };

  const handleSubmit = () => {
    if (uploadedFile) {
      onTextSubmit(`Document: ${uploadedFile}`, 'pdf', uploadedFile, selectedTools);
      setUploadedFile(null);
    } else if (textInput.trim()) {
      onTextSubmit(textInput.trim(), 'text', undefined, selectedTools);
      setTextInput('');
    }
  };

  const hasContent = uploadedFile || textInput.trim();

  return (
    <div className="w-80 border-r border-border bg-muted/30 diagonal-lines p-6 flex flex-col">
      <div className="mb-8">
        <h2 className="mb-6">Enter a legal case to analyze</h2>
        
        <div className="flex gap-2 h-48">
          {/* PDF Upload Section */}
          <div
            className={`
              relative border-2 border-dashed rounded-lg bg-white text-center transition-all duration-300 ease-in-out cursor-pointer
              ${dragActive 
                ? 'border-primary bg-primary/5' 
                : 'border-muted-foreground/30 hover:border-muted-foreground/50'
              }
              ${hoveredSection === 'upload' ? 'flex-[1.5]' : 'flex-1'}
              ${hoveredSection === 'text' ? 'flex-[0.5]' : ''}
            `}
            onDragEnter={handleDrag}
            onDragLeave={handleDrag}
            onDragOver={handleDrag}
            onDrop={handleDrop}
            onMouseEnter={() => setHoveredSection('upload')}
            onMouseLeave={() => setHoveredSection(null)}
            onClick={() => fileInputRef.current?.click()}
          >
            <input
              ref={fileInputRef}
              type="file"
              accept=".pdf"
              onChange={handleFileInput}
              className="absolute inset-0 w-full h-full opacity-0 cursor-pointer"
            />
            
            <div className="absolute inset-0 flex flex-col items-center justify-center p-3">
              {uploadedFile ? (
                <div className="flex flex-col items-center gap-2">
                  <FileText className="w-8 h-8 text-primary" />
                  <p className="text-xs text-center line-clamp-2">{uploadedFile}</p>
                  <Button 
                    variant="outline" 
                    size="sm"
                    onClick={(e) => {
                      e.stopPropagation();
                      setUploadedFile(null);
                    }}
                    className="text-xs px-2 py-1 h-auto"
                  >
                    Remove
                  </Button>
                </div>
              ) : (
                <div className="flex flex-col items-center gap-2">
                  <Upload className="w-8 h-8 text-muted-foreground" />
                  <p className="text-xs text-muted-foreground text-center">
                    Drag PDF here
                  </p>
                  <p className="text-xs text-muted-foreground text-center">
                    or click
                  </p>
                </div>
              )}
            </div>
          </div>

          {/* Text Input Section */}
          <div
            className={`
              relative border-2 border-dashed rounded-lg bg-white transition-all duration-300 ease-in-out
              border-muted-foreground/30 hover:border-muted-foreground/50
              ${hoveredSection === 'text' ? 'flex-[1.5]' : 'flex-1'}
              ${hoveredSection === 'upload' ? 'flex-[0.5]' : ''}
            `}
            onMouseEnter={() => setHoveredSection('text')}
            onMouseLeave={() => setHoveredSection(null)}
          >
            <div className="absolute inset-0 flex flex-col p-3">
              <div className="flex flex-col items-center gap-2 mb-3">
                <Type className="w-8 h-8 text-muted-foreground" />
                <p className="text-xs text-muted-foreground text-center">
                  Paste case text
                </p>
              </div>
              
              <Textarea
                placeholder="Paste your legal case text here..."
                value={textInput}
                onChange={(e) => setTextInput(e.target.value)}
                className="flex-1 resize-none border-0 bg-transparent focus:ring-0 focus:ring-offset-0 text-xs p-2"
              />
            </div>
          </div>
        </div>
      </div>
      
      {/* Tool Selection */}
      <div className="mb-6">
        <ToolSelector
          selectedTools={selectedTools}
          onToolsChange={setSelectedTools}
        />
      </div>
      
      {hasContent && (
        <Button 
          className="mt-auto" 
          onClick={handleSubmit}
          disabled={isProcessing}
        >
          {isProcessing ? 'Analyzing...' : 'Analyze Case'}
        </Button>
      )}
    </div>
  );
}
