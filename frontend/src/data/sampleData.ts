// data/sampleData.ts
import { User, ConversationHistory } from '../types';

export const sampleUser: User = {
  id: 'user-123',
  name: 'Sarah Johnson',
  email: 'sarah.johnson@law.com',
  avatar: 'https://images.unsplash.com/photo-1494790108755-2616b9e70e8a?w=150&h=150&fit=crop&crop=face',
  joinedDate: '2024-01-15'
};

export const sampleConversationHistories: ConversationHistory[] = [
  {
    id: 'conv-1',
    title: 'Employment Contract Review',
    lastMessage: 'The non-compete clause appears to be overly broad...',
    lastUpdated: '2024-12-20T10:30:00Z',
    messageCount: 12,
    category: 'contract'
  },
  {
    id: 'conv-2',
    title: 'Intellectual Property Dispute',
    lastMessage: 'Based on the precedent cases, the patent claim...',
    lastUpdated: '2024-12-19T16:45:00Z',
    messageCount: 8,
    category: 'litigation'
  },
  {
    id: 'conv-3',
    title: 'GDPR Compliance Assessment',
    lastMessage: 'The data processing activities need to be...',
    lastUpdated: '2024-12-18T14:20:00Z',
    messageCount: 15,
    category: 'compliance'
  },
  {
    id: 'conv-4',
    title: 'Corporate Merger Due Diligence',
    lastMessage: 'The financial disclosures show several red flags...',
    lastUpdated: '2024-12-17T09:15:00Z',
    messageCount: 23,
    category: 'research'
  },
  {
    id: 'conv-5',
    title: 'Lease Agreement Analysis',
    lastMessage: 'The escalation clause in section 4.2...',
    lastUpdated: '2024-12-16T11:30:00Z',
    messageCount: 6,
    category: 'contract'
  },
  {
    id: 'conv-6',
    title: 'Trademark Opposition Research',
    lastMessage: 'Similar marks in the same class include...',
    lastUpdated: '2024-12-15T13:45:00Z',
    messageCount: 10,
    category: 'research'
  },
  {
    id: 'conv-7',
    title: 'Securities Compliance Review',
    lastMessage: 'The disclosure requirements under Rule 10b-5...',
    lastUpdated: '2024-12-14T08:20:00Z',
    messageCount: 18,
    category: 'compliance'
  },
  {
    id: 'conv-8',
    title: 'Class Action Settlement',
    lastMessage: 'The proposed settlement amount of $2.5M...',
    lastUpdated: '2024-12-13T15:10:00Z',
    messageCount: 31,
    category: 'litigation'
  }
];

// Helper function to get category color and icon
export const getCategoryInfo = (category: ConversationHistory['category']) => {
  switch (category) {
    case 'contract':
      return { color: '#2196F3', icon: '📄' };
    case 'litigation':
      return { color: '#F44336', icon: '⚖️' };
    case 'compliance':
      return { color: '#FF9800', icon: '✅' };
    case 'research':
      return { color: '#4CAF50', icon: '🔍' };
    case 'other':
      return { color: '#9C27B0', icon: '📋' };
    default:
      return { color: '#757575', icon: '💼' };
  }
};

// Helper function to format date
export const formatDate = (dateString: string): string => {
  const date = new Date(dateString);
  const now = new Date();
  const diffInHours = Math.floor((now.getTime() - date.getTime()) / (1000 * 60 * 60));
  
  if (diffInHours < 1) return 'Just now';
  if (diffInHours < 24) return `${diffInHours}h ago`;
  if (diffInHours < 168) return `${Math.floor(diffInHours / 24)}d ago`;
  
  return date.toLocaleDateString('en-US', { 
    month: 'short', 
    day: 'numeric',
    year: date.getFullYear() !== now.getFullYear() ? 'numeric' : undefined
  });
};
