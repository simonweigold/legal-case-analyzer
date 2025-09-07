/**
 * Hook for managing conversations with Supabase backend.
 */
import { useState, useEffect } from 'react';
import { useAuth } from '../contexts/AuthContext';
import { supabase } from '../lib/supabase';
import type { Conversation, Message } from '../lib/supabase';

interface UseConversationsResult {
  conversations: Conversation[];
  loading: boolean;
  error: string | null;
  createConversation: (title?: string) => Promise<Conversation | null>;
  deleteConversation: (id: string) => Promise<boolean>;
  refreshConversations: () => Promise<void>;
}

export const useConversations = (): UseConversationsResult => {
  const [conversations, setConversations] = useState<Conversation[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const { user, session } = useAuth();

  const fetchConversations = async () => {
    if (!user || !session) {
      setConversations([]);
      setLoading(false);
      return;
    }

    try {
      setLoading(true);
      setError(null);

      const { data, error: fetchError } = await supabase
        .from('conversations')
        .select('*')
        .eq('user_id', user.id)
        .order('updated_at', { ascending: false });

      if (fetchError) {
        throw fetchError;
      }

      setConversations(data || []);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to fetch conversations');
    } finally {
      setLoading(false);
    }
  };

  const createConversation = async (title?: string): Promise<Conversation | null> => {
    if (!user || !session) {
      setError('User not authenticated');
      return null;
    }

    try {
      setError(null);

      const newConversation = {
        user_id: user.id,
        title: title || `Conversation ${new Date().toLocaleDateString()}`,
        metadata: {},
      };

      const { data, error: createError } = await supabase
        .from('conversations')
        .insert([newConversation])
        .select()
        .single();

      if (createError) {
        throw createError;
      }

      // Add to local state
      setConversations(prev => [data, ...prev]);
      return data;
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to create conversation');
      return null;
    }
  };

  const deleteConversation = async (id: string): Promise<boolean> => {
    if (!user || !session) {
      setError('User not authenticated');
      return false;
    }

    try {
      setError(null);

      const { error: deleteError } = await supabase
        .from('conversations')
        .delete()
        .eq('id', id)
        .eq('user_id', user.id);

      if (deleteError) {
        throw deleteError;
      }

      // Remove from local state
      setConversations(prev => prev.filter(conv => conv.id !== id));
      return true;
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to delete conversation');
      return false;
    }
  };

  const refreshConversations = async () => {
    await fetchConversations();
  };

  useEffect(() => {
    fetchConversations();
  }, [user, session]);

  return {
    conversations,
    loading,
    error,
    createConversation,
    deleteConversation,
    refreshConversations,
  };
};

interface UseMessagesResult {
  messages: Message[];
  loading: boolean;
  error: string | null;
  sendMessage: (conversationId: string, content: string) => Promise<boolean>;
  refreshMessages: () => Promise<void>;
}

export const useMessages = (conversationId: string | null): UseMessagesResult => {
  const [messages, setMessages] = useState<Message[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const { session } = useAuth();

  const fetchMessages = async () => {
    if (!conversationId || !session) {
      setMessages([]);
      return;
    }

    try {
      setLoading(true);
      setError(null);

      const { data, error: fetchError } = await supabase
        .from('messages')
        .select('*')
        .eq('conversation_id', conversationId)
        .order('created_at', { ascending: true });

      if (fetchError) {
        throw fetchError;
      }

      setMessages(data || []);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to fetch messages');
    } finally {
      setLoading(false);
    }
  };

  const sendMessage = async (conversationId: string, content: string): Promise<boolean> => {
    if (!session) {
      setError('User not authenticated');
      return false;
    }

    try {
      setError(null);

      // Add user message to local state immediately for optimistic update
      const userMessage: Message = {
        id: `temp-${Date.now()}`,
        conversation_id: conversationId,
        role: 'user',
        content,
        metadata: {},
        created_at: new Date().toISOString(),
      };

      setMessages(prev => [...prev, userMessage]);

      // Send to backend API (which will handle both Supabase storage and AI response)
      const apiBase = (import.meta as any).env?.BUN_PUBLIC_API_BASE || "http://localhost:8001";
      const response = await fetch(`${apiBase}/conversations/${conversationId}/chat`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${session.access_token}`,
        },
        body: JSON.stringify({
          message: content,
          conversation_id: conversationId,
        }),
      });

      if (!response.ok) {
        throw new Error('Failed to send message');
      }

      // Refresh messages to get the actual stored messages from backend
      await fetchMessages();
      return true;
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to send message');
      // Remove optimistic update on error
      setMessages(prev => prev.filter(msg => !msg.id.startsWith('temp-')));
      return false;
    }
  };

  const refreshMessages = async () => {
    await fetchMessages();
  };

  useEffect(() => {
    fetchMessages();
  }, [conversationId, session]);

  return {
    messages,
    loading,
    error,
    sendMessage,
    refreshMessages,
  };
};
