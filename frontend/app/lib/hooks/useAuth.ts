import { useState } from 'react';

interface User {
  id: string;
  email: string;
  first_name: string;
  last_name: string;
}

export const useAuth = () => {
  const [user, setUser] = useState<User | null>(null);
  const [isLoading, setIsLoading] = useState(false);

  const login = async (credentials: Record<string, unknown>) => {
    setIsLoading(true);
    try {
      // Mock login - will be implemented later
      console.log('Login:', credentials);
      return { success: true, user: null };
    } catch {
      return { success: false, error: 'Login failed' };
    } finally {
      setIsLoading(false);
    }
  };

  const register = async (userData: Record<string, unknown>) => {
    setIsLoading(true);
    try {
      // Mock register - will be implemented later
      console.log('Register:', userData);
      return { success: true, user: null };
    } catch {
      return { success: false, error: 'Registration failed' };
    } finally {
      setIsLoading(false);
    }
  };

  const logout = async () => {
    setUser(null);
  };

  const updateProfile = async (profileData: Record<string, unknown>) => {
    setIsLoading(true);
    try {
      // Mock update - will be implemented later
      console.log('Update profile:', profileData);
      return { success: true, user: null };
    } catch {
      return { success: false, error: 'Profile update failed' };
    } finally {
      setIsLoading(false);
    }
  };

  return {
    user,
    isAuthenticated: !!user,
    isLoading,
    login,
    register,
    logout,
    updateProfile,
  };
}; 