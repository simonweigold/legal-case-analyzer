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

export interface User {
  id: string;
  name: string;
  email: string;
  avatar?: string;
  joinedDate: string;
}

export interface ConversationHistory {
  id: string;
  title: string;
  lastMessage: string;
  lastUpdated: string;
  messageCount: number;
  category: 'contract' | 'litigation' | 'compliance' | 'research' | 'other';
}
