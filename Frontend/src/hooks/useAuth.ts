import { createContext, useContext, useState, useCallback } from 'react';
import { authAPI } from '@/services/api';

export type UserRole = 'user' | 'admin';

export interface User {
  id: string;
  name: string;
  email: string;
  role: UserRole;
  avatar?: string;
}

export interface AuthContextType {
  user: User | null;
  isAdmin: boolean;
  login: (email: string, password: string) => Promise<boolean>;
  register: (name: string, email: string, password: string) => Promise<{ success: boolean; message?: string }>;
  logout: () => void;
  switchRole: (role: UserRole) => void;
}

export const AuthContext = createContext<AuthContextType | null>(null);

export function useAuthProvider() {
  const [user, setUser] = useState<User | null>(() => {
    const saved = localStorage.getItem('climaai_user');
    return saved ? JSON.parse(saved) : null;
  });

  const login = useCallback(async (email: string, password: string): Promise<boolean> => {
    try {
      const response = await authAPI.login(email, password);
      console.log('Login response:', response);
      
      if (response.access_token) {
        localStorage.setItem('climaai_token', response.access_token);
        console.log('✓ Token stored in localStorage:', response.access_token.substring(0, 20) + '...');
        
        const userData: User = {
          id: response.user?.id || '0',
          name: response.user?.name || email,
          email: response.user?.email || email,
          role: response.user?.role || 'user',
        };
        setUser(userData);
        localStorage.setItem('climaai_user', JSON.stringify(userData));
        console.log('✓ User data stored:', userData);
        
        // Verify token was stored
        const verifyToken = localStorage.getItem('climaai_token');
        console.log('✓ Token verification:', verifyToken ? 'SUCCESS' : 'FAILED');
        
        return true;
      }
      console.error('No access_token in response:', response);
      return false;
    } catch (error) {
      console.error('❌ Login failed:', error);
      return false;
    }
  }, []);

  const register = useCallback(
    async (name: string, email: string, password: string): Promise<{ success: boolean; message?: string }> => {
      try {
        const response = await authAPI.register({ name, email, password });
        if (response.id) {
          return { success: true, message: 'Registration successful. Please log in.' };
        }
        return { success: false, message: 'Registration failed' };
      } catch (error: any) {
        const message = error.response?.data?.detail || error.message || 'Registration failed';
        return { success: false, message };
      }
    },
    []
  );

  const logout = useCallback(() => {
    setUser(null);
    localStorage.removeItem('climaai_user');
    localStorage.removeItem('climaai_token');
  }, []);

  const switchRole = useCallback((role: UserRole) => {
    setUser((prev) => {
      if (!prev) return prev;
      const updated = { ...prev, role };
      localStorage.setItem('climaai_user', JSON.stringify(updated));
      return updated;
    });
  }, []);

  const isAdmin = user?.role === 'admin';

  return { user, isAdmin, login, register, logout, switchRole };
}

export function useAuth() {
  const ctx = useContext(AuthContext);
  if (!ctx) throw new Error('useAuth must be used within AuthProvider');
  return ctx;
}
