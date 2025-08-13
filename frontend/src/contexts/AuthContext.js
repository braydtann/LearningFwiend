import React, { createContext, useContext, useState, useEffect } from 'react';

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
  const [requiresPasswordChange, setRequiresPasswordChange] = useState(false);

  const backendUrl = process.env.REACT_APP_BACKEND_URL;

  useEffect(() => {
    // Check if user is logged in by checking token and validating it
    checkAuthStatus();
  }, []);

  const checkAuthStatus = async () => {
    try {
      const token = localStorage.getItem('auth_token');
      if (!token) {
        setLoading(false);
        return;
      }

      // Validate token by getting current user info
      const response = await fetch(`${backendUrl}/api/auth/me`, {
        headers: {
          'Authorization': `Bearer ${token}`
        }
      });

      if (response.ok) {
        const userData = await response.json();
        setUser(userData);
        setRequiresPasswordChange(userData.first_login_required || false);
      } else {
        // Token is invalid, remove it
        localStorage.removeItem('auth_token');
        setUser(null);
      }
    } catch (error) {
      console.error('Auth check failed:', error);
      localStorage.removeItem('auth_token');
      setUser(null);
    } finally {
      setLoading(false);
    }
  };

  const login = async (usernameOrEmail, password) => {
    try {
      const response = await fetch(`${backendUrl}/api/auth/login`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          username_or_email: usernameOrEmail,
          password: password
        }),
      });

      if (response.ok) {
        const data = await response.json();
        
        // Store token
        localStorage.setItem('auth_token', data.access_token);
        
        // Set user data
        setUser(data.user);
        setRequiresPasswordChange(data.requires_password_change || false);
        
        return { 
          success: true, 
          user: data.user, 
          requires_password_change: data.requires_password_change 
        };
      } else {
        const errorData = await response.json();
        return { 
          success: false, 
          error: errorData.detail || 'Login failed' 
        };
      }
    } catch (error) {
      console.error('Login error:', error);
      return { 
        success: false, 
        error: 'Network error. Please try again.' 
      };
    }
  };

  const logout = () => {
    localStorage.removeItem('auth_token');
    setUser(null);
    setRequiresPasswordChange(false);
  };

  const changePassword = async (currentPassword, newPassword) => {
    try {
      const token = localStorage.getItem('auth_token');
      const response = await fetch(`${backendUrl}/api/auth/change-password`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify({
          current_password: currentPassword,
          new_password: newPassword
        }),
      });

      if (response.ok) {
        setRequiresPasswordChange(false);
        // Refresh user data
        await checkAuthStatus();
        return { success: true };
      } else {
        const errorData = await response.json();
        return { 
          success: false, 
          error: errorData.detail || 'Password change failed' 
        };
      }
    } catch (error) {
      console.error('Password change error:', error);
      return { 
        success: false, 
        error: 'Network error. Please try again.' 
      };
    }
  };

  const createUser = async (userData) => {
    try {
      const token = localStorage.getItem('auth_token');
      const response = await fetch(`${backendUrl}/api/auth/admin/create-user`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify(userData),
      });

      if (response.ok) {
        const newUser = await response.json();
        return { success: true, user: newUser };
      } else {
        const errorData = await response.json();
        return { 
          success: false, 
          error: errorData.detail || 'User creation failed' 
        };
      }
    } catch (error) {
      console.error('User creation error:', error);
      return { 
        success: false, 
        error: 'Network error. Please try again.' 
      };
    }
  };

  const resetUserPassword = async (userId, newTemporaryPassword) => {
    try {
      const token = localStorage.getItem('auth_token');
      const response = await fetch(`${backendUrl}/api/auth/admin/reset-password`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify({
          user_id: userId,
          new_temporary_password: newTemporaryPassword
        }),
      });

      if (response.ok) {
        const result = await response.json();
        return { success: true, data: result };
      } else {
        const errorData = await response.json();
        return { 
          success: false, 
          error: errorData.detail || 'Password reset failed' 
        };
      }
    } catch (error) {
      console.error('Password reset error:', error);
      return { 
        success: false, 
        error: 'Network error. Please try again.' 
      };
    }
  };

  const getAllUsers = async () => {
    try {
      const token = localStorage.getItem('auth_token');
      const response = await fetch(`${backendUrl}/api/auth/admin/users`, {
        headers: {
          'Authorization': `Bearer ${token}`
        }
      });

      if (response.ok) {
        const users = await response.json();
        return { success: true, users };
      } else {
        const errorData = await response.json();
        return { 
          success: false, 
          error: errorData.detail || 'Failed to fetch users' 
        };
      }
    } catch (error) {
      console.error('Fetch users error:', error);
      return { 
        success: false, 
        error: 'Network error. Please try again.' 
      };
    }
  };

  const deleteUser = async (userId) => {
    try {
      const token = localStorage.getItem('auth_token');
      const response = await fetch(`${backendUrl}/api/auth/admin/users/${userId}`, {
        method: 'DELETE',
        headers: {
          'Authorization': `Bearer ${token}`
        }
      });

      if (response.ok) {
        const result = await response.json();
        return { success: true, data: result };
      } else {
        const errorData = await response.json();
        return { 
          success: false, 
          error: errorData.detail || 'Failed to delete user' 
        };
      }
    } catch (error) {
      console.error('Delete user error:', error);
      return { 
        success: false, 
        error: 'Network error. Please try again.' 
      };
    }
  };

  const updateUser = async (userId, userData) => {
    try {
      const token = localStorage.getItem('auth_token');
      const response = await fetch(`${backendUrl}/api/auth/admin/users/${userId}`, {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify(userData),
      });

      if (response.ok) {
        const updatedUser = await response.json();
        return { success: true, user: updatedUser };
      } else {
        const errorData = await response.json();
        return { 
          success: false, 
          error: errorData.detail || 'Failed to update user' 
        };
      }
    } catch (error) {
      console.error('Update user error:', error);
      return { 
        success: false, 
        error: 'Network error. Please try again.' 
      };
    }
  };

  // =============================================================================
  // COURSE MANAGEMENT FUNCTIONS
  // =============================================================================

  const createCourse = async (courseData) => {
    try {
      const token = localStorage.getItem('auth_token');
      const response = await fetch(`${backendUrl}/api/courses`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify(courseData),
      });

      if (response.ok) {
        const newCourse = await response.json();
        return { success: true, course: newCourse };
      } else {
        const errorData = await response.json();
        return { 
          success: false, 
          error: errorData.detail || 'Failed to create course' 
        };
      }
    } catch (error) {
      console.error('Create course error:', error);
      return { 
        success: false, 
        error: 'Network error. Please try again.' 
      };
    }
  };

  const getAllCourses = async () => {
    try {
      const token = localStorage.getItem('auth_token');
      const response = await fetch(`${backendUrl}/api/courses`, {
        headers: {
          'Authorization': `Bearer ${token}`
        }
      });

      if (response.ok) {
        const courses = await response.json();
        return { success: true, courses };
      } else {
        const errorData = await response.json();
        return { 
          success: false, 
          error: errorData.detail || 'Failed to fetch courses' 
        };
      }
    } catch (error) {
      console.error('Fetch courses error:', error);
      return { 
        success: false, 
        error: 'Network error. Please try again.' 
      };
    }
  };

  const getMyCourses = async () => {
    try {
      const token = localStorage.getItem('auth_token');
      const response = await fetch(`${backendUrl}/api/courses/my-courses`, {
        headers: {
          'Authorization': `Bearer ${token}`
        }
      });

      if (response.ok) {
        const courses = await response.json();
        return { success: true, courses };
      } else {
        const errorData = await response.json();
        return { 
          success: false, 
          error: errorData.detail || 'Failed to fetch your courses' 
        };
      }
    } catch (error) {
      console.error('Fetch my courses error:', error);
      return { 
        success: false, 
        error: 'Network error. Please try again.' 
      };
    }
  };

  const enrollInCourse = async (courseId) => {
    try {
      const token = localStorage.getItem('auth_token');
      const response = await fetch(`${backendUrl}/api/enrollments`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify({ courseId }),
      });

      if (response.ok) {
        const enrollment = await response.json();
        return { success: true, enrollment };
      } else {
        const errorData = await response.json();
        return { 
          success: false, 
          error: errorData.detail || 'Failed to enroll in course' 
        };
      }
    } catch (error) {
      console.error('Enroll in course error:', error);
      return { 
        success: false, 
        error: 'Network error. Please try again.' 
      };
    }
  };

  const unenrollFromCourse = async (courseId) => {
    try {
      const token = localStorage.getItem('auth_token');
      const response = await fetch(`${backendUrl}/api/enrollments/${courseId}`, {
        method: 'DELETE',
        headers: {
          'Authorization': `Bearer ${token}`
        }
      });

      if (response.ok) {
        const result = await response.json();
        return { success: true, data: result };
      } else {
        const errorData = await response.json();
        return { 
          success: false, 
          error: errorData.detail || 'Failed to unenroll from course' 
        };
      }
    } catch (error) {
      console.error('Unenroll from course error:', error);
      return { 
        success: false, 
        error: 'Network error. Please try again.' 
      };
    }
  };

  // =============================================================================
  // PROGRAM MANAGEMENT FUNCTIONS  
  // =============================================================================

  const createProgram = async (programData) => {
    try {
      const token = localStorage.getItem('auth_token');
      const response = await fetch(`${backendUrl}/api/programs`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify(programData),
      });

      if (response.ok) {
        const newProgram = await response.json();
        return { success: true, program: newProgram };
      } else {
        const errorData = await response.json();
        return { 
          success: false, 
          error: errorData.detail || 'Failed to create program' 
        };
      }
    } catch (error) {
      console.error('Create program error:', error);
      return { 
        success: false, 
        error: 'Network error. Please try again.' 
      };
    }
  };

  const getAllPrograms = async () => {
    try {
      const token = localStorage.getItem('auth_token');
      const response = await fetch(`${backendUrl}/api/programs`, {
        headers: {
          'Authorization': `Bearer ${token}`
        }
      });

      if (response.ok) {
        const programs = await response.json();
        return { success: true, programs };
      } else {
        const errorData = await response.json();
        return { 
          success: false, 
          error: errorData.detail || 'Failed to fetch programs' 
        };
      }
    } catch (error) {
      console.error('Fetch programs error:', error);
      return { 
        success: false, 
        error: 'Network error. Please try again.' 
      };
    }
  };

  const getMyPrograms = async () => {
    try {
      const token = localStorage.getItem('auth_token');
      const response = await fetch(`${backendUrl}/api/programs/my-programs`, {
        headers: {
          'Authorization': `Bearer ${token}`
        }
      });

      if (response.ok) {
        const programs = await response.json();
        return { success: true, programs };
      } else {
        const errorData = await response.json();
        return { 
          success: false, 
          error: errorData.detail || 'Failed to fetch your programs' 
        };
      }
    } catch (error) {
      console.error('Fetch my programs error:', error);
      return { 
        success: false, 
        error: 'Network error. Please try again.' 
      };
    }
  };

  const value = {
    user,
    loading,
    requiresPasswordChange,
    login,
    logout,
    changePassword,
    createUser,
    resetUserPassword,
    getAllUsers,
    deleteUser,
    updateUser,
    checkAuthStatus,
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