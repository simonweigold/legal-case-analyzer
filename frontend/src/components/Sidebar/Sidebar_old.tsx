// components/Sidebar/Sidebar.tsx
import React, { useState } from 'react';
import {
  Box,
  Drawer,
  List,
  ListItem,
  ListItemButton,
  ListItemIcon,
  ListItemText,
  IconButton,
  Typography,
  Divider,
  Tooltip,
  Chip,
  Avatar,
  Button,
  TextField,
  InputAdornment,
  Badge,
  Menu,
  MenuItem
} from '@mui/material';
import {
  Menu as MenuIcon,
  Add,
  Search,
  Brightness4,
  Brightness7,
  Login,
  Logout,
  AccountCircle,
  MoreVert,
  Delete,
  Edit
} from '@mui/icons-material';
import { User, ConversationHistory } from '../../types';
import { useAuth } from '../../contexts/AuthContext';
import { AuthModal } from '../Auth';

export interface SidebarProps {
  open: boolean;
  onToggle: () => void;
  darkMode: boolean;
  onThemeToggle: () => void;
  sessionId: string | null;
  onClearSession: () => void;
  isStreaming: boolean;
  loading: boolean;
  conversations: ConversationHistory[];
  onLoadConversation: (conversationId: string) => void;
  onDeleteConversation: (conversationId: string) => void;
}

const DRAWER_WIDTH = 320;

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
  darkMode,
  onThemeToggle,
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
  const [menuAnchorEl, setMenuAnchorEl] = useState<null | HTMLElement>(null);

  // Filter conversations based on search
  const filteredConversations = conversations.filter(conv => {
    const matchesSearch = conv.title.toLowerCase().includes(searchQuery.toLowerCase()) ||
                         conv.lastMessage?.toLowerCase().includes(searchQuery.toLowerCase());
    return matchesSearch;
  });

  const handleNewChat = () => {
    onClearSession();
    onToggle(); // Close sidebar on mobile after action
  };

  const handleLoginClick = () => {
    setAuthMode('login');
    setAuthModalOpen(true);
  };

  const handleSignUpClick = () => {
    setAuthMode('register');
    setAuthModalOpen(true);
  };

  const handleMenuOpen = (event: React.MouseEvent<HTMLElement>) => {
    setMenuAnchorEl(event.currentTarget);
  };

  const handleMenuClose = () => {
    setMenuAnchorEl(null);
  };

  const handleLogout = async () => {
    handleMenuClose();
    await logout();
  };

  const renderUserSection = () => {
    if (!isAuthenticated || !user) {
      return (
        <Box sx={{ p: 2, textAlign: 'center' }}>
          <AccountCircle sx={{ fontSize: 48, color: 'text.secondary', mb: 1 }} />
          <Typography variant="body2" color="text.secondary" gutterBottom>
            Sign in to access your conversation history
          </Typography>
          <Box sx={{ display: 'flex', gap: 1, mt: 2 }}>
            <Button
              variant="contained"
              startIcon={<Login />}
              onClick={handleLoginClick}
              size="small"
              fullWidth
            >
              Sign In
            </Button>
            <Button
              variant="outlined"
              onClick={handleSignUpClick}
              size="small"
              fullWidth
            >
              Sign Up
            </Button>
          </Box>
        </Box>
      );
    }

    return (
      <Box sx={{ p: 2 }}>
        <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
          <Avatar
            src={user.avatar}
            alt={user.name || user.email}
            sx={{ width: 40, height: 40, mr: 2 }}
          >
            {(user.name || user.email).split(' ').map(n => n[0]).join('').toUpperCase()}
          </Avatar>
          <Box sx={{ flexGrow: 1, minWidth: 0 }}>
            <Typography variant="subtitle2" noWrap>
              {user.name || 'User'}
            </Typography>
            <Typography variant="caption" color="text.secondary" noWrap>
              {user.email}
            </Typography>
          </Box>
          <IconButton size="small" onClick={handleMenuOpen}>
            <MoreVert fontSize="small" />
          </IconButton>
        </Box>
        
        <Button
          variant="contained"
          startIcon={<Add />}
          onClick={handleNewChat}
          disabled={isStreaming}
          fullWidth
          sx={{ mb: 2 }}
        >
          New Analysis
        </Button>
      </Box>
    );
  };

  const renderConversationHistory = () => {
    if (!isAuthenticated) {
      return (
        <Box sx={{ p: 3, textAlign: 'center' }}>
          <Typography variant="body2" color="text.secondary">
            Your conversation history will appear here after signing in
          </Typography>
        </Box>
      );
    }

    return (
      <Box sx={{ flexGrow: 1 }}>
        {/* Search and Filter */}
        <Box sx={{ p: 2, pb: 1 }}>
          <TextField
            placeholder="Search conversations..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            size="small"
            fullWidth
            InputProps={{
              startAdornment: (
                <InputAdornment position="start">
                  <Search fontSize="small" />
                </InputAdornment>
              ),
            }}
            sx={{ mb: 1 }}
          />

        </Box>

        {/* Conversations List */}
        <List sx={{ px: 1, flexGrow: 1, maxHeight: 'calc(100vh - 320px)', overflow: 'auto' }}>
          {filteredConversations.map((conversation) => {
            return (
              <ListItem key={conversation.id} disablePadding sx={{ mb: 0.5 }}>
                <ListItemButton
                  onClick={() => onLoadConversation(conversation.id)}
                  sx={{
                    borderRadius: 1,
                    flexDirection: 'column',
                    alignItems: 'flex-start',
                    py: 1.5,
                    '&:hover': {
                      backgroundColor: 'action.hover',
                    }
                  }}
                >
                  <Box sx={{ display: 'flex', alignItems: 'center', width: '100%', mb: 0.5 }}>
                    <Box
                      sx={{
                        width: 8,
                        height: 8,
                        borderRadius: '50%',
                        mr: 1,
                        flexShrink: 0
                      }}
                    />
                    <Typography
                      variant="subtitle2"
                      sx={{
                        flexGrow: 1,
                        fontSize: '0.875rem',
                        fontWeight: 500,
                        overflow: 'hidden',
                        textOverflow: 'ellipsis',
                        whiteSpace: 'nowrap'
                      }}
                    >
                      {conversation.title}
                    </Typography>
                    <Typography variant="caption" color="text.secondary">
                      {formatDate(conversation.updated_at)}
                    </Typography>
                    <IconButton
                      size="small"
                      onClick={(e) => {
                        e.stopPropagation();
                        onDeleteConversation(conversation.id);
                      }}
                      sx={{ ml: 1 }}
                    >
                      <Delete fontSize="small" />
                    </IconButton>
                  </Box>
                  
                  {conversation.lastMessage && (
                    <Typography
                      variant="body2"
                      color="text.secondary"
                      sx={{
                        fontSize: '0.75rem',
                        overflow: 'hidden',
                        textOverflow: 'ellipsis',
                        whiteSpace: 'nowrap',
                        width: '100%',
                        mb: 0.5
                      }}
                    >
                      {conversation.lastMessage}
                    </Typography>
                  )}
                  
                  <Box sx={{ display: 'flex', alignItems: 'center', width: '100%' }}>
                    {conversation.category && (
                      <Chip
                        label={conversation.category}
                        size="small"
                        variant="outlined"
                        sx={{
                          fontSize: '0.6rem',
                          height: 20,
                          mr: 1
                        }}
                      />
                    )}
                    {conversation.messageCount && (
                      <Badge
                        badgeContent={conversation.messageCount}
                        color="primary"
                        sx={{
                          '& .MuiBadge-badge': {
                            fontSize: '0.6rem',
                            height: 16,
                            minWidth: 16
                          }
                        }}
                      >
                        <Typography variant="caption" color="text.secondary">
                          messages
                        </Typography>
                      </Badge>
                    )}
                  </Box>
                </ListItemButton>
              </ListItem>
            );
          })}
          
          {filteredConversations.length === 0 && searchQuery && (
            <Box sx={{ p: 2, textAlign: 'center' }}>
              <Typography variant="body2" color="text.secondary">
                No conversations found matching "{searchQuery}"
              </Typography>
            </Box>
          )}
          
          {filteredConversations.length === 0 && !searchQuery && isAuthenticated && (
            <Box sx={{ p: 2, textAlign: 'center' }}>
              <Typography variant="body2" color="text.secondary">
                No conversations yet. Start a new analysis!
              </Typography>
            </Box>
          )}
        </List>
      </Box>
    );
  };

  const drawerContent = (
    <Box sx={{ width: DRAWER_WIDTH, height: '100%', display: 'flex', flexDirection: 'column' }}>
      {/* Header */}
      <Box sx={{ p: 2, borderBottom: '1px solid', borderColor: 'divider' }}>
        <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
          <Box>
            <Typography variant="h6" component="h1" sx={{ fontWeight: 600, fontSize: '1.1rem' }}>
              Legal Case Analyzer
            </Typography>
            <Typography variant="body2" color="text.secondary" sx={{ fontSize: '0.75rem' }}>
              AI-powered legal analysis
            </Typography>
          </Box>
          <IconButton onClick={onThemeToggle} size="small">
            {darkMode ? <Brightness7 fontSize="small" /> : <Brightness4 fontSize="small" />}
          </IconButton>
        </Box>
      </Box>

      {/* User Section */}
      {renderUserSection()}
      
      <Divider />

      {/* Conversation History */}
      {renderConversationHistory()}

      {/* Footer */}
      {isAuthenticated && (
        <>
          <Divider />
          <Box sx={{ p: 2 }}>
            <Typography variant="caption" color="text.secondary" display="block">
              Session: {sessionId && typeof sessionId === 'string' ? sessionId.slice(0, 8) + '...' : 'New Session'}
            </Typography>
            {(loading || isStreaming) && (
              <Chip 
                label={isStreaming ? 'Streaming...' : 'Processing...'}
                size="small"
                color="primary"
                sx={{ mt: 1, fontSize: '0.7rem', height: 20 }}
              />
            )}
          </Box>
        </>
      )}
    </Box>
  );

  return (
    <>
      {/* Menu Button - only show when sidebar is closed */}
      {!open && (
        <IconButton
          onClick={onToggle}
          sx={{
            position: 'fixed',
            top: 16,
            right: 16,
            zIndex: 1201,
            backgroundColor: 'background.paper',
            boxShadow: 2,
            '&:hover': {
              backgroundColor: 'action.hover',
            }
          }}
        >
          <MenuIcon />
        </IconButton>
      )}

      {/* Drawer */}
      <Drawer
        variant="temporary"
        anchor="right"
        open={open}
        onClose={onToggle}
        ModalProps={{
          keepMounted: true, // Better open performance on mobile
        }}
        sx={{
          '& .MuiDrawer-paper': {
            width: DRAWER_WIDTH,
            boxSizing: 'border-box',
          },
        }}
      >
        {drawerContent}
      </Drawer>

      {/* User Menu */}
      <Menu
        anchorEl={menuAnchorEl}
        open={Boolean(menuAnchorEl)}
        onClose={handleMenuClose}
      >
        <MenuItem onClick={handleLogout}>
          <Logout sx={{ mr: 1 }} fontSize="small" />
          Sign Out
        </MenuItem>
      </Menu>

      {/* Auth Modal */}
      <AuthModal
        open={authModalOpen}
        onClose={() => setAuthModalOpen(false)}
        initialMode={authMode}
      />
    </>
  );
}
