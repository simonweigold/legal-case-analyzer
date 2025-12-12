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

import { backendConfig } from '../config';
import { createClient, SupabaseClient } from '@supabase/supabase-js';

const SUPABASE_URL = (import.meta as any).env?.VITE_SUPABASE_URL as string;
const SUPABASE_ANON_KEY = (import.meta as any).env?.VITE_SUPABASE_ANON_KEY as string;

class AuthService {
  private baseUrl = backendConfig.baseUrl;
  private tokenKey = 'legal_analyzer_token';
  private supabase: SupabaseClient;

  constructor() {
    if (!SUPABASE_URL || !SUPABASE_ANON_KEY) {
      // Soft fail to avoid crashing UI; backend routes will still work if custom auth is used
      console.warn('Supabase env missing. Set VITE_SUPABASE_URL and VITE_SUPABASE_ANON_KEY.');
    }
    this.supabase = createClient(SUPABASE_URL, SUPABASE_ANON_KEY);
  }

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

  // Register new user via Supabase Auth
  async register(data: RegisterRequest): Promise<AuthUser> {
    const { data: signUpData, error } = await this.supabase.auth.signUp({
      email: data.email,
      password: data.password,
      options: {
  // Store display name in user_metadata so it shows in Supabase Auth user object
  data: data.name ? { name: data.name, full_name: data.name, display_name: data.name } : undefined,
      },
    });
    if (error) throw new Error(error.message);

    const user = signUpData.user;
    if (!user) throw new Error('Signup succeeded but no user returned');
    // If email confirmations are enabled, session may be null until confirmed
    const session = signUpData.session;
    if (session?.access_token) this.setToken(session.access_token);

    // Also persist display name to a profiles table if present (common convention)
    // This requires a `profiles` table with RLS allowing insert/update where id = auth.uid()
    // Schema example:
    // create table public.profiles (id uuid primary key references auth.users(id) on delete cascade, full_name text, updated_at timestamptz default now());
    // policy: with check (auth.uid() = id)
    if (data.name) {
      try {
        await this.supabase.from('profiles').upsert({
          id: user.id,
          full_name: data.name,
        }, { onConflict: 'id' });
      } catch (e) {
        console.warn('Profiles upsert failed:', e);
      }
    }
    return {
      id: user.id,
      email: user.email ?? '',
      name: (user.user_metadata as any)?.name,
      avatar: undefined,
      is_active: true,
      is_superuser: false,
      is_verified: !!user.confirmed_at,
    };
  }

  // Login via Supabase email/password
  async login(data: LoginRequest): Promise<AuthResponse> {
    const { data: signInData, error } = await this.supabase.auth.signInWithPassword({
      email: data.username,
      password: data.password,
    });
    if (error) throw new Error(error.message);
    const token = signInData.session?.access_token;
    if (!token) throw new Error('No access token returned');
    this.setToken(token);
    return { access_token: token, token_type: 'bearer' };
  }

  // Logout user (Supabase)
  async logout(): Promise<void> {
    try {
      await this.supabase.auth.signOut();
    } finally {
      this.clearToken();
    }
  }

  // Get current user info via Supabase; falls back to backend if needed
  async getCurrentUser(): Promise<AuthUser> {
    const { data } = await this.supabase.auth.getUser();
    const u = data.user;
    if (!u) throw new Error('Not authenticated');
    return {
      id: u.id,
      email: u.email ?? '',
      name: (u.user_metadata as any)?.name,
      avatar: undefined,
      is_active: true,
      is_superuser: false,
      is_verified: !!u.confirmed_at,
    };
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
