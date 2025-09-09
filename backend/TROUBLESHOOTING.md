# Backend Troubleshooting Guide

## Issue: ImportError with JWTAuthentication

The error `ImportError: cannot import name 'JWTAuthentication' from 'fastapi_users.authentication'` indicates that the fastapi-users API has changed.

## Solutions Applied

### 1. Updated Authentication Setup (auth.py)
- Replaced `JWTAuthentication` with `JWTStrategy`
- Updated the authentication backend setup to use the new API

### 2. Fixed Database Dependencies (database.py)
- Added proper `Depends` import
- Fixed the `get_user_db` function to use proper dependency injection

### 3. Reorganized Imports (main.py)
- Moved imports inside functions to avoid circular dependencies
- Added a setup function to initialize routes after app creation

### 4. Updated Requirements (requirements.txt)
- Updated fastapi-users version to >= 13.0.0 for compatibility

## Step-by-Step Debugging

If you're still getting errors, try this approach:

1. **Test with minimal auth setup**:
   ```bash
   python main_test.py
   ```

2. **Check specific dependency versions**:
   ```bash
   pip show fastapi-users
   pip show sqlalchemy
   pip show fastapi
   ```

3. **Install exact working versions**:
   ```bash
   pip install fastapi-users[sqlalchemy]==13.0.0
   pip install sqlalchemy==2.0.23
   pip install fastapi==0.104.1
   ```

## Common Issues and Fixes

### Issue 1: Circular Import
**Error**: Import errors when starting the app
**Fix**: Moved imports inside functions and removed circular dependencies

### Issue 2: Wrong fastapi-users Version
**Error**: `JWTAuthentication` not found
**Fix**: Updated to use `JWTStrategy` and newer fastapi-users API

### Issue 3: Missing Dependencies
**Error**: Various import errors
**Fix**: Ensured all dependencies are properly listed in requirements.txt

### Issue 4: Database Connection
**Error**: SQLite or async session issues
**Fix**: Used proper async SQLite URL: `sqlite+aiosqlite:///./legal_analyzer.db`

## Verification Steps

1. **Basic FastAPI works**:
   ```bash
   curl http://localhost:8000/
   ```

2. **Database tables created**:
   Check if `legal_analyzer.db` file is created in the backend directory

3. **Auth endpoints available**:
   ```bash
   curl http://localhost:8000/docs
   ```
   Should show registration and login endpoints

4. **User registration works**:
   ```bash
   curl -X POST "http://localhost:8000/auth/register" \
     -H "Content-Type: application/json" \
     -d '{"email": "test@example.com", "password": "testpass123"}'
   ```

## Alternative: Downgrade Approach

If the new API doesn't work, you can try downgrading:

```bash
pip install fastapi-users[sqlalchemy]==12.1.3
```

And revert the auth.py changes to use `JWTAuthentication`.

## Files Changed

1. `auth.py` - Updated authentication strategy
2. `database.py` - Fixed dependency injection
3. `main.py` - Reorganized imports to avoid circular dependencies
4. `main_test.py` - Created minimal test version
5. `requirements.txt` - Updated package versions
6. `routes/chat.py` - Removed direct model initialization
