// services/api.ts
import { authService } from './auth';

export interface Conversation {
  id: string;
  user_id: string;
  title: string;
  created_at: string;
  updated_at: string;
  category?: string;
  is_active: boolean;
}

export interface Message {
  id: string;
  conversation_id: string;
  content: string;
  role: 'user' | 'assistant';
  timestamp: string;
  metadata?: Record<string, any>;
}

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

class ApiService {
  private baseUrl = 'http://localhost:8000';

  // Get authorization headers
  private getAuthHeaders(): Record<string, string> {
    return {
      'Content-Type': 'application/json',
      ...authService.getAuthHeaders(),
    };
  }

  // Handle API errors
  private async handleResponse<T>(response: Response): Promise<T> {
    if (!response.ok) {
      if (response.status === 401) {
        authService.clearToken();
        throw new Error('Authentication expired. Please log in again.');
      }
      
      const errorData = await response.json().catch(() => ({}));
      throw new Error(errorData.detail || `HTTP ${response.status}: ${response.statusText}`);
    }
    
    return response.json();
  }

  // Get all conversations for the current user
  async getConversations(): Promise<Conversation[]> {
    const response = await fetch(`${this.baseUrl}/chat/conversations`, {
      headers: this.getAuthHeaders(),
    });
    
    return this.handleResponse<Conversation[]>(response);
  }

  // Get a specific conversation
  async getConversation(conversationId: string): Promise<Conversation> {
    const response = await fetch(`${this.baseUrl}/chat/conversations/${conversationId}`, {
      headers: this.getAuthHeaders(),
    });
    
    return this.handleResponse<Conversation>(response);
  }

  // Get messages for a conversation
  async getMessages(conversationId: string): Promise<Message[]> {
    const response = await fetch(`${this.baseUrl}/chat/conversations/${conversationId}/messages`, {
      headers: this.getAuthHeaders(),
    });
    
    return this.handleResponse<Message[]>(response);
  }

  // Send a chat message
  async sendMessage(data: ChatRequest): Promise<ChatResponse> {
    const response = await fetch(`${this.baseUrl}/chat/`, {
      method: 'POST',
      headers: this.getAuthHeaders(),
      body: JSON.stringify(data),
    });
    
    return this.handleResponse<ChatResponse>(response);
  }

  // Send a streaming chat message
  async sendStreamingMessage(
    data: ChatRequest,
    onChunk: (chunk: string) => void,
    onComplete: (response: ChatResponse) => void,
    onError: (error: Error) => void
  ): Promise<void> {
    try {
      const response = await fetch(`${this.baseUrl}/chat/stream`, {
        method: 'POST',
        headers: this.getAuthHeaders(),
        body: JSON.stringify({ ...data, stream: true }),
      });

      if (!response.ok) {
        if (response.status === 401) {
          authService.clearToken();
          throw new Error('Authentication expired. Please log in again.');
        }
        throw new Error(`HTTP ${response.status}: ${response.statusText}`);
      }

      const reader = response.body?.getReader();
      if (!reader) {
        throw new Error('No response body');
      }

      const decoder = new TextDecoder();
      let buffer = '';

      while (true) {
        const { done, value } = await reader.read();
        if (done) break;

        buffer += decoder.decode(value, { stream: true });
        const lines = buffer.split('\n');
        buffer = lines.pop() || '';

        for (const line of lines) {
          if (line.startsWith('data: ')) {
            const data = line.slice(6);
            if (data === '[DONE]') {
              return;
            }
            try {
              const parsed = JSON.parse(data);
              if (parsed.type === 'chunk') {
                onChunk(parsed.content);
              } else if (parsed.type === 'complete') {
                onComplete(parsed.data);
              }
            } catch (error) {
              console.error('Error parsing streaming data:', error);
            }
          }
        }
      }
    } catch (error) {
      onError(error instanceof Error ? error : new Error('Streaming failed'));
    }
  }

  // Update conversation
  async updateConversation(conversationId: string, data: Partial<Conversation>): Promise<Conversation> {
    const response = await fetch(`${this.baseUrl}/chat/conversations/${conversationId}`, {
      method: 'PATCH',
      headers: this.getAuthHeaders(),
      body: JSON.stringify(data),
    });
    
    return this.handleResponse<Conversation>(response);
  }

  // Delete conversation
  async deleteConversation(conversationId: string): Promise<void> {
    const response = await fetch(`${this.baseUrl}/chat/conversations/${conversationId}`, {
      method: 'DELETE',
      headers: this.getAuthHeaders(),
    });
    
    if (!response.ok) {
      if (response.status === 401) {
        authService.clearToken();
        throw new Error('Authentication expired. Please log in again.');
      }
      throw new Error(`Failed to delete conversation: ${response.statusText}`);
    }
  }

  // Create a new conversation
  async createConversation(title: string, category?: string): Promise<Conversation> {
    const response = await fetch(`${this.baseUrl}/chat/conversations`, {
      method: 'POST',
      headers: this.getAuthHeaders(),
      body: JSON.stringify({ title, category }),
    });
    
    return this.handleResponse<Conversation>(response);
  }
}

export const apiService = new ApiService();
