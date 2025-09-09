# User Authentication and Conversation Management

## Overview

The Legal Case Analyzer backend now includes comprehensive user authentication and conversation management using `fastapi-users` and SQLite database. This allows users to:

- Sign up and sign in with email/password
- Maintain persistent conversation histories
- Access their own conversations securely
- Create, view, and delete conversations

## New Features Added

### 1. **User Authentication**
- JWT-based authentication using `fastapi-users`
- User registration and login endpoints
- Password-based authentication
- Secure user session management

### 2. **Database Models**
- **User**: Built on `fastapi-users` UUID-based user model
- **Conversation**: Stores conversation metadata (title, user association)
- **Message**: Stores individual messages with role, content, and tool information

### 3. **New API Endpoints**

#### Authentication Endpoints
- `POST /auth/register` - User registration
- `POST /auth/jwt/login` - User login
- `POST /auth/jwt/logout` - User logout
- `GET /users/me` - Get current user info

#### Conversation Management
- `POST /conversations/` - Create new conversation
- `GET /conversations/` - Get user's conversations
- `GET /conversations/{id}` - Get conversation with messages
- `DELETE /conversations/{id}` - Delete conversation
- `GET /conversations/{id}/messages` - Get conversation messages

#### Enhanced Chat Endpoints
- `POST /chat/` - Chat with conversation management (authenticated)
- `POST /chat/stream` - Streaming chat with conversation management
- `POST /chat/legacy` - Legacy session-based chat (backward compatibility)

### 4. **Database Schema**

```sql
-- Users table (managed by fastapi-users)
CREATE TABLE user (
    id UUID PRIMARY KEY,
    email VARCHAR UNIQUE NOT NULL,
    hashed_password VARCHAR NOT NULL,
    is_active BOOLEAN DEFAULT TRUE,
    is_superuser BOOLEAN DEFAULT FALSE,
    is_verified BOOLEAN DEFAULT FALSE
);

-- Conversations table
CREATE TABLE conversations (
    id INTEGER PRIMARY KEY,
    title VARCHAR(255) NOT NULL,
    user_id UUID REFERENCES user(id),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Messages table
CREATE TABLE messages (
    id INTEGER PRIMARY KEY,
    conversation_id INTEGER REFERENCES conversations(id),
    role VARCHAR(50) NOT NULL,  -- 'user', 'assistant', 'tool'
    content TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    tool_name VARCHAR(100),     -- For tool messages
    tool_call_id VARCHAR(100)   -- For tool messages
);
```

### 5. **File Structure Updates**

```
backend/
├── main.py                     # Updated with auth routes and DB initialization
├── config.py                  # Added database and auth settings
├── database.py                # Database connection and session management
├── auth.py                    # fastapi-users authentication setup
├── models/
│   ├── __init__.py
│   └── database.py            # SQLAlchemy models for User, Conversation, Message
├── schemas/
│   ├── __init__.py
│   ├── chat.py               # Original chat schemas
│   └── conversation.py       # New conversation schemas
├── services/
│   ├── __init__.py
│   ├── tools.py              # Original tools
│   ├── session.py            # Original session management (for backward compatibility)
│   └── conversation.py       # New conversation service for DB operations
└── routes/
    ├── __init__.py
    ├── chat.py               # Updated with authenticated and legacy endpoints
    ├── auth.py               # Authentication routes
    └── conversations.py      # Conversation management routes
```

## Usage Examples

### 1. User Registration
```bash
curl -X POST "http://localhost:8000/auth/register" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@example.com",
    "password": "securepassword"
  }'
```

### 2. User Login
```bash
curl -X POST "http://localhost:8000/auth/jwt/login" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=user@example.com&password=securepassword"
```

### 3. Start New Conversation
```bash
curl -X POST "http://localhost:8000/chat/" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Hello, I need help with a legal case",
    "conversation_title": "Legal Case Discussion"
  }'
```

### 4. Continue Existing Conversation
```bash
curl -X POST "http://localhost:8000/chat/" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Can you provide more details?",
    "conversation_id": 1
  }'
```

### 5. Get User Conversations
```bash
curl -X GET "http://localhost:8000/conversations/" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"
```

## Migration Notes

### Backward Compatibility
- Legacy endpoints maintain session-based functionality
- Existing frontend can continue using `/chat/legacy` endpoints
- Session-based storage still available for non-authenticated use

### Database Migration
- Database tables are created automatically on first run
- SQLite database file: `legal_analyzer.db`
- No manual migration required

### Environment Variables
Add to your `.env` file:
```
SECRET_KEY=your-very-secure-secret-key-change-in-production
DATABASE_URL=sqlite+aiosqlite:///./legal_analyzer.db
```

## Security Considerations

1. **JWT Secret**: Change the `SECRET_KEY` in production
2. **CORS**: Restrict `CORS_ORIGINS` in production
3. **HTTPS**: Use HTTPS in production for secure token transmission
4. **Database**: Consider PostgreSQL for production use
5. **Rate Limiting**: Implement rate limiting for auth endpoints

## Benefits

1. **Persistent Storage**: Conversations are saved and can be accessed anytime
2. **User Isolation**: Each user only sees their own conversations
3. **Scalability**: Database-backed storage supports multiple users
4. **Security**: JWT-based authentication with proper user isolation
5. **Flexibility**: Both authenticated and session-based modes available
