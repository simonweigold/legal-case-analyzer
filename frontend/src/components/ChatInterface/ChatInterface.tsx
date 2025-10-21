// components/ChatInterface/ChatInterface.tsx
import React, { useState, useRef, useEffect } from 'react';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
import { Textarea } from '../ui/textarea';
import type { ChatState } from '../../hooks/useChat';
import { Upload, FileText, Type } from 'lucide-react';
import { Button } from '../ui/button';

export interface ChatActions {
  setInput: (value: string) => void;
  sendMessage: () => void;
  clearSession: () => void;
  stopGeneration: () => void;
}

export interface ChatInterfaceProps {
  state: ChatState & { input: string };
  actions: ChatActions;
  inputRef: React.RefObject<HTMLInputElement | HTMLTextAreaElement | null>;
  onInitialSubmit: (text: string, source: 'text' | 'pdf', filename?: string) => void;
}

export function ChatInterface({ state, actions, inputRef, onInitialSubmit }: ChatInterfaceProps) {
  const initialMode = state.messages.length === 0; // gating condition
  // Local state for initial analysis input
  const [showChoices, setShowChoices] = useState(false);
  const [pastedText, setPastedText] = useState('');
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [customInstructions, setCustomInstructions] = useState('');
  const fileInputRef = useRef<HTMLInputElement | null>(null);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  // Auto-scroll to bottom when messages change or streaming
  useEffect(() => {
    if (messagesEndRef.current) {
      messagesEndRef.current.scrollIntoView({ behavior: 'smooth' });
    }
  }, [state.messages, state.isStreaming, state.isLoading]);

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;
    if (!(file.type === 'application/pdf' || file.name.toLowerCase().endsWith('.txt'))) return;
    setSelectedFile(file);
  };

  const handleInitialAnalyze = () => {
    const instructions = customInstructions.trim() || 'Please analyze this legal document.\n\nLegal Document:';

    if (selectedFile) {
      if (selectedFile.type === 'application/pdf') {
        onInitialSubmit(`Document: ${selectedFile.name}`, 'pdf', selectedFile.name);
        setSelectedFile(null);
        setPastedText('');
        setCustomInstructions('');
      } else if (selectedFile.name.toLowerCase().endsWith('.txt')) {
        const reader = new FileReader();
        reader.onload = () => {
          const text = String(reader.result || '').trim();
          if (text) {
            const formattedText = `${instructions}\n\n${text}`;
            onInitialSubmit(formattedText, 'text', selectedFile.name);
          }
          setSelectedFile(null);
          setPastedText('');
          setCustomInstructions('');
        };
        reader.readAsText(selectedFile);
      }
      return;
    }
    if (pastedText.trim()) {
      const formattedText = `${instructions}\n\n${pastedText.trim()}`;
      onInitialSubmit(formattedText, 'text');
      setPastedText('');
      setCustomInstructions('');
    }
  };

  return (
    <div className="flex-1 flex flex-col">
      {/* Messages area - scrollable */}
      <div className="flex-1 overflow-y-auto p-8 pb-4">
        <div className="max-w-4xl mx-auto space-y-6">
          {state.messages.length === 0 && !state.isLoading ? (
            <div className="mt-16 flex flex-col items-center justify-center h-full min-h-[400px] text-center">
              <div className="space-y-4">
                <h1 className="h1 text-4xl mb-12">Welcome to CLERK</h1>
                <p className="text-lg text-black/50 leading-relaxed max-w-md">
                  Start by providing a court decision (PDF, TXT, or paste the text). After the initial analysis you can continue the conversation.
                </p>
              </div>
            </div>
          ) : (
            <>
              {state.messages.map((message, index) => (
                <div key={index}>
                  {message.role === 'user' && (
                    <div className="bg-blue-50 border border-blue-200 rounded-lg p-6">
                      <p className="leading-relaxed whitespace-pre-wrap">{message.content}</p>
                    </div>
                  )}
                  {message.role === 'assistant' && (
                    <div className="space-y-4">
                      <ReactMarkdown
                        remarkPlugins={[remarkGfm]}
                        className="prose prose-sm max-w-none prose-headings:font-serif prose-h1:text-3xl prose-h2:text-2xl prose-h3:text-xl prose-p:leading-relaxed prose-pre:bg-gray-900 prose-pre:text-gray-100 prose-code:text-pink-600"
                        components={{
                          a: (props: React.AnchorHTMLAttributes<HTMLAnchorElement>) => (
                            <a {...props} target="_blank" rel="noopener noreferrer" className="text-blue-600 underline" />
                          ),
                          table: (props: React.HTMLAttributes<HTMLTableElement>) => (
                            <div className="overflow-x-auto"><table {...props} /></div>
                          )
                        }}
                      >
                        {message.content}
                      </ReactMarkdown>
                    </div>
                  )}
                  {message.role === 'tool' && (
                    <div className="bg-gray-50 border border-gray-200 rounded-lg p-6">
                      <div className="flex items-start gap-3">
                        <div className="flex-shrink-0">
                          <div className="w-6 h-6 bg-gray-500 text-white rounded text-xs flex items-center justify-center font-medium">
                            T
                          </div>
                        </div>
                        <div className="flex-1">
                          <p className="text-sm font-medium text-gray-700 mb-1">Tool Usage</p>
                          <p className="text-sm leading-relaxed text-gray-600">{message.content}</p>
                        </div>
                      </div>
                    </div>
                  )}
                </div>
              ))}

              {(state.isLoading || state.isStreaming) && (
                <div className="flex justify-center py-6">
                  <div className="flex space-x-1">
                    <div className="w-2 h-2 bg-blue-500 rounded-full animate-pulse-dot-1"></div>
                    <div className="w-2 h-2 bg-blue-500 rounded-full animate-pulse-dot-2"></div>
                    <div className="w-2 h-2 bg-blue-500 rounded-full animate-pulse-dot-3"></div>
                  </div>
                </div>
              )}
              
              {/* Invisible element to scroll to */}
              <div ref={messagesEndRef} />
            </>
          )}
        </div>
      </div>

      {/* Fixed bottom area */}
      <div className="flex-shrink-0 p-8 pt-4 border-t border-border bg-background">
        <div className="max-w-4xl mx-auto">
          {initialMode ? (
            <div className="relative border-2 border-dashed rounded-lg p-6 bg-muted/30 hover:bg-muted/50 transition-colors flowing-blue-bg">
              {!showChoices && (
                <button
                  className="w-full h-full flex flex-col items-center justify-center gap-2 text-muted-foreground"
                  onClick={() => setShowChoices(true)}
                >
                  <Upload className="w-8 h-8" />
                  <span className="text-sm">Click to add a court decision (PDF, TXT, or paste text)</span>
                </button>
              )}
              {showChoices && (
                <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                  {/* Custom Instructions - spans full width and appears first */}
                  <div className="md:col-span-2 flex flex-col gap-3">
                    <label className="text-sm font-medium">Custom Analysis Instructions</label>
                    <Textarea
                      placeholder="Enter specific instructions for how you want the legal document analyzed"
                      value={customInstructions}
                      onChange={(e) => setCustomInstructions(e.target.value)}
                      className="min-h-[80px] resize-none border border-border bg-white hover:border-primary hover:bg-primary/5 transition text-sm"
                    />
                  </div>
                  
                  {/* File chooser */}
                  <div className="flex flex-col gap-3">
                    <label className="text-sm font-medium flex items-center gap-2"><FileText className="w-4 h-4" /> Upload File</label>
                    <div
                      onClick={() => fileInputRef.current?.click()}
                      className="group border border-border rounded-lg p-4 text-center cursor-pointer bg-white hover:border-primary hover:bg-primary/5 transition min-h-[160px]"
                    >
                      {selectedFile ? (
                        <div className="space-y-2">
                          <p className="text-sm font-medium break-all">{selectedFile.name}</p>
                          <Button
                            size="sm"
                            variant="outline"
                            onClick={(e) => { e.stopPropagation(); setSelectedFile(null); }}
                          >Remove</Button>
                        </div>
                      ) : (
                        <div className="flex flex-col items-center gap-2 text-xs text-muted-foreground">
                          <Upload className="w-6 h-6" />
                          <span>PDF or TXT</span>
                          <span className="text-[10px]">Click to choose</span>
                        </div>
                      )}
                      <input
                        ref={fileInputRef}
                        type="file"
                        accept=".pdf,.txt,text/plain,application/pdf"
                        onChange={handleFileChange}
                        className="hidden"
                      />
                    </div>
                  </div>
                  {/* Paste text */}
                  <div className="flex flex-col gap-3">
                    <label className="text-sm font-medium flex items-center gap-2"><Type className="w-4 h-4" /> Paste Text</label>
                    <Textarea
                      placeholder="Paste the full text of the decision here..."
                      value={pastedText}
                      onChange={(e) => setPastedText(e.target.value)}
                      className="min-h-[160px] resize-none border border-border bg-white hover:border-primary hover:bg-primary/5 transition"
                    />
                  </div>
                  
                  <div className="md:col-span-2 flex justify-end gap-3">
                    <Button
                      variant="outline"
                      size="sm"
                      onClick={() => { setShowChoices(false); setSelectedFile(null); setPastedText(''); setCustomInstructions(''); }}
                    >Cancel</Button>
                    <Button
                      size="sm"
                      disabled={!selectedFile && !pastedText.trim()}
                      onClick={handleInitialAnalyze}
                    >Analyze Decision</Button>
                  </div>
                </div>
              )}
            </div>
          ) : (
            <Textarea
              ref={inputRef as React.RefObject<HTMLTextAreaElement>}
              placeholder="Enter follow-up questions or analysis here..."
              value={state.input}
              onChange={(e) => actions.setInput(e.target.value)}
              onKeyDown={(e) => {
                if (e.key === 'Enter' && !e.shiftKey) {
                  e.preventDefault();
                  if (state.input.trim() && !state.isLoading && !state.isStreaming) {
                    actions.sendMessage();
                  }
                }
              }}
              className="min-h-[150px] resize-none flowing-blue-bg flowing-blue-border focus:border-blue-400 focus:ring-2 focus:ring-blue-200 focus:ring-offset-2 transition-all duration-200"
              disabled={state.isLoading || state.isStreaming}
            />
          )}
        </div>
      </div>
    </div>
  );
}
