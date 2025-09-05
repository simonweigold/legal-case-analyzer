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
  Badge
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
  FilterList
} from '@mui/icons-material';
import { User, ConversationHistory } from '../../types';
import { sampleUser, sampleConversationHistories, getCategoryInfo, formatDate } from '../../data/sampleData';

export interface SidebarProps {
  open: boolean;
  onToggle: () => void;
  darkMode: boolean;
  onThemeToggle: () => void;
  sessionId: string;
  onClearSession: () => void;
  isStreaming: boolean;
  loading: boolean;
}

const DRAWER_WIDTH = 320;

export function Sidebar({
  open,
  onToggle,
  darkMode,
  onThemeToggle,
  sessionId,
  onClearSession,
  isStreaming,
  loading
}: SidebarProps) {
  // Mock state for user authentication - replace with real auth state
  const [isLoggedIn, setIsLoggedIn] = useState(true);
  const [user] = useState<User>(sampleUser);
  const [conversations] = useState<ConversationHistory[]>(sampleConversationHistories);
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedCategory, setSelectedCategory] = useState<string>('all');

  // Filter conversations based on search and category
  const filteredConversations = conversations.filter(conv => {
    const matchesSearch = conv.title.toLowerCase().includes(searchQuery.toLowerCase()) ||
                         conv.lastMessage.toLowerCase().includes(searchQuery.toLowerCase());
    const matchesCategory = selectedCategory === 'all' || conv.category === selectedCategory;
    return matchesSearch && matchesCategory;
  });

  const handleNewChat = () => {
    onClearSession();
    onToggle(); // Close sidebar on mobile after action
  };

  const handleLoginToggle = () => {
    setIsLoggedIn(!isLoggedIn);
  };

  const renderUserSection = () => {
    if (!isLoggedIn) {
      return (
        <Box sx={{ p: 2, textAlign: 'center' }}>
          <AccountCircle sx={{ fontSize: 48, color: 'text.secondary', mb: 1 }} />
          <Typography variant="body2" color="text.secondary" gutterBottom>
            Sign in to access your conversation history
          </Typography>
          <Button
            variant="contained"
            startIcon={<Login />}
            onClick={handleLoginToggle}
            size="small"
            fullWidth
            sx={{ mt: 1 }}
          >
            Sign In
          </Button>
        </Box>
      );
    }

    return (
      <Box sx={{ p: 2 }}>
        <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
          <Avatar
            src={user.avatar}
            alt={user.name}
            sx={{ width: 40, height: 40, mr: 2 }}
          >
            {user.name.split(' ').map(n => n[0]).join('')}
          </Avatar>
          <Box sx={{ flexGrow: 1, minWidth: 0 }}>
            <Typography variant="subtitle2" noWrap>
              {user.name}
            </Typography>
            <Typography variant="caption" color="text.secondary" noWrap>
              {user.email}
            </Typography>
          </Box>
          <IconButton size="small" onClick={handleLoginToggle}>
            <Logout fontSize="small" />
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
    if (!isLoggedIn) {
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
          
          {/* Category Filter */}
          <Box sx={{ display: 'flex', gap: 0.5, flexWrap: 'wrap' }}>
            {['all', 'contract', 'litigation', 'compliance', 'research'].map((category) => (
              <Chip
                key={category}
                label={category === 'all' ? 'All' : category.charAt(0).toUpperCase() + category.slice(1)}
                size="small"
                variant={selectedCategory === category ? 'filled' : 'outlined'}
                onClick={() => setSelectedCategory(category)}
                sx={{ fontSize: '0.75rem' }}
              />
            ))}
          </Box>
        </Box>

        {/* Conversations List */}
        <List sx={{ px: 1, flexGrow: 1, maxHeight: 'calc(100vh - 320px)', overflow: 'auto' }}>
          {filteredConversations.map((conversation) => {
            const categoryInfo = getCategoryInfo(conversation.category);
            return (
              <ListItem key={conversation.id} disablePadding sx={{ mb: 0.5 }}>
                <ListItemButton
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
                        backgroundColor: categoryInfo.color,
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
                      {formatDate(conversation.lastUpdated)}
                    </Typography>
                  </Box>
                  
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
                  
                  <Box sx={{ display: 'flex', alignItems: 'center', width: '100%' }}>
                    <Chip
                      label={conversation.category}
                      size="small"
                      variant="outlined"
                      sx={{
                        fontSize: '0.6rem',
                        height: 20,
                        color: categoryInfo.color,
                        borderColor: categoryInfo.color,
                        mr: 1
                      }}
                    />
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
      {isLoggedIn && (
        <>
          <Divider />
          <Box sx={{ p: 2 }}>
            <Typography variant="caption" color="text.secondary" display="block">
              Session: {sessionId.slice(0, 8)}...
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
      {/* Menu Button */}
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
    </>
  );
}
