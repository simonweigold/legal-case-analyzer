# Supabase Integration Setup Guide

This guide will help you integrate your Legal Case Analyzer with Supabase for user authentication and conversation history storage.

## Prerequisites

- Running Supabase instance (using the official docker-compose setup)
- Python 3.8+ with virtual environment
- Node.js/Bun for frontend
- OpenAI API key

## Backend Setup

### 1. Install Dependencies

```bash
cd backend
source .venv/bin/activate  # Activate your virtual environment
pip install -r requirements.txt
```

### 2. Configure Environment Variables

Copy the example environment file and update it:

```bash
cp .env.example .env
```

Edit `.env` and add your actual values:

```env
# OpenAI API Configuration
OPENAI_API_KEY=your_actual_openai_api_key_here

# Supabase Configuration
SUPABASE_URL=http://localhost:54321
SUPABASE_ANON_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZS1kZW1vIiwicm9sZSI6ImFub24iLCJleHAiOjE5ODM4MTI5OTZ9.CRXP1A7WOeoJeXxjNni43kdQwgnWNReilDMblYTn_I0
SUPABASE_SERVICE_ROLE_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZS1kZW1vIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImV4cCI6MTk4MzgxMjk5Nn0.EGIM96RAZx35lJzdJsyH-qQwv8Hdp7fsn3W0YpN81IU

# JWT Secret for token verification
JWT_SECRET=your-secret-key
JWT_ALGORITHM=HS256
```

**Note**: The keys above are the default development keys from Supabase. Replace them with your actual keys if you're using a custom setup.

### 3. Set Up Database Tables

You have two options:

#### Option A: Using Supabase SQL Editor (Recommended)

1. Open your Supabase Dashboard at `http://localhost:54323`
2. Go to the SQL Editor
3. Copy and paste the contents of `setup_supabase.sql`
4. Run the query

#### Option B: Using Python Script

```bash
python3 setup_database.py
```

### 4. Start the Backend

```bash
python3 main.py
```

The API will be available at `http://localhost:8000` with the following new endpoints:

- `POST /conversations` - Create a new conversation
- `GET /conversations` - List user's conversations
- `POST /conversations/{id}/chat` - Send a message to a conversation
- `GET /conversations/{id}/messages` - Get conversation messages

## Frontend Setup

### 1. Install Dependencies

```bash
cd frontend
bun install
```

### 2. Start the Frontend

```bash
bun dev
```

The frontend will be available at `http://localhost:3000`.

## User Flow

1. **Authentication**: Users can sign up/login using email and password
2. **Conversations**: Users can create new conversations or continue existing ones
3. **Chat**: Messages are stored in Supabase and tied to the authenticated user
4. **History**: Conversation history is preserved and only accessible to the conversation owner

## Key Features Added

### Backend Features

- ✅ **Supabase Integration**: Full integration with Supabase for data storage
- ✅ **User Authentication**: JWT-based authentication with Supabase Auth
- ✅ **Row Level Security**: Database policies ensure users only access their own data
- ✅ **Conversation Management**: Create, list, update, and delete conversations
- ✅ **Message Storage**: All chat messages are stored in PostgreSQL
- ✅ **Backward Compatibility**: Legacy endpoints still work for existing integrations

### Frontend Features

- ✅ **Authentication UI**: Login/signup forms with error handling
- ✅ **Protected Routes**: App only accessible after authentication
- ✅ **Real-time Auth**: Automatic session management and updates
- ✅ **Conversation Hooks**: React hooks for managing conversations and messages

## API Documentation

### Authentication

All API endpoints (except legacy ones) require a valid JWT token in the Authorization header:

```
Authorization: Bearer <your-jwt-token>
```

### New Endpoints

#### Create Conversation
```http
POST /conversations
Content-Type: application/json
Authorization: Bearer <token>

{
  "title": "My Legal Case Analysis",
  "metadata": {}
}
```

#### List Conversations
```http
GET /conversations?page=1&page_size=20
Authorization: Bearer <token>
```

#### Send Message
```http
POST /conversations/{conversation_id}/chat
Content-Type: application/json
Authorization: Bearer <token>

{
  "message": "Analyze this contract clause...",
  "conversation_id": "uuid-here"
}
```

### Legacy Endpoints

The following endpoints remain for backward compatibility:
- `POST /chat` - Session-based chat (no authentication required)
- `GET /chat/history/{session_id}` - Get session history
- `POST /chat/stream` - Streaming chat

## Security Features

- **Row Level Security (RLS)**: Database policies ensure data isolation
- **JWT Authentication**: Secure token-based authentication
- **Password Hashing**: Supabase handles secure password storage
- **CORS Configuration**: Proper CORS setup for development

## Troubleshooting

### Common Issues

1. **Database Connection Error**
   - Make sure Supabase is running: `docker-compose ps`
   - Check your SUPABASE_URL in `.env`

2. **Authentication Errors**
   - Verify your JWT keys are correct
   - Check that RLS policies are set up correctly

3. **Frontend Build Errors**
   - Run `bun install` to ensure all dependencies are installed
   - Check that the Supabase client is properly configured

### Logs and Debugging

- Backend logs: Check the FastAPI console output
- Frontend logs: Check browser developer console
- Database logs: Check Supabase Dashboard logs

## Next Steps

1. **Customize the UI**: Modify the frontend components to match your design
2. **Add More Features**: Implement conversation sharing, export, etc.
3. **Production Setup**: Configure proper secrets and SSL for production
4. **Monitoring**: Add logging and error tracking
5. **Backup**: Set up database backups for production

## Development Notes

- The backend maintains backward compatibility with the existing session-based API
- Frontend uses optimistic updates for better UX
- Database schemas support extensible metadata for future features
- Authentication context provides easy access to user state throughout the app

For more help, check the API documentation at `http://localhost:8000/docs` when the backend is running.
