// types/index.ts
export interface ApiError {
  message: string;
  status?: number;
}

export interface ChatResponse {
  response: string;
  session_id: string;
}

export interface StreamEvent {
  type: 'token' | 'tool' | 'tool_result' | 'error';
  content?: string;
  error?: string;
  done?: boolean;
}

export interface AppConfig {
  apiBase: string;
  title: string;
  description: string;
}

// types/index.ts
// User types
export interface User {
  id: string;
  email: string;
  name?: string;
  avatar?: string;
  is_active: boolean;
  is_superuser: boolean;
  is_verified: boolean;
}

// Conversation types
export interface ConversationHistory {
  id: string;
  user_id: string;
  title: string;
  created_at: string;
  updated_at: string;
  category?: string;
  is_active: boolean;
  messageCount?: number;
  lastMessage?: string;
  lastUpdated?: string;
}

// Message types
export interface Message {
  id: string;
  conversation_id: string;
  content: string;
  role: 'user' | 'assistant' | 'tool';
  timestamp: string;
  metadata?: Record<string, any>;
}

// Chat types
export interface ChatMessage {
  id: string;
  content: string;
  role: 'user' | 'assistant' | 'tool';
  timestamp: Date;
  isStreaming?: boolean;
}

// API Request/Response types
export interface ChatRequest {
  message: string;
  conversation_id?: string;
  stream?: boolean;
}

export interface ChatResponse {
  response: string;
  conversation_id: string;
  message_id: string;
}

// Analysis types
export interface AnalysisResult {
  summary: string;
  keyPoints: string[];
  legalIssues: string[];
  recommendations: string[];
  confidence: number;
  jurisdiction?: string;
  caseType?: string;
}

// Theme types
export interface Theme {
  mode: 'light' | 'dark';
}

// Category information
export interface CategoryInfo {
  label: string;
  color: string;
  icon?: string;
}
