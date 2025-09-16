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
    <div className="w-full h-full flex flex-col bg-light">
      {/* Header */}
      <div className="p-6 border-b border-gray-dark/10">
        <div className="flex items-center justify-between mb-4">
          <h2 className="text-h2 text-dark">Conversations</h2>
          <button
            onClick={handleNewChat}
            disabled={loading || isStreaming}
            className={cn(
              "causa-btn causa-btn-primary h-10 w-10 p-0",
              (loading || isStreaming) && "opacity-50 cursor-not-allowed"
            )}
            title="New Conversation"
          >
            <Plus className="w-5 h-5" />
          </button>
        </div>

        {/* Search */}
        <div className="relative">
          <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 w-4 h-4 text-gray" />
          <input
            type="text"
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            placeholder="Search conversations..."
            className="causa-input pl-10 h-10 w-full"
          />
        </div>
      </div>

      {/* Conversations List */}
      <div className="flex-1 overflow-y-auto p-4">
        {isAuthenticated ? (
          filteredConversations.length > 0 ? (
            <div className="space-y-2">
              {filteredConversations.map((conversation) => (
                <div
                  key={conversation.id}
                  className={cn(
                    "group relative p-4 rounded-causa cursor-pointer transition-colors border",
                    conversation.id === sessionId
                      ? "bg-white border-brand text-dark"
                      : "bg-white border-gray/20 hover:border-brand/50 hover:shadow-sm"
                  )}
                  onClick={() => handleConversationClick(conversation.id)}
                >
                  <div className="flex items-start justify-between">
                    <div className="flex-1 min-w-0">
                      <h4 className="text-body font-medium truncate text-dark">
                        {conversation.title || 'Legal Analysis Session'}
                      </h4>
                      {conversation.lastMessage && (
                        <p className="text-small text-gray truncate mt-1">
                          {conversation.lastMessage}
                        </p>
                      )}
                      <p className="text-small text-gray mt-2">
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
                        className="opacity-0 group-hover:opacity-100 p-1 text-gray hover:text-dark transition-all"
                      >
                        <MoreVertical className="w-4 h-4" />
                      </button>
                      
                      {conversationMenuId === conversation.id && (
                        <div className="absolute right-0 top-full mt-1 bg-white border border-gray/20 rounded-causa shadow-lg z-10 min-w-[120px]">
                          <button
                            onClick={(e) => handleDeleteConversation(conversation.id, e)}
                            className="w-full px-3 py-2 text-left text-small hover:bg-light flex items-center text-red-500 rounded-causa"
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
              <MessageSquare className="w-12 h-12 text-gray mx-auto mb-4" />
              <p className="text-body text-gray-dark">
                {searchQuery ? 'No conversations found' : 'No conversations yet'}
              </p>
              <p className="text-small text-gray mt-2">
                Start analyzing legal documents to see your history
              </p>
            </div>
          )
        ) : (
          <div className="causa-sidebar-auth p-6 rounded-causa text-center">
            <User className="w-12 h-12 text-gray mx-auto mb-4" />
            <p className="text-body text-dark mb-4">
              Sign in to save your legal analysis history
            </p>
            <div className="space-y-3">
              <button
                onClick={handleLoginClick}
                className="text-body text-dark underline-offset-4 hover:underline"
              >
                Sign in
              </button>
              <div>
                <button
                  onClick={handleRegisterClick}
                  className="text-body font-bold text-brand hover:text-brand/80 transition-colors"
                >
                  Create account
                </button>
              </div>
            </div>
          </div>
        )}
      </div>

      {/* Footer */}
      <div className="p-6 border-t border-gray-dark/10">
        {isAuthenticated && user && (
          <div className="flex items-center justify-between mb-4 p-3 bg-white rounded-causa border border-gray/20">
            <div className="flex items-center space-x-3 min-w-0">
              <div className="w-8 h-8 bg-brand text-white rounded-causa flex items-center justify-center flex-shrink-0">
                <User className="w-4 h-4" />
              </div>
              <span className="text-body text-dark truncate">
                {user.email}
              </span>
            </div>
            <button
              onClick={handleLogout}
              className="p-1 text-gray hover:text-dark transition-colors"
              title="Logout"
            >
              <LogOut className="w-4 h-4" />
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
                "p-2 text-gray hover:text-dark transition-colors rounded-causa",
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
