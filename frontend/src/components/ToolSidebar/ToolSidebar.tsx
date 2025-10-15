// components/ToolSidebar/ToolSidebar.tsx
import React, { useState, useRef } from 'react';
import { Upload, FileText, Type } from 'lucide-react';
import { Button } from '../ui/button';
import { Textarea } from '../ui/textarea';
import { ToolSelector } from './ToolSelector';

export interface ToolSidebarProps {
  open: boolean;
  onToggle: () => void;
  onTextSubmit: (text: string, source: 'text' | 'pdf', filename?: string, tools?: string[]) => void;
  isProcessing?: boolean;
  active?: boolean; // whether initial analysis has been provided
}

export function ToolSidebar({ open, onToggle, onTextSubmit, isProcessing = false, active = true }: ToolSidebarProps) {
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
      {active ? (
        <>
          {/* Tool Selection */}
          <div className="mt-24">
            <ToolSelector selectedTools={selectedTools} onToolsChange={setSelectedTools} />
          </div>
          {hasContent && (
            <Button
              className="mt-auto bg-white border text-black hover:bg-blue-50 hover:border-blue-200"
              onClick={handleSubmit}
              disabled={isProcessing}
            >
              {isProcessing ? 'Analyzing...' : 'Analyze Case'}
            </Button>
          )}
        </>
      ) : (
        <div className="flex flex-col h-full">
          <h2 className="mb-4">Analysis Inputs</h2>
          <div className="text-xs text-muted-foreground bg-white border rounded-md p-4">
            Provide a court decision below to unlock detailed tool inputs.
            Once the initial analysis completes, you can add more documents or paste additional case text here.
          </div>
        </div>
      )}
    </div>
  );
}
