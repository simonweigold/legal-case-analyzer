// components/Sidebar/Sidebar.tsx
import React, { useState } from 'react';
import { 
  MessageSquare, 
  Plus, 
  Search, 
  LogIn, 
  LogOut, 
  User, 
  MoreVertical, 
  Trash2, 
  Edit,
  Menu,
  RotateCcw
} from 'lucide-react';
import { cn } from '../../lib/utils';
import { useAuth } from '../../contexts/AuthContext';
import { AuthModal } from '../Auth';

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

const formatDate = (dateString: string) => {
  const date = new Date(dateString);
  const now = new Date();
  const diffTime = Math.abs(now.getTime() - date.getTime());
  const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24));
  
  if (diffDays === 1) return 'Today';
  if (diffDays === 2) return 'Yesterday';
  if (diffDays < 7) return `${diffDays} days ago`;
  return date.toLocaleDateString();
};

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
  const [searchQuery, setSearchQuery] = useState('');
  const [authModalOpen, setAuthModalOpen] = useState(false);
  const [authMode, setAuthMode] = useState<'login' | 'register'>('login');
  const [conversationMenuId, setConversationMenuId] = useState<string | null>(null);

  // Filter conversations based on search
  const filteredConversations = conversations.filter(conv => {
    const matchesSearch = conv.title?.toLowerCase().includes(searchQuery.toLowerCase()) ||
                         conv.lastMessage?.toLowerCase().includes(searchQuery.toLowerCase());
    return matchesSearch;
  });

  const handleNewChat = () => {
    onClearSession();
  };

  const handleLoginClick = () => {
    setAuthMode('login');
    setAuthModalOpen(true);
  };

  const handleRegisterClick = () => {
    setAuthMode('register');
    setAuthModalOpen(true);
  };

  const handleLogout = () => {
    logout();
  };

  const handleConversationClick = (conversationId: string) => {
    onLoadConversation(conversationId);
  };

  const handleDeleteConversation = (conversationId: string, e: React.MouseEvent) => {
    e.stopPropagation();
    onDeleteConversation(conversationId);
    setConversationMenuId(null);
  };

  return (
    <div className="w-80 h-full flex flex-col bg-sidebar border-l border-sidebar-border">
      {/* Header */}
      <div className="p-4 border-b border-sidebar-border">
        <div className="flex items-center justify-between mb-4">
          <h2 className="text-lg font-semibold text-sidebar-foreground">Conversations</h2>
          <button
            onClick={handleNewChat}
            disabled={loading || isStreaming}
            className={cn(
              "btn btn-primary h-8 w-8 p-0",
              (loading || isStreaming) && "opacity-50 cursor-not-allowed"
            )}
            title="New Conversation"
          >
            <Plus className="w-4 h-4" />
          </button>
        </div>

        {/* Search */}
        <div className="relative">
          <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 w-4 h-4 text-sidebar-foreground/50" />
          <input
            type="text"
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            placeholder="Search conversations..."
            className="input pl-10 h-9 w-full bg-sidebar-accent text-sidebar-accent-foreground"
          />
        </div>
      </div>

      {/* Conversations List */}
      <div className="flex-1 overflow-y-auto p-2">
        {isAuthenticated ? (
          filteredConversations.length > 0 ? (
            <div className="space-y-1">
              {filteredConversations.map((conversation) => (
                <div
                  key={conversation.id}
                  className={cn(
                    "group relative p-3 rounded-lg cursor-pointer transition-colors",
                    conversation.id === sessionId
                      ? "bg-sidebar-primary text-sidebar-primary-foreground"
                      : "hover:bg-sidebar-accent hover:text-sidebar-accent-foreground"
                  )}
                  onClick={() => handleConversationClick(conversation.id)}
                >
                  <div className="flex items-start justify-between">
                    <div className="flex-1 min-w-0">
                      <h4 className="text-sm font-medium truncate">
                        {conversation.title || 'Untitled Conversation'}
                      </h4>
                      {conversation.lastMessage && (
                        <p className="text-xs text-current/70 truncate mt-1">
                          {conversation.lastMessage}
                        </p>
                      )}
                      <p className="text-xs text-current/50 mt-1">
                        {formatDate(conversation.updatedAt)}
                      </p>
                    </div>
                    
                    <div className="relative">
                      <button
                        onClick={(e) => {
                          e.stopPropagation();
                          setConversationMenuId(
                            conversationMenuId === conversation.id ? null : conversation.id
                          );
                        }}
                        className="opacity-0 group-hover:opacity-100 btn btn-ghost h-6 w-6 p-0 text-current/50 hover:text-current"
                      >
                        <MoreVertical className="w-3 h-3" />
                      </button>
                      
                      {conversationMenuId === conversation.id && (
                        <div className="absolute right-0 top-full mt-1 bg-popover border border-border rounded-md shadow-lg z-10 min-w-[120px]">
                          <button
                            onClick={(e) => handleDeleteConversation(conversation.id, e)}
                            className="w-full px-3 py-2 text-left text-sm hover:bg-accent hover:text-accent-foreground flex items-center text-destructive"
                          >
                            <Trash2 className="w-3 h-3 mr-2" />
                            Delete
                          </button>
                        </div>
                      )}
                    </div>
                  </div>
                </div>
              ))}
            </div>
          ) : (
            <div className="text-center py-8">
              <MessageSquare className="w-12 h-12 text-sidebar-foreground/30 mx-auto mb-3" />
              <p className="text-sm text-sidebar-foreground/60">
                {searchQuery ? 'No conversations found' : 'No conversations yet'}
              </p>
              <p className="text-xs text-sidebar-foreground/40 mt-1">
                Start a new conversation to get started
              </p>
            </div>
          )
        ) : (
          <div className="text-center py-8">
            <User className="w-12 h-12 text-sidebar-foreground/30 mx-auto mb-3" />
            <p className="text-sm text-sidebar-foreground/60 mb-3">
              Sign in to save your conversations
            </p>
            <div className="space-y-2">
              <button
                onClick={handleLoginClick}
                className="btn btn-primary w-full h-8 text-xs"
              >
                <LogIn className="w-3 h-3 mr-1" />
                Sign In
              </button>
              <button
                onClick={handleRegisterClick}
                className="btn btn-outline w-full h-8 text-xs"
              >
                Create Account
              </button>
            </div>
          </div>
        )}
      </div>

      {/* Footer */}
      <div className="p-4 border-t border-sidebar-border">
        {isAuthenticated && user && (
          <div className="flex items-center justify-between mb-3 p-2 bg-sidebar-accent rounded-lg">
            <div className="flex items-center space-x-2 min-w-0">
              <div className="w-6 h-6 bg-sidebar-primary text-sidebar-primary-foreground rounded-full flex items-center justify-center flex-shrink-0">
                <User className="w-3 h-3" />
              </div>
              <span className="text-sm text-sidebar-accent-foreground truncate">
                {user.email}
              </span>
            </div>
            <button
              onClick={handleLogout}
              className="btn btn-ghost h-6 w-6 p-0 text-sidebar-foreground/50 hover:text-sidebar-foreground"
              title="Logout"
            >
              <LogOut className="w-3 h-3" />
            </button>
          </div>
        )}

        {/* Action Buttons */}
        <div className="flex items-center justify-end">
          {sessionId && (
            <button
              onClick={onClearSession}
              disabled={loading || isStreaming}
              className={cn(
                "btn btn-ghost h-8 w-8 p-0",
                (loading || isStreaming) && "opacity-50 cursor-not-allowed"
              )}
              title="Clear Current Session"
            >
              <RotateCcw className="w-4 h-4" />
            </button>
          )}
        </div>
      </div>

      {/* Click outside to close conversation menu */}
      {conversationMenuId && (
        <div
          className="fixed inset-0 z-0"
          onClick={() => setConversationMenuId(null)}
        />
      )}

      {/* Auth Modal */}
      <AuthModal
        open={authModalOpen}
        onClose={() => setAuthModalOpen(false)}
        mode={authMode}
        onModeChange={setAuthMode}
      />
    </div>
  );
}
