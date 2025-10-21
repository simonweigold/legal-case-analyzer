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
    <div className="w-80 grid grid-rows-[1fr_6fr_1fr] border-r border-border h-full">
      {/* Top decorative / spacer */}
      <div className="diagonal-lines" />
      {/* Controlled height area for tools - exactly 1/3 of grid */}
      <div className="p-4 border-t border-b border-border bg-white overflow-hidden">
        <ToolSelector
          selectedTools={selectedTools}
          onToolsChange={setSelectedTools}
          className="h-full"
        />
      </div>
      {/* Bottom decorative / spacer */}
      <div className="diagonal-lines" />
    </div>
  );
}
