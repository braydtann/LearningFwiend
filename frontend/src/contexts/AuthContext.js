import React, { createContext, useContext, useState, useEffect } from 'react';
import { getCurrentUser, setCurrentUser, mockUsers } from '../data/mockData';

const AuthContext = createContext();

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};

export const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    // Load user from localStorage or set default
    const currentUser = getCurrentUser();
    setUser(currentUser);
    setLoading(false);
  }, []);

  const login = async (email, password) => {
    // Mock login - find user by email
    const foundUser = mockUsers.find(u => u.email === email);
    if (foundUser) {
      setUser(foundUser);
      setCurrentUser(foundUser);
      return { success: true, user: foundUser };
    }
    return { success: false, error: 'Invalid credentials' };
  };

  const logout = () => {
    setUser(null);
    localStorage.removeItem('currentUser');
  };

  const register = async (userData) => {
    // Mock registration
    const newUser = {
      id: Date.now().toString(),
      ...userData,
      role: userData.role || 'learner',
      joinDate: new Date().toISOString().split('T')[0],
      avatar: `https://images.unsplash.com/photo-1535713875002-d1d0cf377fde?w=100&h=100&fit=crop&crop=face`
    };

    // In real app, would save to backend
    mockUsers.push(newUser);
    setUser(newUser);
    setCurrentUser(newUser);
    return { success: true, user: newUser };
  };

  const switchRole = (role) => {
    const roleUser = mockUsers.find(u => u.role === role);
    if (roleUser) {
      setUser(roleUser);
      setCurrentUser(roleUser);
    }
  };

  const value = {
    user,
    login,
    logout,
    register,
    switchRole,
    loading,
    isAdmin: user?.role === 'admin',
    isInstructor: user?.role === 'instructor',
    isLearner: user?.role === 'learner'
  };

  return (
    <AuthContext.Provider value={value}>
      {!loading && children}
    </AuthContext.Provider>
  );
};