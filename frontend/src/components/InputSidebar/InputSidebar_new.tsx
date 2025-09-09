// components/InputSidebar/InputSidebar.tsx
import React, { useState, useRef } from 'react';
import { Upload, FileText, FileUp, X, Send, AlertCircle } from 'lucide-react';
import { cn } from '../../lib/utils';

export interface InputSidebarProps {
  open: boolean;
  onToggle: () => void;
  onTextSubmit: (text: string, source: 'text' | 'pdf', filename?: string) => void;
  isProcessing?: boolean;
}

interface UploadedFile {
  id: string;
  name: string;
  size: number;
  text?: string;
  status: 'uploading' | 'processing' | 'ready' | 'error';
  error?: string;
}

export function InputSidebar({ open, onToggle, onTextSubmit, isProcessing = false }: InputSidebarProps) {
  const [textInput, setTextInput] = useState('');
  const [uploadedFiles, setUploadedFiles] = useState<UploadedFile[]>([]);
  const [dragOver, setDragOver] = useState(false);
  const fileInputRef = useRef<HTMLInputElement>(null);

  const handleTextSubmit = () => {
    if (textInput.trim()) {
      onTextSubmit(textInput.trim(), 'text');
      setTextInput('');
    }
  };

  const handleFileUpload = async (files: FileList) => {
    const file = files[0];
    if (!file) return;

    const fileId = Date.now().toString();
    const newFile: UploadedFile = {
      id: fileId,
      name: file.name,
      size: file.size,
      status: 'uploading',
    };

    setUploadedFiles(prev => [...prev, newFile]);

    try {
      if (file.type === 'application/pdf') {
        // Handle PDF upload (you'll need to implement PDF text extraction)
        setUploadedFiles(prev =>
          prev.map(f => f.id === fileId ? { ...f, status: 'processing' } : f)
        );
        
        // Simulate PDF processing
        setTimeout(() => {
          const extractedText = `Extracted text from ${file.name}`;
          setUploadedFiles(prev =>
            prev.map(f => f.id === fileId ? { ...f, status: 'ready', text: extractedText } : f)
          );
        }, 2000);
      } else if (file.type === 'text/plain') {
        const text = await file.text();
        setUploadedFiles(prev =>
          prev.map(f => f.id === fileId ? { ...f, status: 'ready', text } : f)
        );
      } else {
        throw new Error('Unsupported file type');
      }
    } catch (error) {
      setUploadedFiles(prev =>
        prev.map(f => f.id === fileId ? { 
          ...f, 
          status: 'error', 
          error: error instanceof Error ? error.message : 'Upload failed' 
        } : f)
      );
    }
  };

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    setDragOver(false);
    handleFileUpload(e.dataTransfer.files);
  };

  const removeFile = (fileId: string) => {
    setUploadedFiles(prev => prev.filter(f => f.id !== fileId));
  };

  const submitFile = (file: UploadedFile) => {
    if (file.text && file.status === 'ready') {
      onTextSubmit(file.text, 'pdf', file.name);
      removeFile(file.id);
    }
  };

  const formatFileSize = (bytes: number) => {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
  };

  return (
    <div className="w-80 h-full flex flex-col bg-sidebar border-r border-sidebar-border">
      {/* Header */}
      <div className="p-4 border-b border-sidebar-border">
        <h2 className="text-lg font-semibold text-sidebar-foreground">Input & Documents</h2>
        <p className="text-sm text-sidebar-foreground/70 mt-1">
          Enter text or upload documents to analyze
        </p>
      </div>

      {/* Content */}
      <div className="flex-1 overflow-y-auto p-4 space-y-6">
        {/* Text Input Section */}
        <div className="space-y-3">
          <h3 className="text-sm font-medium text-sidebar-foreground">Direct Text Input</h3>
          <div className="space-y-3">
            <textarea
              value={textInput}
              onChange={(e) => setTextInput(e.target.value)}
              placeholder="Enter legal text to analyze..."
              className="textarea w-full min-h-[120px] bg-sidebar-accent text-sidebar-accent-foreground"
              disabled={isProcessing}
            />
            <button
              onClick={handleTextSubmit}
              disabled={!textInput.trim() || isProcessing}
              className={cn(
                "btn btn-primary w-full h-10",
                (!textInput.trim() || isProcessing) && "opacity-50 cursor-not-allowed"
              )}
            >
              <Send className="w-4 h-4 mr-2" />
              {isProcessing ? 'Processing...' : 'Analyze Text'}
            </button>
          </div>
        </div>

        {/* File Upload Section */}
        <div className="space-y-3">
          <h3 className="text-sm font-medium text-sidebar-foreground">Document Upload</h3>
          
          {/* Drop Zone */}
          <div
            onDrop={handleDrop}
            onDragOver={(e) => {
              e.preventDefault();
              setDragOver(true);
            }}
            onDragLeave={() => setDragOver(false)}
            onClick={() => fileInputRef.current?.click()}
            className={cn(
              "border-2 border-dashed rounded-lg p-6 text-center cursor-pointer transition-colors",
              dragOver 
                ? "border-sidebar-primary bg-sidebar-accent/50" 
                : "border-sidebar-border hover:border-sidebar-primary/50 hover:bg-sidebar-accent/20"
            )}
          >
            <Upload className="w-8 h-8 mx-auto mb-2 text-sidebar-foreground/50" />
            <p className="text-sm text-sidebar-foreground/70">
              Drag & drop files here, or click to select
            </p>
            <p className="text-xs text-sidebar-foreground/50 mt-1">
              Supports PDF and text files
            </p>
          </div>

          <input
            ref={fileInputRef}
            type="file"
            accept=".pdf,.txt"
            onChange={(e) => e.target.files && handleFileUpload(e.target.files)}
            className="hidden"
          />
        </div>

        {/* Uploaded Files */}
        {uploadedFiles.length > 0 && (
          <div className="space-y-3">
            <h3 className="text-sm font-medium text-sidebar-foreground">Uploaded Files</h3>
            <div className="space-y-2">
              {uploadedFiles.map((file) => (
                <div
                  key={file.id}
                  className="p-3 bg-sidebar-accent rounded-lg border border-sidebar-border"
                >
                  <div className="flex items-start justify-between">
                    <div className="flex items-start space-x-2 flex-1 min-w-0">
                      <FileText className="w-4 h-4 mt-0.5 text-sidebar-foreground/50 flex-shrink-0" />
                      <div className="min-w-0 flex-1">
                        <p className="text-sm font-medium text-sidebar-accent-foreground truncate">
                          {file.name}
                        </p>
                        <p className="text-xs text-sidebar-foreground/60">
                          {formatFileSize(file.size)}
                        </p>
                      </div>
                    </div>
                    <button
                      onClick={() => removeFile(file.id)}
                      className="btn btn-ghost h-6 w-6 p-0 text-sidebar-foreground/50 hover:text-sidebar-foreground"
                    >
                      <X className="w-3 h-3" />
                    </button>
                  </div>

                  {/* Status */}
                  <div className="mt-2">
                    {file.status === 'uploading' && (
                      <div className="flex items-center space-x-2">
                        <div className="w-full bg-sidebar-border rounded-full h-1.5">
                          <div className="bg-sidebar-primary h-1.5 rounded-full animate-pulse w-1/3"></div>
                        </div>
                        <span className="text-xs text-sidebar-foreground/60">Uploading...</span>
                      </div>
                    )}
                    
                    {file.status === 'processing' && (
                      <div className="flex items-center space-x-2">
                        <div className="w-full bg-sidebar-border rounded-full h-1.5">
                          <div className="bg-sidebar-primary h-1.5 rounded-full animate-pulse w-2/3"></div>
                        </div>
                        <span className="text-xs text-sidebar-foreground/60">Processing...</span>
                      </div>
                    )}
                    
                    {file.status === 'ready' && (
                      <button
                        onClick={() => submitFile(file)}
                        disabled={isProcessing}
                        className={cn(
                          "btn btn-primary w-full h-8 text-xs",
                          isProcessing && "opacity-50 cursor-not-allowed"
                        )}
                      >
                        <FileUp className="w-3 h-3 mr-1" />
                        Analyze Document
                      </button>
                    )}
                    
                    {file.status === 'error' && (
                      <div className="flex items-center space-x-2 text-destructive">
                        <AlertCircle className="w-3 h-3" />
                        <span className="text-xs">{file.error}</span>
                      </div>
                    )}
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
