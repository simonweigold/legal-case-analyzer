// components/Sidebar/Sidebar.tsx
import React, { useState, useEffect } from 'react';
import { X, Search, MessageCircle, User, Plus, Trash2, MoreVertical } from "lucide-react";
import { Button } from "../ui/button";
import { Input } from "../ui/input";
import { ScrollArea } from "../ui/scroll-area";
import { useAuth } from '../../contexts/AuthContext';
import { AuthModal } from '../Auth/AuthModal';

export interface SidebarProps {
  open: boolean;
  onToggle: () => void;
  sessionId: string | null;
  onClearSession: () => void;
  isStreaming: boolean;
  loading: boolean;
  conversations: any[];
  onLoadConversation: (conversationId: string) => void;
  onDeleteConversation: (conversationId: string) => void;
}

interface Conversation {
  id: string;
  title: string;
  lastMessage: string;
  timestamp: string;
}

export function Sidebar({
  open,
  onToggle,
  sessionId,
  onClearSession,
  isStreaming,
  loading,
  conversations,
  onLoadConversation,
  onDeleteConversation
}: SidebarProps) {
  const { user, isAuthenticated, logout } = useAuth();
  const [isOpen, setIsOpen] = useState(true);
  const [searchQuery, setSearchQuery] = useState("");
  const [authModalOpen, setAuthModalOpen] = useState(false);
  const [authMode, setAuthMode] = useState<'login' | 'register'>('login');
  const [openDropdownId, setOpenDropdownId] = useState<string | null>(null);

  const filteredConversations = conversations
    .filter(
      (conv) =>
        conv.title
          ?.toLowerCase()
          .includes(searchQuery.toLowerCase()) ||
        conv.lastMessage
          ?.toLowerCase()
          .includes(searchQuery.toLowerCase()),
    )
    .sort((a, b) => {
      // Sort by updatedAt in descending order (most recent first)
      const dateA = new Date(a.updatedAt || a.timestamp || 0).getTime();
      const dateB = new Date(b.updatedAt || b.timestamp || 0).getTime();
      return dateB - dateA;
    });

  const handleDeleteConversation = (conversationId: string, e: React.MouseEvent) => {
    e.stopPropagation(); // Prevent triggering the conversation click
    onDeleteConversation(conversationId);
    setOpenDropdownId(null);
  };

  const toggleDropdown = (conversationId: string, e: React.MouseEvent) => {
    e.stopPropagation(); // Prevent triggering the conversation click
    setOpenDropdownId(openDropdownId === conversationId ? null : conversationId);
  };

  // Close dropdown when clicking outside
  useEffect(() => {
    const handleClickOutside = () => {
      setOpenDropdownId(null);
    };

    if (openDropdownId) {
      document.addEventListener('click', handleClickOutside);
      return () => document.removeEventListener('click', handleClickOutside);
    }
  }, [openDropdownId]);

  const handleLogout = async () => {
    // Clear the current session first
    onClearSession();
    // Then logout the user - this should trigger conversation clearing in parent component
    await logout();
  };

  // Clear conversations when user logs out (becomes unauthenticated)
  useEffect(() => {
    if (!isAuthenticated && conversations.length > 0) {
      // If user is not authenticated but still has conversations, clear the session
      // This helps ensure UI state is consistent
      onClearSession();
    }
  }, [isAuthenticated, conversations.length, onClearSession]);

  if (!isOpen) {
    return (
      <Button
        variant="outline"
        size="sm"
        className="fixed top-4 right-4 z-10"
        onClick={() => setIsOpen(true)}
      >
        <MessageCircle className="w-4 h-4" />
      </Button>
    );
  }

  return (
    <div className="w-80 border-l border-border bg-background flex flex-col">
      <div className="p-4 border-b border-border diagonal-lines">
        <div className="flex items-center justify-between mb-4">
          <h3>Conversations</h3>
          <Button
            variant="ghost"
            size="sm"
            onClick={() => setIsOpen(false)}
          >
            <X className="w-4 h-4" />
          </Button>
        </div>

        <div className="relative">
          <div className="relative">
            <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 w-4 h-4 text-muted-foreground" />
            <Input
              placeholder="Search Conversations"
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="pl-10"
            />
          </div>
          <div className="relative">
            <Button
              onClick={onClearSession}
              variant="outline"
              size="sm"
              className="w-full flex items-center gap-2 justify-center mt-3 bg-white hover:bg-blue-50 hover:border-blue-200"
              disabled={isStreaming || loading}
            >
              <Plus className="w-4 h-4" />
              New Chat
            </Button>
          </div>
        </div>
      </div>

      <ScrollArea className="flex-1">
        <div className="p-4 space-y-3">
          {filteredConversations.length > 0 ? (
            filteredConversations.map((conversation) => (
              <div
                key={conversation.id}
                className="relative p-3 rounded-lg border border-border hover:bg-muted/50 cursor-pointer transition-colors"
                onClick={() => onLoadConversation(conversation.id)}
              >
                <div className="flex items-start justify-between">
                  <div className="flex-1 min-w-0">
                    <h4 className="mb-1 truncate">
                      {conversation.title || 'Legal Analysis Session'}
                    </h4>
                    <p className="text-sm text-muted-foreground mb-2 line-clamp-2">
                      {conversation.lastMessage || 'No messages yet'}
                    </p>
                    <p className="text-xs text-muted-foreground">
                      {conversation.updatedAt ? new Date(conversation.updatedAt).toLocaleDateString() : 'Just now'}
                    </p>
                  </div>
                  
                  {/* Dropdown menu button */}
                  <div className="relative">
                    <Button
                      variant="ghost"
                      size="sm"
                      onClick={(e) => toggleDropdown(conversation.id, e)}
                      className="p-1 h-6 w-6 text-muted-foreground hover:text-foreground"
                    >
                      <MoreVertical className="w-4 h-4" />
                    </Button>
                    
                    {/* Dropdown menu */}
                    {openDropdownId === conversation.id && (
                      <div className="absolute right-0 top-full mt-1 bg-white border border-border rounded-md shadow-lg z-10 min-w-[120px]">
                        <button
                          onClick={(e) => handleDeleteConversation(conversation.id, e)}
                          className="w-full px-3 py-2 text-left text-sm text-red-600 hover:bg-red-50 flex items-center gap-2"
                        >
                          <Trash2 className="w-3 h-3" />
                          Delete
                        </button>
                      </div>
                    )}
                  </div>
                </div>
              </div>
            ))
          ) : (
            <p className="text-sm text-muted-foreground text-center py-8">
              No conversations found
            </p>
          )}
        </div>
      </ScrollArea>

      {isAuthenticated && user ? (
        <div className="border-t border-border p-4 bg-muted/30 diagonal-lines">
          <div className="flex items-center gap-2 p-2 rounded-lg bg-white border">
            <div className="w-8 h-8 rounded-full bg-background flex items-center justify-center">
              <User className="w-4 h-4" />
            </div>
            <div className="flex-1 min-w-0">
              <p className="text-sm truncate">{user.email}</p>
            </div>
            <Button variant="ghost" size="sm" onClick={handleLogout}>
              <X className="w-4 h-4 hover:text-red-500" />
            </Button>
          </div>
        </div>
      ) : (
        <div className="border-t border-border p-4 bg-muted/30 diagonal-lines">
          <div className="space-y-3">
            <p className="text-sm text-muted-foreground mb-3">Sign in to save your conversations</p>
            <div className="grid grid-cols-2 gap-4">
              <div className="grid bg-white hover:bg-blue-50 hover:border-blue-200">
                <Button 
                  variant="outline"
                  size="sm"
                  onClick={() => {
                    setAuthMode('login');
                    setAuthModalOpen(true);
                  }}
                  className="text-xs"
                >
                  Sign In
                </Button>
              </div>
              <div className="grid bg-white hover:bg-blue-50 hover:border-blue-200">
                <Button 
                  variant="outline"
                  size="sm"
                  onClick={() => {
                    setAuthMode('register');
                    setAuthModalOpen(true);
                  }}
                  className="text-xs"
                >
                  Sign Up
                </Button>
              </div>
            </div>
          </div>
        </div>
      )}

      <AuthModal
        open={authModalOpen}
        onClose={() => setAuthModalOpen(false)}
        mode={authMode}
        onModeChange={setAuthMode}
      />
    </div>
  );
}
