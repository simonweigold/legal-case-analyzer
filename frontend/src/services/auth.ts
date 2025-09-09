// services/auth.ts
export interface AuthUser {
  id: string;
  email: string;
  name?: string;
  avatar?: string;
  is_active: boolean;
  is_superuser: boolean;
  is_verified: boolean;
}

export interface LoginRequest {
  username: string;
  password: string;
}

export interface RegisterRequest {
  email: string;
  password: string;
  name?: string;
}

export interface AuthResponse {
  access_token: string;
  token_type: string;
}

class AuthService {
  private baseUrl = 'http://localhost:8000';
  private tokenKey = 'legal_analyzer_token';

  // Get stored token
  getToken(): string | null {
    return localStorage.getItem(this.tokenKey);
  }

  // Store token
  setToken(token: string): void {
    localStorage.setItem(this.tokenKey, token);
  }

  // Remove token
  clearToken(): void {
    localStorage.removeItem(this.tokenKey);
  }

  // Check if user is logged in
  isAuthenticated(): boolean {
    const token = this.getToken();
    if (!token) return false;
    
    try {
      // Basic token validation (check if it's not expired)
      const payload = JSON.parse(atob(token.split('.')[1]));
      const currentTime = Date.now() / 1000;
      return payload.exp > currentTime;
    } catch {
      return false;
    }
  }

  // Get authorization headers
  getAuthHeaders(): Record<string, string> {
    const token = this.getToken();
    return token ? { Authorization: `Bearer ${token}` } : {};
  }

  // Register new user
  async register(data: RegisterRequest): Promise<AuthUser> {
    const response = await fetch(`${this.baseUrl}/auth/register`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(data),
    });

    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail || 'Registration failed');
    }

    return response.json();
  }

  // Login user
  async login(data: LoginRequest): Promise<AuthResponse> {
    const formData = new FormData();
    formData.append('username', data.username);
    formData.append('password', data.password);

    const response = await fetch(`${this.baseUrl}/auth/jwt/login`, {
      method: 'POST',
      body: formData,
    });

    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail || 'Login failed');
    }

    const authResponse = await response.json();
    this.setToken(authResponse.access_token);
    return authResponse;
  }

  // Logout user
  async logout(): Promise<void> {
    try {
      await fetch(`${this.baseUrl}/auth/jwt/logout`, {
        method: 'POST',
        headers: this.getAuthHeaders(),
      });
    } catch (error) {
      console.error('Logout error:', error);
    } finally {
      this.clearToken();
    }
  }

  // Get current user info
  async getCurrentUser(): Promise<AuthUser> {
    const response = await fetch(`${this.baseUrl}/users/me`, {
      headers: this.getAuthHeaders(),
    });

    if (!response.ok) {
      if (response.status === 401) {
        this.clearToken();
        throw new Error('Authentication expired');
      }
      throw new Error('Failed to get user info');
    }

    return response.json();
  }

  // Update user profile
  async updateProfile(data: Partial<AuthUser>): Promise<AuthUser> {
    const response = await fetch(`${this.baseUrl}/users/me`, {
      method: 'PATCH',
      headers: {
        'Content-Type': 'application/json',
        ...this.getAuthHeaders(),
      },
      body: JSON.stringify(data),
    });

    if (!response.ok) {
      throw new Error('Failed to update profile');
    }

    return response.json();
  }
}

export const authService = new AuthService();
