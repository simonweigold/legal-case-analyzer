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
    <div className="w-full h-full flex flex-col bg-light">
      {/* Header */}
      <div className="p-6 border-b border-gray-dark/10">
        <h2 className="text-h2 text-dark">Case Input</h2>
        <p className="text-small text-gray-dark mt-1">
          Enter legal text or upload documents for analysis
        </p>
      </div>

      {/* Content */}
      <div className="flex-1 overflow-y-auto p-6 space-y-8">
        {/* Text Input Section */}
        <div className="space-y-4">
          <h3 className="text-body font-medium text-dark">Legal Text Analysis</h3>
          <div className="space-y-4">
            <textarea
              value={textInput}
              onChange={(e) => setTextInput(e.target.value)}
              placeholder="Enter legal case details, statutes, or court documents to analyze..."
              className="causa-textarea causa-input-tinted w-full min-h-[120px]"
              disabled={isProcessing}
            />
            <button
              onClick={handleTextSubmit}
              disabled={!textInput.trim() || isProcessing}
              className={cn(
                "causa-btn causa-btn-primary w-full",
                (!textInput.trim() || isProcessing) && "opacity-50 cursor-not-allowed"
              )}
            >
              <Send className="w-4 h-4 mr-2" />
              {isProcessing ? 'Analyzing...' : 'Analyze Legal Text'}
            </button>
          </div>
        </div>

        {/* File Upload Section */}
        <div className="space-y-4">
          <h3 className="text-body font-medium text-dark">Document Upload</h3>
          
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
              "causa-upload-zone py-8",
              dragOver && "border-brand"
            )}
          >
            <Upload className="w-8 h-8 mx-auto mb-3 text-gray" />
            <p className="text-body text-dark">
              Drag & drop legal documents here
            </p>
            <p className="text-small text-gray mt-1">
              or click to browse files
            </p>
            <p className="text-small text-gray mt-2">
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
          <div className="space-y-4">
            <h3 className="text-body font-medium text-dark">Uploaded Documents</h3>
            <div className="space-y-3">
              {uploadedFiles.map((file) => (
                <div
                  key={file.id}
                  className="p-4 bg-white rounded-causa border border-gray/20"
                >
                  <div className="flex items-start justify-between">
                    <div className="flex items-start space-x-3 flex-1 min-w-0">
                      <FileText className="w-5 h-5 mt-0.5 text-gray flex-shrink-0" />
                      <div className="min-w-0 flex-1">
                        <p className="text-body font-medium text-dark truncate">
                          {file.name}
                        </p>
                        <p className="text-small text-gray">
                          {formatFileSize(file.size)}
                        </p>
                      </div>
                    </div>
                    <button
                      onClick={() => removeFile(file.id)}
                      className="p-1 text-gray hover:text-dark transition-colors"
                    >
                      <X className="w-4 h-4" />
                    </button>
                  </div>

                  {/* Status */}
                  <div className="mt-3">
                    {file.status === 'uploading' && (
                      <div className="flex items-center space-x-3">
                        <div className="w-full bg-gray/20 rounded-full h-2">
                          <div className="bg-brand h-2 rounded-full animate-pulse w-1/3"></div>
                        </div>
                        <span className="text-small text-gray">Uploading...</span>
                      </div>
                    )}
                    
                    {file.status === 'processing' && (
                      <div className="flex items-center space-x-3">
                        <div className="w-full bg-gray/20 rounded-full h-2">
                          <div className="bg-brand h-2 rounded-full animate-pulse w-2/3"></div>
                        </div>
                        <span className="text-small text-gray">Processing...</span>
                      </div>
                    )}
                    
                    {file.status === 'ready' && (
                      <button
                        onClick={() => submitFile(file)}
                        disabled={isProcessing}
                        className={cn(
                          "causa-btn causa-btn-primary w-full",
                          isProcessing && "opacity-50 cursor-not-allowed"
                        )}
                      >
                        <FileUp className="w-4 h-4 mr-2" />
                        Analyze Document
                      </button>
                    )}
                    
                    {file.status === 'error' && (
                      <div className="flex items-center space-x-2 text-red-500">
                        <AlertCircle className="w-4 h-4" />
                        <span className="text-small">{file.error}</span>
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
