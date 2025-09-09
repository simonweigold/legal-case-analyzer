# Legal Case Analyzer API - Bruno Collection

This Bruno collection provides comprehensive examples for testing the Legal Case Analyzer API, including both legacy (session-based) and new (authenticated user-based) endpoints.

## Setup Instructions

1. **Environment Variables**: The collection uses environment variables to store authentication tokens and conversation IDs between requests. Bruno will automatically manage these during test execution.

2. **Server**: Ensure the Legal Case Analyzer API is running on `http://localhost:8000`

3. **Test Order**: For the authenticated endpoints, run the requests in the following order:
   1. `user-register` - Register a new user
   2. `user-login` - Login and get authentication token
   3. `get-current-user` - Verify authentication
   4. Other authenticated endpoints as needed

## Request Overview

### Authentication Endpoints

#### 1. **user-register.bru**
- **Purpose**: Register a new user account
- **Method**: POST `/auth/register`
- **Body**: JSON with email and password
- **Test**: Validates successful registration and user data

#### 2. **user-login.bru**
- **Purpose**: Login and obtain JWT token
- **Method**: POST `/auth/jwt/login`
- **Body**: Form data with username (email) and password
- **Test**: Validates login success and stores auth token
- **Note**: Stores `auth_token` environment variable for subsequent requests

#### 3. **get-current-user.bru**
- **Purpose**: Get current authenticated user information
- **Method**: GET `/users/me`
- **Auth**: Bearer token
- **Test**: Validates user profile data

#### 4. **user-logout.bru**
- **Purpose**: Logout current user
- **Method**: POST `/auth/jwt/logout`
- **Auth**: Bearer token
- **Test**: Validates logout and clears auth token

### Conversation Management

#### 5. **create-conversation.bru**
- **Purpose**: Create a new empty conversation
- **Method**: POST `/conversations/`
- **Auth**: Bearer token
- **Body**: JSON with conversation title
- **Test**: Validates conversation creation and stores conversation ID

#### 6. **get-user-conversations.bru**
- **Purpose**: Get all conversations for the authenticated user
- **Method**: GET `/conversations/`
- **Auth**: Bearer token
- **Test**: Validates conversation list structure

#### 7. **get-conversation-with-messages.bru**
- **Purpose**: Get a specific conversation with all its messages
- **Method**: GET `/conversations/{id}`
- **Auth**: Bearer token
- **Test**: Validates conversation and message structure

#### 8. **delete-conversation.bru**
- **Purpose**: Delete a conversation
- **Method**: DELETE `/conversations/{id}`
- **Auth**: Bearer token
- **Test**: Validates successful deletion

### Chat Endpoints

#### 9. **authenticated-chat-new-conversation.bru**
- **Purpose**: Start a new conversation with the AI
- **Method**: POST `/chat/`
- **Auth**: Bearer token
- **Body**: JSON with message and optional conversation title
- **Test**: Validates response and stores conversation ID
- **Note**: Creates a new conversation automatically

#### 10. **authenticated-chat-continue-conversation.bru**
- **Purpose**: Continue an existing conversation
- **Method**: POST `/chat/`
- **Auth**: Bearer token
- **Body**: JSON with message and conversation ID
- **Test**: Validates response within existing conversation

#### 11. **streaming-chat-with-conversation.bru**
- **Purpose**: Stream chat response with conversation management
- **Method**: POST `/chat/stream`
- **Auth**: Bearer token
- **Body**: JSON with message and optional conversation details
- **Note**: Returns Server-Sent Events (SSE) streaming response

### Legacy Endpoints (Backward Compatibility)

#### 12. **basic-chat.bru**
- **Purpose**: Legacy session-based chat (no authentication required)
- **Method**: POST `/chat/legacy`
- **Body**: JSON with message and session_id
- **Note**: Uses in-memory session storage

#### 13. **chat-court-decision.bru**
- **Purpose**: Legacy session-based chat with legal case analysis
- **Method**: POST `/chat/legacy`
- **Body**: JSON with complex legal case text and session_id
- **Note**: Demonstrates tool usage for legal analysis

## Environment Variables Used

- `auth_token`: JWT authentication token (set by login, used by authenticated endpoints)
- `conversation_id`: ID of the current conversation (set by chat endpoints)
- `new_conversation_id`: ID of manually created conversation (set by create-conversation)

## Response Formats

### Authentication Response
```json
{
  "access_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
  "token_type": "bearer"
}
```

### User Response
```json
{
  "id": "uuid-string",
  "email": "user@example.com",
  "is_active": true,
  "is_superuser": false,
  "is_verified": false
}
```

### Conversation Response
```json
{
  "id": 1,
  "title": "Legal Discussion",
  "user_id": "uuid-string",
  "created_at": "2025-09-08T10:00:00Z",
  "updated_at": "2025-09-08T10:00:00Z"
}
```

### Chat Response
```json
{
  "response": "AI response text...",
  "conversation_id": 1,
  "conversation_title": "Legal Discussion"
}
```

### Streaming Response (SSE)
```
data: {"content": "Hello", "conversation_id": 1, "done": false, "type": "token"}
data: {"content": " there!", "conversation_id": 1, "done": false, "type": "token"}
data: {"content": "", "conversation_id": 1, "done": true, "type": "done"}
```

## Testing Flow

### Full Authentication + Conversation Flow
1. Register user → Login → Create conversation → Chat → Get conversations → Delete conversation → Logout

### Quick Chat Testing
1. Login → Start new chat conversation → Continue conversation → Get conversation history

### Legacy Testing
1. Use basic-chat or chat-court-decision for session-based testing (no auth required)

## Notes

- All authenticated endpoints require a valid JWT token in the Authorization header
- Conversation IDs are automatically managed between related requests
- The streaming endpoint returns real-time responses as the AI generates them
- Legacy endpoints maintain backward compatibility with existing implementations
- Tool usage (legal analysis, precedent search) is demonstrated in the court decision example
