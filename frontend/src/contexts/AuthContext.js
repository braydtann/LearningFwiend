import React, { createContext, useContext, useState, useEffect, useCallback, useMemo } from 'react';
import { edgeCompatibleFetch, showBrowserWarning } from '../utils/browserCompat';

// Edge compatibility check and polyfill
if (typeof Promise === 'undefined') {
  console.error('Promise not supported. Please use a modern browser or add polyfills.');
}

// Edge fetch polyfill check
if (typeof fetch === 'undefined') {
  console.error('Fetch API not supported. Please use a modern browser.');
}

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

  const backendUrl = useMemo(() => 
    process.env.REACT_APP_BACKEND_URL, 
    []
  );
  console.log('AUTH CONTEXT DEBUG - Backend URL:', backendUrl);

  useEffect(() => {
    // Show browser compatibility warning if needed
    showBrowserWarning();
    
    // Check if user is already authenticated
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
        method: 'GET',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json',
          'Accept': 'application/json',
          'Cache-Control': 'no-cache'
        },
        credentials: 'same-origin',
        cache: 'no-cache'
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

  const checkProgramAccess = async (programId) => {
    try {
      const token = localStorage.getItem('auth_token');
      const response = await fetch(`${backendUrl}/api/programs/${programId}/access-check`, {
        headers: {
          'Authorization': `Bearer ${token}`
        }
      });

      if (response.ok) {
        const accessInfo = await response.json();
        return { success: true, ...accessInfo };
      } else {
        const errorData = await response.json();
        return { 
          success: false, 
          hasAccess: false,
          error: errorData.detail || 'Failed to check program access' 
        };
      }
    } catch (error) {
      console.error('Check program access error:', error);
      return { 
        success: false, 
        hasAccess: false,
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

  const updateCourse = async (courseId, courseData) => {
    try {
      const token = localStorage.getItem('auth_token');
      const response = await fetch(`${backendUrl}/api/courses/${courseId}`, {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify(courseData),
      });

      if (response.ok) {
        const updatedCourse = await response.json();
        return { success: true, course: updatedCourse };
      } else {
        const errorData = await response.json();
        return { 
          success: false, 
          error: errorData.detail || 'Failed to update course' 
        };
      }
    } catch (error) {
      console.error('Update course error:', error);
      return { 
        success: false, 
        error: 'Network error. Please try again.' 
      };
    }
  };

  const deleteCourse = async (courseId) => {
    try {
      const token = localStorage.getItem('auth_token');
      const response = await fetch(`${backendUrl}/api/courses/${courseId}`, {
        method: 'DELETE',
        headers: {
          'Authorization': `Bearer ${token}`
        },
      });

      if (response.ok) {
        return { success: true, message: 'Course deleted successfully' };
      } else {
        const errorData = await response.json();
        return { 
          success: false, 
          error: errorData.detail || 'Failed to delete course' 
        };
      }
    } catch (error) {
      console.error('Delete course error:', error);
      return { 
        success: false, 
        error: 'Network error. Please try again.' 
      };
    }
  };

  const getAllCourses = async () => {
    try {
      const token = localStorage.getItem('auth_token');
      
      // Use Edge-compatible fetch
      const response = await edgeCompatibleFetch(`${backendUrl}/api/courses`, {
        method: 'GET',
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

  const getCourseById = useCallback(async (courseId) => {
    try {
      const token = localStorage.getItem('auth_token');
      const response = await fetch(`${backendUrl}/api/courses/${courseId}`, {
        headers: {
          'Authorization': `Bearer ${token}`
        }
      });

      if (response.ok) {
        const course = await response.json();
        return { success: true, course };
      } else {
        const errorData = await response.json();
        return { 
          success: false, 
          error: errorData.detail || 'Failed to fetch course' 
        };
      }
    } catch (error) {
      console.error('Fetch course error:', error);
      return { 
        success: false, 
        error: 'Network error. Please try again.' 
      };
    }
  }, [backendUrl]);

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

  const getProgramById = async (programId) => {
    try {
      const token = localStorage.getItem('auth_token');
      const response = await fetch(`${backendUrl}/api/programs/${programId}`, {
        headers: {
          'Authorization': `Bearer ${token}`
        }
      });

      if (response.ok) {
        const program = await response.json();
        return { success: true, program };
      } else {
        const errorData = await response.json();
        return { 
          success: false, 
          error: errorData.detail || 'Failed to fetch program' 
        };
      }
    } catch (error) {
      console.error('Fetch program error:', error);
      return { 
        success: false, 
        error: 'Network error. Please try again.' 
      };
    }
  };

  const updateProgram = async (programId, programData) => {
    try {
      const token = localStorage.getItem('auth_token');
      const response = await fetch(`${backendUrl}/api/programs/${programId}`, {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify(programData),
      });

      if (response.ok) {
        const updatedProgram = await response.json();
        return { success: true, program: updatedProgram };
      } else {
        const errorData = await response.json();
        return { 
          success: false, 
          error: errorData.detail || 'Failed to update program' 
        };
      }
    } catch (error) {
      console.error('Update program error:', error);
      return { 
        success: false, 
        error: 'Network error. Please try again.' 
      };
    }
  };

  const deleteProgram = async (programId) => {
    try {
      const token = localStorage.getItem('auth_token');
      const response = await fetch(`${backendUrl}/api/programs/${programId}`, {
        method: 'DELETE',
        headers: {
          'Authorization': `Bearer ${token}`
        }
      });

      if (response.ok) {
        return { success: true };
      } else {
        const errorData = await response.json();
        return { 
          success: false, 
          error: errorData.detail || 'Failed to delete program' 
        };
      }
    } catch (error) {
      console.error('Delete program error:', error);
      return { 
        success: false, 
        error: 'Network error. Please try again.' 
      };
    }
  };

  // =============================================================================
  // CATEGORY MANAGEMENT FUNCTIONS  
  // =============================================================================

  const createCategory = async (categoryData) => {
    try {
      const token = localStorage.getItem('auth_token');
      const response = await fetch(`${backendUrl}/api/categories`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify(categoryData),
      });

      if (response.ok) {
        const newCategory = await response.json();
        return { success: true, category: newCategory };
      } else {
        const errorData = await response.json();
        return { 
          success: false, 
          error: errorData.detail || 'Failed to create category' 
        };
      }
    } catch (error) {
      console.error('Create category error:', error);
      return { 
        success: false, 
        error: 'Network error. Please try again.' 
      };
    }
  };

  const getAllCategories = async () => {
    try {
      const token = localStorage.getItem('auth_token');
      const response = await fetch(`${backendUrl}/api/categories`, {
        headers: {
          'Authorization': `Bearer ${token}`
        }
      });

      if (response.ok) {
        const categories = await response.json();
        return { success: true, categories };
      } else {
        const errorData = await response.json();
        return { 
          success: false, 
          error: errorData.detail || 'Failed to fetch categories' 
        };
      }
    } catch (error) {
      console.error('Fetch categories error:', error);
      return { 
        success: false, 
        error: 'Network error. Please try again.' 
      };
    }
  };

  const getCategoryById = async (categoryId) => {
    try {
      const token = localStorage.getItem('auth_token');
      const response = await fetch(`${backendUrl}/api/categories/${categoryId}`, {
        headers: {
          'Authorization': `Bearer ${token}`
        }
      });

      if (response.ok) {
        const category = await response.json();
        return { success: true, category };
      } else {
        const errorData = await response.json();
        return { 
          success: false, 
          error: errorData.detail || 'Failed to fetch category' 
        };
      }
    } catch (error) {
      console.error('Fetch category error:', error);
      return { 
        success: false, 
        error: 'Network error. Please try again.' 
      };
    }
  };

  const updateCategory = async (categoryId, categoryData) => {
    try {
      const token = localStorage.getItem('auth_token');
      const response = await fetch(`${backendUrl}/api/categories/${categoryId}`, {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify(categoryData),
      });

      if (response.ok) {
        const updatedCategory = await response.json();
        return { success: true, category: updatedCategory };
      } else {
        const errorData = await response.json();
        return { 
          success: false, 
          error: errorData.detail || 'Failed to update category' 
        };
      }
    } catch (error) {
      console.error('Update category error:', error);
      return { 
        success: false, 
        error: 'Network error. Please try again.' 
      };
    }
  };

  const deleteCategory = async (categoryId) => {
    try {
      const token = localStorage.getItem('auth_token');
      const response = await fetch(`${backendUrl}/api/categories/${categoryId}`, {
        method: 'DELETE',
        headers: {
          'Authorization': `Bearer ${token}`
        }
      });

      if (response.ok) {
        return { success: true };
      } else {
        const errorData = await response.json();
        return { 
          success: false, 
          error: errorData.detail || 'Failed to delete category' 
        };
      }
    } catch (error) {
      console.error('Delete category error:', error);
      return { 
        success: false, 
        error: 'Network error. Please try again.' 
      };
    }
  };

  // =============================================================================
  // DEPARTMENT MANAGEMENT FUNCTIONS  
  // =============================================================================

  const createDepartment = async (departmentData) => {
    try {
      const token = localStorage.getItem('auth_token');
      const response = await fetch(`${backendUrl}/api/departments`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify(departmentData),
      });

      if (response.ok) {
        const newDepartment = await response.json();
        return { success: true, department: newDepartment };
      } else {
        const errorData = await response.json();
        return { 
          success: false, 
          error: errorData.detail || 'Failed to create department' 
        };
      }
    } catch (error) {
      console.error('Create department error:', error);
      return { 
        success: false, 
        error: 'Network error. Please try again.' 
      };
    }
  };

  const getAllDepartments = async () => {
    try {
      const token = localStorage.getItem('auth_token');
      const response = await fetch(`${backendUrl}/api/departments`, {
        headers: {
          'Authorization': `Bearer ${token}`
        }
      });

      if (response.ok) {
        const departments = await response.json();
        return { success: true, departments };
      } else {
        const errorData = await response.json();
        return { 
          success: false, 
          error: errorData.detail || 'Failed to fetch departments' 
        };
      }
    } catch (error) {
      console.error('Fetch departments error:', error);
      return { 
        success: false, 
        error: 'Network error. Please try again.' 
      };
    }
  };

  const getDepartmentById = async (departmentId) => {
    try {
      const token = localStorage.getItem('auth_token');
      const response = await fetch(`${backendUrl}/api/departments/${departmentId}`, {
        headers: {
          'Authorization': `Bearer ${token}`
        }
      });

      if (response.ok) {
        const department = await response.json();
        return { success: true, department };
      } else {
        const errorData = await response.json();
        return { 
          success: false, 
          error: errorData.detail || 'Failed to fetch department' 
        };
      }
    } catch (error) {
      console.error('Fetch department error:', error);
      return { 
        success: false, 
        error: 'Network error. Please try again.' 
      };
    }
  };

  const updateDepartment = async (departmentId, departmentData) => {
    try {
      const token = localStorage.getItem('auth_token');
      const response = await fetch(`${backendUrl}/api/departments/${departmentId}`, {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify(departmentData),
      });

      if (response.ok) {
        const updatedDepartment = await response.json();
        return { success: true, department: updatedDepartment };
      } else {
        const errorData = await response.json();
        return { 
          success: false, 
          error: errorData.detail || 'Failed to update department' 
        };
      }
    } catch (error) {
      console.error('Update department error:', error);
      return { 
        success: false, 
        error: 'Network error. Please try again.' 
      };
    }
  };

  const deleteDepartment = async (departmentId) => {
    try {
      const token = localStorage.getItem('auth_token');
      const response = await fetch(`${backendUrl}/api/departments/${departmentId}`, {
        method: 'DELETE',
        headers: {
          'Authorization': `Bearer ${token}`
        }
      });

      if (response.ok) {
        return { success: true };
      } else {
        const errorData = await response.json();
        return { 
          success: false, 
          error: errorData.detail || 'Failed to delete department' 
        };
      }
    } catch (error) {
      console.error('Delete department error:', error);
      return { 
        success: false, 
        error: 'Network error. Please try again.' 
      };
    }
  };

  // =============================================================================
  // CLASSROOM MANAGEMENT FUNCTIONS  
  // =============================================================================

  const createClassroom = async (classroomData) => {
    try {
      const token = localStorage.getItem('auth_token');
      const response = await fetch(`${backendUrl}/api/classrooms`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify(classroomData),
      });

      if (response.ok) {
        const newClassroom = await response.json();
        return { success: true, classroom: newClassroom };
      } else {
        const errorData = await response.json();
        
        // Handle different error formats
        let errorMessage = 'Failed to create classroom';
        
        if (typeof errorData.detail === 'string') {
          errorMessage = errorData.detail;
        } else if (Array.isArray(errorData.detail)) {
          // Handle Pydantic validation errors (array of error objects)
          errorMessage = errorData.detail.map(err => err.msg || 'Validation error').join(', ');
        } else if (errorData.message) {
          errorMessage = errorData.message;
        }
        
        return { 
          success: false, 
          error: errorMessage
        };
      }
    } catch (error) {
      console.error('Create classroom error:', error);
      return { 
        success: false, 
        error: 'Network error. Please try again.' 
      };
    }
  };

  const getAllClassrooms = async () => {
    try {
      const token = localStorage.getItem('auth_token');
      const response = await fetch(`${backendUrl}/api/classrooms`, {
        headers: {
          'Authorization': `Bearer ${token}`
        }
      });

      if (response.ok) {
        const classrooms = await response.json();
        return { success: true, classrooms };
      } else {
        const errorData = await response.json();
        return { 
          success: false, 
          error: errorData.detail || 'Failed to fetch classrooms' 
        };
      }
    } catch (error) {
      console.error('Fetch classrooms error:', error);
      return { 
        success: false, 
        error: 'Network error. Please try again.' 
      };
    }
  };

  const getMyClassrooms = async () => {
    try {
      const token = localStorage.getItem('auth_token');
      const response = await fetch(`${backendUrl}/api/classrooms/my-classrooms`, {
        headers: {
          'Authorization': `Bearer ${token}`
        }
      });

      if (response.ok) {
        const classrooms = await response.json();
        return { success: true, classrooms };
      } else {
        const errorData = await response.json();
        return { 
          success: false, 
          error: errorData.detail || 'Failed to fetch your classrooms' 
        };
      }
    } catch (error) {
      console.error('Fetch my classrooms error:', error);
      return { 
        success: false, 
        error: 'Network error. Please try again.' 
      };
    }
  };

  const getClassroomById = async (classroomId) => {
    try {
      const token = localStorage.getItem('auth_token');
      const response = await fetch(`${backendUrl}/api/classrooms/${classroomId}`, {
        headers: {
          'Authorization': `Bearer ${token}`
        }
      });

      if (response.ok) {
        const classroom = await response.json();
        return { success: true, classroom };
      } else {
        const errorData = await response.json();
        return { 
          success: false, 
          error: errorData.detail || 'Failed to fetch classroom' 
        };
      }
    } catch (error) {
      console.error('Fetch classroom error:', error);
      return { 
        success: false, 
        error: 'Network error. Please try again.' 
      };
    }
  };

  const updateClassroom = async (classroomId, classroomData) => {
    try {
      const token = localStorage.getItem('auth_token');
      const response = await fetch(`${backendUrl}/api/classrooms/${classroomId}`, {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify(classroomData),
      });

      if (response.ok) {
        const updatedClassroom = await response.json();
        return { success: true, classroom: updatedClassroom };
      } else {
        const errorData = await response.json();
        return { 
          success: false, 
          error: errorData.detail || 'Failed to update classroom' 
        };
      }
    } catch (error) {
      console.error('Update classroom error:', error);
      return { 
        success: false, 
        error: 'Network error. Please try again.' 
      };
    }
  };

  const getClassroomStudents = async (classroomId) => {
    try {
      const token = localStorage.getItem('auth_token');
      const response = await fetch(`${backendUrl}/api/classrooms/${classroomId}/students`, {
        headers: {
          'Authorization': `Bearer ${token}`
        }
      });

      if (response.ok) {
        const students = await response.json();
        return { success: true, students };
      } else {
        const errorData = await response.json();
        return { 
          success: false, 
          error: errorData.detail || 'Failed to fetch classroom students' 
        };
      }
    } catch (error) {
      console.error('Fetch classroom students error:', error);
      return { 
        success: false, 
        error: 'Network error. Please try again.' 
      };
    }
  };

  const deleteClassroom = async (classroomId) => {
    try {
      const token = localStorage.getItem('auth_token');
      const response = await fetch(`${backendUrl}/api/classrooms/${classroomId}`, {
        method: 'DELETE',
        headers: {
          'Authorization': `Bearer ${token}`
        }
      });

      if (response.ok) {
        return { success: true };
      } else {
        const errorData = await response.json();
        return { 
          success: false, 
          error: errorData.detail || 'Failed to delete classroom' 
        };
      }
    } catch (error) {
      console.error('Delete classroom error:', error);
      return { 
        success: false, 
        error: 'Network error. Please try again.' 
      };
    }
  };

  // =============================================================================
  // ENROLLMENT MANAGEMENT FUNCTIONS  
  // =============================================================================

  const createEnrollment = async (enrollmentData) => {
    try {
      const token = localStorage.getItem('auth_token');
      const response = await fetch(`${backendUrl}/api/enrollments`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify(enrollmentData),
      });

      if (response.ok) {
        const newEnrollment = await response.json();
        return { success: true, enrollment: newEnrollment };
      } else {
        const errorData = await response.json();
        return { 
          success: false, 
          error: errorData.detail || 'Failed to create enrollment' 
        };
      }
    } catch (error) {
      console.error('Create enrollment error:', error);
      return { 
        success: false, 
        error: 'Network error. Please try again.' 
      };
    }
  };

  const createBulkEnrollments = async (bulkEnrollmentData) => {
    try {
      const token = localStorage.getItem('auth_token');
      const response = await fetch(`${backendUrl}/api/enrollments/bulk`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify(bulkEnrollmentData),
      });

      if (response.ok) {
        const enrollments = await response.json();
        return { success: true, enrollments };
      } else {
        const errorData = await response.json();
        return { 
          success: false, 
          error: errorData.detail || 'Failed to create bulk enrollments' 
        };
      }
    } catch (error) {
      console.error('Create bulk enrollments error:', error);
      return { 
        success: false, 
        error: 'Network error. Please try again.' 
      };
    }
  };

  const getAllEnrollments = async () => {
    try {
      const token = localStorage.getItem('auth_token');
      const response = await fetch(`${backendUrl}/api/enrollments`, {
        headers: {
          'Authorization': `Bearer ${token}`
        }
      });

      if (response.ok) {
        const enrollments = await response.json();
        return { success: true, enrollments };
      } else {
        const errorData = await response.json();
        return { 
          success: false, 
          error: errorData.detail || 'Failed to fetch enrollments' 
        };
      }
    } catch (error) {
      console.error('Fetch enrollments error:', error);
      return { 
        success: false, 
        error: 'Network error. Please try again.' 
      };
    }
  };

  // New method for admin/instructor analytics - gets ALL enrollments
  const getAllEnrollmentsForAnalytics = async () => {
    try {
      const token = localStorage.getItem('auth_token');
      const response = await fetch(`${backendUrl}/api/admin/enrollments`, {
        headers: {
          'Authorization': `Bearer ${token}`
        }
      });

      if (response.ok) {
        const enrollments = await response.json();
        return { success: true, enrollments };
      } else {
        const errorData = await response.json();
        return { 
          success: false, 
          error: errorData.detail || 'Failed to fetch all enrollments' 
        };
      }
    } catch (error) {
      console.error('Fetch all enrollments error:', error);
      return { 
        success: false, 
        error: 'Network error. Please try again.' 
      };
    }
  };

  const getMyEnrollments = async () => {
    try {
      const token = localStorage.getItem('auth_token');
      const response = await fetch(`${backendUrl}/api/enrollments`, {
        headers: {
          'Authorization': `Bearer ${token}`
        }
      });

      if (response.ok) {
        const enrollments = await response.json();
        return { success: true, enrollments };
      } else {
        const errorData = await response.json();
        return { 
          success: false, 
          error: errorData.detail || 'Failed to fetch your enrollments' 
        };
      }
    } catch (error) {
      console.error('Fetch my enrollments error:', error);
      return { 
        success: false, 
        error: 'Network error. Please try again.' 
      };
    }
  };

  const getCourseEnrollments = async (courseId) => {
    try {
      const token = localStorage.getItem('auth_token');
      const response = await fetch(`${backendUrl}/api/enrollments/course/${courseId}`, {
        headers: {
          'Authorization': `Bearer ${token}`
        }
      });

      if (response.ok) {
        const enrollments = await response.json();
        return { success: true, enrollments };
      } else {
        const errorData = await response.json();
        return { 
          success: false, 
          error: errorData.detail || 'Failed to fetch course enrollments' 
        };
      }
    } catch (error) {
      console.error('Fetch course enrollments error:', error);
      return { 
        success: false, 
        error: 'Network error. Please try again.' 
      };
    }
  };

  const getStudentEnrollments = async (studentId) => {
    try {
      const token = localStorage.getItem('auth_token');
      const response = await fetch(`${backendUrl}/api/enrollments/student/${studentId}`, {
        headers: {
          'Authorization': `Bearer ${token}`
        }
      });

      if (response.ok) {
        const enrollments = await response.json();
        return { success: true, enrollments };
      } else {
        const errorData = await response.json();
        return { 
          success: false, 
          error: errorData.detail || 'Failed to fetch student enrollments' 
        };
      }
    } catch (error) {
      console.error('Fetch student enrollments error:', error);
      return { 
        success: false, 
        error: 'Network error. Please try again.' 
      };
    }
  };

  const updateEnrollment = async (enrollmentId, enrollmentData) => {
    try {
      const token = localStorage.getItem('auth_token');
      const response = await fetch(`${backendUrl}/api/enrollments/${enrollmentId}`, {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify(enrollmentData),
      });

      if (response.ok) {
        const updatedEnrollment = await response.json();
        return { success: true, enrollment: updatedEnrollment };
      } else {
        const errorData = await response.json();
        return { 
          success: false, 
          error: errorData.detail || 'Failed to update enrollment' 
        };
      }
    } catch (error) {
      console.error('Update enrollment error:', error);
      return { 
        success: false, 
        error: 'Network error. Please try again.' 
      };
    }
  };

  const updateEnrollmentProgress = useCallback(async (courseId, progressData) => {
    try {
      const token = localStorage.getItem('auth_token');
      const response = await fetch(`${backendUrl}/api/enrollments/${courseId}/progress`, {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify(progressData),
      });

      if (response.ok) {
        const updatedEnrollment = await response.json();
        return { success: true, enrollment: updatedEnrollment };
      } else {
        const errorData = await response.json();
        return { 
          success: false, 
          error: errorData.detail || 'Failed to update enrollment progress' 
        };
      }
    } catch (error) {
      console.error('Update enrollment progress error:', error);
      return { 
        success: false, 
        error: 'Network error. Please try again.' 
      };
    }
  }, [backendUrl]);

  const uploadFile = async (file) => {
    try {
      const token = localStorage.getItem('auth_token');
      const formData = new FormData();
      formData.append('file', file);
      
      const response = await fetch(`${backendUrl}/api/files/upload`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`
        },
        body: formData
      });

      if (response.ok) {
        const result = await response.json();
        return { 
          success: true, 
          fileUrl: `${backendUrl}${result.file_url}`,
          fileName: result.filename,
          fileId: result.file_id
        };
      } else {
        const errorData = await response.json();
        return { 
          success: false, 
          error: errorData.detail || 'File upload failed' 
        };
      }
    } catch (error) {
      console.error('File upload error:', error);
      return { 
        success: false, 
        error: 'Network error. Please try again.' 
      };
    }
  };

  const migrateEnrollmentProgress = async (enrollmentId) => {
    try {
      const token = localStorage.getItem('auth_token');
      const response = await fetch(`${backendUrl}/api/enrollments/${enrollmentId}/migrate-progress`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        },
      });

      if (response.ok) {
        const result = await response.json();
        return { success: true, result };
      } else {
        const errorData = await response.json();
        return { 
          success: false, 
          error: errorData.detail || 'Failed to migrate enrollment progress' 
        };
      }
    } catch (error) {
      console.error('Migrate enrollment progress error:', error);
      return { 
        success: false, 
        error: 'Network error. Please try again.' 
      };
    }
  };

  const deleteEnrollment = async (enrollmentId) => {
    try {
      const token = localStorage.getItem('auth_token');
      const response = await fetch(`${backendUrl}/api/enrollments/${enrollmentId}`, {
        method: 'DELETE',
        headers: {
          'Authorization': `Bearer ${token}`
        }
      });

      if (response.ok) {
        return { success: true };
      } else {
        const errorData = await response.json();
        return { 
          success: false, 
          error: errorData.detail || 'Failed to delete enrollment' 
        };
      }
    } catch (error) {
      console.error('Delete enrollment error:', error);
      return { 
        success: false, 
        error: 'Network error. Please try again.' 
      };
    }
  };

  // =============================================================================
  // ANNOUNCEMENT MANAGEMENT FUNCTIONS  
  // =============================================================================

  const createAnnouncement = async (announcementData) => {
    try {
      const token = localStorage.getItem('auth_token');
      const response = await fetch(`${backendUrl}/api/announcements`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify(announcementData),
      });

      if (response.ok) {
        const newAnnouncement = await response.json();
        return { success: true, announcement: newAnnouncement };
      } else {
        const errorData = await response.json();
        return { 
          success: false, 
          error: errorData.detail || 'Failed to create announcement' 
        };
      }
    } catch (error) {
      console.error('Create announcement error:', error);
      return { 
        success: false, 
        error: 'Network error. Please try again.' 
      };
    }
  };

  const getAllAnnouncements = async (filters = {}) => {
    try {
      const token = localStorage.getItem('auth_token');
      const queryParams = new URLSearchParams();
      
      if (filters.type) queryParams.append('type', filters.type);
      if (filters.priority) queryParams.append('priority', filters.priority);
      if (filters.course_id) queryParams.append('course_id', filters.course_id);
      if (filters.limit) queryParams.append('limit', filters.limit);
      
      const url = `${backendUrl}/api/announcements${queryParams.toString() ? '?' + queryParams.toString() : ''}`;
      
      const response = await fetch(url, {
        headers: {
          'Authorization': `Bearer ${token}`
        }
      });

      if (response.ok) {
        const announcements = await response.json();
        return { success: true, announcements };
      } else {
        const errorData = await response.json();
        return { 
          success: false, 
          error: errorData.detail || 'Failed to fetch announcements' 
        };
      }
    } catch (error) {
      console.error('Fetch announcements error:', error);
      return { 
        success: false, 
        error: 'Network error. Please try again.' 
      };
    }
  };

  const getMyAnnouncements = async () => {
    try {
      const token = localStorage.getItem('auth_token');
      const response = await fetch(`${backendUrl}/api/announcements/my-announcements`, {
        headers: {
          'Authorization': `Bearer ${token}`
        }
      });

      if (response.ok) {
        const announcements = await response.json();
        return { success: true, announcements };
      } else {
        const errorData = await response.json();
        return { 
          success: false, 
          error: errorData.detail || 'Failed to fetch your announcements' 
        };
      }
    } catch (error) {
      console.error('Fetch my announcements error:', error);
      return { 
        success: false, 
        error: 'Network error. Please try again.' 
      };
    }
  };

  const getAnnouncementById = async (announcementId) => {
    try {
      const token = localStorage.getItem('auth_token');
      const response = await fetch(`${backendUrl}/api/announcements/${announcementId}`, {
        headers: {
          'Authorization': `Bearer ${token}`
        }
      });

      if (response.ok) {
        const announcement = await response.json();
        return { success: true, announcement };
      } else {
        const errorData = await response.json();
        return { 
          success: false, 
          error: errorData.detail || 'Failed to fetch announcement' 
        };
      }
    } catch (error) {
      console.error('Fetch announcement error:', error);
      return { 
        success: false, 
        error: 'Network error. Please try again.' 
      };
    }
  };

  const updateAnnouncement = async (announcementId, announcementData) => {
    try {
      const token = localStorage.getItem('auth_token');
      const response = await fetch(`${backendUrl}/api/announcements/${announcementId}`, {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify(announcementData),
      });

      if (response.ok) {
        const updatedAnnouncement = await response.json();
        return { success: true, announcement: updatedAnnouncement };
      } else {
        const errorData = await response.json();
        return { 
          success: false, 
          error: errorData.detail || 'Failed to update announcement' 
        };
      }
    } catch (error) {
      console.error('Update announcement error:', error);
      return { 
        success: false, 
        error: 'Network error. Please try again.' 
      };
    }
  };

  const deleteAnnouncement = async (announcementId) => {
    try {
      const token = localStorage.getItem('auth_token');
      const response = await fetch(`${backendUrl}/api/announcements/${announcementId}`, {
        method: 'DELETE',
        headers: {
          'Authorization': `Bearer ${token}`
        }
      });

      if (response.ok) {
        return { success: true };
      } else {
        const errorData = await response.json();
        return { 
          success: false, 
          error: errorData.detail || 'Failed to delete announcement' 
        };
      }
    } catch (error) {
      console.error('Delete announcement error:', error);
      return { 
        success: false, 
        error: 'Network error. Please try again.' 
      };
    }
  };

  const togglePinAnnouncement = async (announcementId) => {
    try {
      const token = localStorage.getItem('auth_token');
      const response = await fetch(`${backendUrl}/api/announcements/${announcementId}/pin`, {
        method: 'PUT',
        headers: {
          'Authorization': `Bearer ${token}`
        }
      });

      if (response.ok) {
        return { success: true };
      } else {
        const errorData = await response.json();
        return { 
          success: false, 
          error: errorData.detail || 'Failed to toggle pin status' 
        };
      }
    } catch (error) {
      console.error('Toggle pin announcement error:', error);
      return { 
        success: false, 
        error: 'Network error. Please try again.' 
      };
    }
  };

  // =============================================================================
  // CERTIFICATE MANAGEMENT FUNCTIONS  
  // =============================================================================

  const createCertificate = async (certificateData) => {
    try {
      const token = localStorage.getItem('auth_token');
      const response = await fetch(`${backendUrl}/api/certificates`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify(certificateData),
      });

      if (response.ok) {
        const newCertificate = await response.json();
        return { success: true, certificate: newCertificate };
      } else {
        const errorData = await response.json();
        return { 
          success: false, 
          error: errorData.detail || 'Failed to create certificate' 
        };
      }
    } catch (error) {
      console.error('Create certificate error:', error);
      return { 
        success: false, 
        error: 'Network error. Please try again.' 
      };
    }
  };

  const getAllCertificates = async (filters = {}) => {
    try {
      const token = localStorage.getItem('auth_token');
      const queryParams = new URLSearchParams();
      
      if (filters.student_id) queryParams.append('student_id', filters.student_id);
      if (filters.course_id) queryParams.append('course_id', filters.course_id);
      if (filters.program_id) queryParams.append('program_id', filters.program_id);
      if (filters.type) queryParams.append('type', filters.type);
      if (filters.status) queryParams.append('status', filters.status);
      
      const url = `${backendUrl}/api/certificates${queryParams.toString() ? '?' + queryParams.toString() : ''}`;
      
      const response = await fetch(url, {
        headers: {
          'Authorization': `Bearer ${token}`
        }
      });

      if (response.ok) {
        const certificates = await response.json();
        return { success: true, certificates };
      } else {
        const errorData = await response.json();
        return { 
          success: false, 
          error: errorData.detail || 'Failed to fetch certificates' 
        };
      }
    } catch (error) {
      console.error('Fetch certificates error:', error);
      return { 
        success: false, 
        error: 'Network error. Please try again.' 
      };
    }
  };

  const getMyCertificates = async () => {
    try {
      const token = localStorage.getItem('auth_token');
      const response = await fetch(`${backendUrl}/api/certificates/my-certificates`, {
        headers: {
          'Authorization': `Bearer ${token}`
        }
      });

      if (response.ok) {
        const certificates = await response.json();
        return { success: true, certificates };
      } else {
        const errorData = await response.json();
        return { 
          success: false, 
          error: errorData.detail || 'Failed to fetch your certificates' 
        };
      }
    } catch (error) {
      console.error('Fetch my certificates error:', error);
      return { 
        success: false, 
        error: 'Network error. Please try again.' 
      };
    }
  };

  const getCertificateById = async (certificateId) => {
    try {
      const token = localStorage.getItem('auth_token');
      const response = await fetch(`${backendUrl}/api/certificates/${certificateId}`, {
        headers: {
          'Authorization': `Bearer ${token}`
        }
      });

      if (response.ok) {
        const certificate = await response.json();
        return { success: true, certificate };
      } else {
        const errorData = await response.json();
        return { 
          success: false, 
          error: errorData.detail || 'Failed to fetch certificate' 
        };
      }
    } catch (error) {
      console.error('Fetch certificate error:', error);
      return { 
        success: false, 
        error: 'Network error. Please try again.' 
      };
    }
  };

  const verifyCertificate = async (verificationCode) => {
    try {
      const response = await fetch(`${backendUrl}/api/certificates/verify/${verificationCode}`);

      if (response.ok) {
        const verificationResult = await response.json();
        return { success: true, verification: verificationResult };
      } else {
        const errorData = await response.json();
        return { 
          success: false, 
          error: errorData.detail || 'Failed to verify certificate' 
        };
      }
    } catch (error) {
      console.error('Verify certificate error:', error);
      return { 
        success: false, 
        error: 'Network error. Please try again.' 
      };
    }
  };

  const updateCertificate = async (certificateId, certificateData) => {
    try {
      const token = localStorage.getItem('auth_token');
      const response = await fetch(`${backendUrl}/api/certificates/${certificateId}`, {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify(certificateData),
      });

      if (response.ok) {
        const updatedCertificate = await response.json();
        return { success: true, certificate: updatedCertificate };
      } else {
        const errorData = await response.json();
        return { 
          success: false, 
          error: errorData.detail || 'Failed to update certificate' 
        };
      }
    } catch (error) {
      console.error('Update certificate error:', error);
      return { 
        success: false, 
        error: 'Network error. Please try again.' 
      };
    }
  };

  const revokeCertificate = async (certificateId) => {
    try {
      const token = localStorage.getItem('auth_token');
      const response = await fetch(`${backendUrl}/api/certificates/${certificateId}`, {
        method: 'DELETE',
        headers: {
          'Authorization': `Bearer ${token}`
        }
      });

      if (response.ok) {
        return { success: true };
      } else {
        const errorData = await response.json();
        return { 
          success: false, 
          error: errorData.detail || 'Failed to revoke certificate' 
        };
      }
    } catch (error) {
      console.error('Revoke certificate error:', error);
      return { 
        success: false, 
        error: 'Network error. Please try again.' 
      };
    }
  };

  // =============================================================================
  // QUIZ/ASSESSMENT MANAGEMENT FUNCTIONS  
  // =============================================================================

  const createQuiz = async (quizData) => {
    try {
      const token = localStorage.getItem('auth_token');
      const response = await fetch(`${backendUrl}/api/quizzes`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify(quizData),
      });

      if (response.ok) {
        const newQuiz = await response.json();
        return { success: true, quiz: newQuiz };
      } else {
        const errorData = await response.json();
        return { 
          success: false, 
          error: errorData.detail || 'Failed to create quiz' 
        };
      }
    } catch (error) {
      console.error('Create quiz error:', error);
      return { 
        success: false, 
        error: 'Network error. Please try again.' 
      };
    }
  };

  const getAllQuizzes = async (filters = {}) => {
    try {
      const token = localStorage.getItem('auth_token');
      const queryParams = new URLSearchParams();
      
      if (filters.course_id) queryParams.append('course_id', filters.course_id);
      if (filters.program_id) queryParams.append('program_id', filters.program_id);
      if (filters.published_only !== undefined) queryParams.append('published_only', filters.published_only);
      
      const url = `${backendUrl}/api/quizzes${queryParams.toString() ? '?' + queryParams.toString() : ''}`;
      
      const response = await fetch(url, {
        headers: {
          'Authorization': `Bearer ${token}`
        }
      });

      if (response.ok) {
        const quizzes = await response.json();
        return { success: true, quizzes };
      } else {
        const errorData = await response.json();
        return { 
          success: false, 
          error: errorData.detail || 'Failed to fetch quizzes' 
        };
      }
    } catch (error) {
      console.error('Fetch quizzes error:', error);
      return { 
        success: false, 
        error: 'Network error. Please try again.' 
      };
    }
  };

  const getMyQuizzes = async () => {
    try {
      const token = localStorage.getItem('auth_token');
      const response = await fetch(`${backendUrl}/api/quizzes/my-quizzes`, {
        headers: {
          'Authorization': `Bearer ${token}`
        }
      });

      if (response.ok) {
        const quizzes = await response.json();
        return { success: true, quizzes };
      } else {
        const errorData = await response.json();
        return { 
          success: false, 
          error: errorData.detail || 'Failed to fetch your quizzes' 
        };
      }
    } catch (error) {
      console.error('Fetch my quizzes error:', error);
      return { 
        success: false, 
        error: 'Network error. Please try again.' 
      };
    }
  };

  const getQuizById = async (quizId, includeAnswers = false) => {
    try {
      const token = localStorage.getItem('auth_token');
      const url = `${backendUrl}/api/quizzes/${quizId}${includeAnswers ? '?include_answers=true' : ''}`;
      
      const response = await fetch(url, {
        headers: {
          'Authorization': `Bearer ${token}`
        }
      });

      if (response.ok) {
        const quiz = await response.json();
        return { success: true, quiz };
      } else {
        const errorData = await response.json();
        return { 
          success: false, 
          error: errorData.detail || 'Failed to fetch quiz' 
        };
      }
    } catch (error) {
      console.error('Fetch quiz error:', error);
      return { 
        success: false, 
        error: 'Network error. Please try again.' 
      };
    }
  };

  const updateQuiz = async (quizId, quizData) => {
    try {
      const token = localStorage.getItem('auth_token');
      const response = await fetch(`${backendUrl}/api/quizzes/${quizId}`, {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify(quizData),
      });

      if (response.ok) {
        const updatedQuiz = await response.json();
        return { success: true, quiz: updatedQuiz };
      } else {
        const errorData = await response.json();
        return { 
          success: false, 
          error: errorData.detail || 'Failed to update quiz' 
        };
      }
    } catch (error) {
      console.error('Update quiz error:', error);
      return { 
        success: false, 
        error: 'Network error. Please try again.' 
      };
    }
  };

  const deleteQuiz = async (quizId) => {
    try {
      const token = localStorage.getItem('auth_token');
      const response = await fetch(`${backendUrl}/api/quizzes/${quizId}`, {
        method: 'DELETE',
        headers: {
          'Authorization': `Bearer ${token}`
        }
      });

      if (response.ok) {
        return { success: true };
      } else {
        const errorData = await response.json();
        return { 
          success: false, 
          error: errorData.detail || 'Failed to delete quiz' 
        };
      }
    } catch (error) {
      console.error('Delete quiz error:', error);
      return { 
        success: false, 
        error: 'Network error. Please try again.' 
      };
    }
  };

  const submitQuizAttempt = async (attemptData) => {
    try {
      const token = localStorage.getItem('auth_token');
      const response = await fetch(`${backendUrl}/api/quiz-attempts`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify(attemptData),
      });

      if (response.ok) {
        const attempt = await response.json();
        return { success: true, attempt };
      } else {
        const errorData = await response.json();
        return { 
          success: false, 
          error: errorData.detail || 'Failed to submit quiz attempt' 
        };
      }
    } catch (error) {
      console.error('Submit quiz attempt error:', error);
      return { 
        success: false, 
        error: 'Network error. Please try again.' 
      };
    }
  };

  const getQuizAttempts = async (filters = {}) => {
    try {
      const token = localStorage.getItem('auth_token');
      const queryParams = new URLSearchParams();
      
      if (filters.quiz_id) queryParams.append('quiz_id', filters.quiz_id);
      if (filters.student_id) queryParams.append('student_id', filters.student_id);
      
      const url = `${backendUrl}/api/quiz-attempts${queryParams.toString() ? '?' + queryParams.toString() : ''}`;
      
      const response = await fetch(url, {
        headers: {
          'Authorization': `Bearer ${token}`
        }
      });

      if (response.ok) {
        const attempts = await response.json();
        return { success: true, attempts };
      } else {
        const errorData = await response.json();
        return { 
          success: false, 
          error: errorData.detail || 'Failed to fetch quiz attempts' 
        };
      }
    } catch (error) {
      console.error('Fetch quiz attempts error:', error);
      return { 
        success: false, 
        error: 'Network error. Please try again.' 
      };
    }
  };

  const getQuizAttemptById = async (attemptId) => {
    try {
      const token = localStorage.getItem('auth_token');
      const response = await fetch(`${backendUrl}/api/quiz-attempts/${attemptId}`, {
        headers: {
          'Authorization': `Bearer ${token}`
        }
      });

      if (response.ok) {
        const attempt = await response.json();
        return { success: true, attempt };
      } else {
        const errorData = await response.json();
        return { 
          success: false, 
          error: errorData.detail || 'Failed to fetch quiz attempt' 
        };
      }
    } catch (error) {
      console.error('Fetch quiz attempt error:', error);
      return { 
        success: false, 
        error: 'Network error. Please try again.' 
      };
    }
  };

  // =============================================================================
  // FINAL TEST MANAGEMENT FUNCTIONS (PROGRAM-LEVEL TESTS)
  // =============================================================================

  const createFinalTest = async (testData) => {
    try {
      const token = localStorage.getItem('auth_token');
      const response = await fetch(`${backendUrl}/api/final-tests`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify(testData),
      });

      if (response.ok) {
        const newTest = await response.json();
        return { success: true, test: newTest };
      } else {
        const errorData = await response.json();
        return { 
          success: false, 
          error: errorData.detail || 'Failed to create final test' 
        };
      }
    } catch (error) {
      console.error('Create final test error:', error);
      return { 
        success: false, 
        error: 'Network error. Please try again.' 
      };
    }
  };

  const getAllFinalTests = async (filters = {}) => {
    try {
      const token = localStorage.getItem('auth_token');
      const queryParams = new URLSearchParams();
      
      if (filters.program_id) queryParams.append('program_id', filters.program_id);
      if (filters.published_only !== undefined) queryParams.append('published_only', filters.published_only);
      
      const url = `${backendUrl}/api/final-tests${queryParams.toString() ? '?' + queryParams.toString() : ''}`;
      
      const response = await fetch(url, {
        headers: {
          'Authorization': `Bearer ${token}`
        }
      });

      if (response.ok) {
        const tests = await response.json();
        return { success: true, tests };
      } else {
        const errorData = await response.json();
        return { 
          success: false, 
          error: errorData.detail || 'Failed to fetch final tests' 
        };
      }
    } catch (error) {
      console.error('Fetch final tests error:', error);
      return { 
        success: false, 
        error: 'Network error. Please try again.' 
      };
    }
  };

  const getMyFinalTests = async () => {
    try {
      const token = localStorage.getItem('auth_token');
      const response = await fetch(`${backendUrl}/api/final-tests/my-tests`, {
        headers: {
          'Authorization': `Bearer ${token}`
        }
      });

      if (response.ok) {
        const tests = await response.json();
        return { success: true, tests };
      } else {
        const errorData = await response.json();
        return { 
          success: false, 
          error: errorData.detail || 'Failed to fetch your final tests' 
        };
      }
    } catch (error) {
      console.error('Fetch my final tests error:', error);
      return { 
        success: false, 
        error: 'Network error. Please try again.' 
      };
    }
  };

  const getFinalTestById = async (testId, includeAnswers = false) => {
    try {
      const token = localStorage.getItem('auth_token');
      const url = `${backendUrl}/api/final-tests/${testId}${includeAnswers ? '?include_answers=true' : ''}`;
      
      const response = await fetch(url, {
        headers: {
          'Authorization': `Bearer ${token}`
        }
      });

      if (response.ok) {
        const test = await response.json();
        return { success: true, test };
      } else {
        const errorData = await response.json();
        return { 
          success: false, 
          error: errorData.detail || 'Failed to fetch final test' 
        };
      }
    } catch (error) {
      console.error('Fetch final test error:', error);
      return { 
        success: false, 
        error: 'Network error. Please try again.' 
      };
    }
  };

  const updateFinalTest = async (testId, testData) => {
    try {
      const token = localStorage.getItem('auth_token');
      const response = await fetch(`${backendUrl}/api/final-tests/${testId}`, {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify(testData),
      });

      if (response.ok) {
        const updatedTest = await response.json();
        return { success: true, test: updatedTest };
      } else {
        const errorData = await response.json();
        return { 
          success: false, 
          error: errorData.detail || 'Failed to update final test' 
        };
      }
    } catch (error) {
      console.error('Update final test error:', error);
      return { 
        success: false, 
        error: 'Network error. Please try again.' 
      };
    }
  };

  const deleteFinalTest = async (testId) => {
    try {
      const token = localStorage.getItem('auth_token');
      const response = await fetch(`${backendUrl}/api/final-tests/${testId}`, {
        method: 'DELETE',
        headers: {
          'Authorization': `Bearer ${token}`
        }
      });

      if (response.ok) {
        const result = await response.json();
        return { success: true, message: result.message };
      } else {
        const errorData = await response.json();
        return { 
          success: false, 
          error: errorData.detail || 'Failed to delete final test' 
        };
      }
    } catch (error) {
      console.error('Delete final test error:', error);
      return { 
        success: false, 
        error: 'Network error. Please try again.' 
      };
    }
  };

  const submitFinalTestAttempt = async (attemptData) => {
    try {
      const token = localStorage.getItem('auth_token');
      const response = await fetch(`${backendUrl}/api/final-test-attempts`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify(attemptData),
      });

      if (response.ok) {
        const attempt = await response.json();
        return { success: true, attempt };
      } else {
        const errorData = await response.json();
        return { 
          success: false, 
          error: errorData.detail || 'Failed to submit final test attempt' 
        };
      }
    } catch (error) {
      console.error('Submit final test attempt error:', error);
      return { 
        success: false, 
        error: 'Network error. Please try again.' 
      };
    }
  };

  const getFinalTestAttempts = async (filters = {}) => {
    try {
      const token = localStorage.getItem('auth_token');
      const queryParams = new URLSearchParams();
      
      if (filters.test_id) queryParams.append('test_id', filters.test_id);
      if (filters.program_id) queryParams.append('program_id', filters.program_id);
      if (filters.student_id) queryParams.append('student_id', filters.student_id);
      
      const url = `${backendUrl}/api/final-test-attempts${queryParams.toString() ? '?' + queryParams.toString() : ''}`;
      
      const response = await fetch(url, {
        headers: {
          'Authorization': `Bearer ${token}`
        }
      });

      if (response.ok) {
        const attempts = await response.json();
        return { success: true, attempts };
      } else {
        const errorData = await response.json();
        return { 
          success: false, 
          error: errorData.detail || 'Failed to fetch final test attempts' 
        };
      }
    } catch (error) {
      console.error('Fetch final test attempts error:', error);
      return { 
        success: false, 
        error: 'Network error. Please try again.' 
      };
    }
  };

  const getFinalTestAttemptById = async (attemptId) => {
    try {
      const token = localStorage.getItem('auth_token');
      const response = await fetch(`${backendUrl}/api/final-test-attempts/${attemptId}`, {
        headers: {
          'Authorization': `Bearer ${token}`
        }
      });

      if (response.ok) {
        const attempt = await response.json();
        return { success: true, attempt };
      } else {
        const errorData = await response.json();
        return { 
          success: false, 
          error: errorData.detail || 'Failed to fetch final test attempt' 
        };
      }
    } catch (error) {
      console.error('Fetch final test attempt error:', error);
      return { 
        success: false, 
        error: 'Network error. Please try again.' 
      };
    }
  };

  // =============================================================================
  // ANALYTICS MANAGEMENT FUNCTIONS  
  // =============================================================================

  const getSystemStats = async () => {
    try {
      const token = localStorage.getItem('auth_token');
      const response = await fetch(`${backendUrl}/api/analytics/system-stats`, {
        headers: {
          'Authorization': `Bearer ${token}`
        }
      });

      if (response.ok) {
        const stats = await response.json();
        return { success: true, stats };
      } else {
        const errorData = await response.json();
        return { 
          success: false, 
          error: errorData.detail || 'Failed to fetch system statistics' 
        };
      }
    } catch (error) {
      console.error('Fetch system stats error:', error);
      return { 
        success: false, 
        error: 'Network error. Please try again.' 
      };
    }
  };

  const getCourseAnalytics = async (courseId) => {
    try {
      const token = localStorage.getItem('auth_token');
      const response = await fetch(`${backendUrl}/api/analytics/course/${courseId}`, {
        headers: {
          'Authorization': `Bearer ${token}`
        }
      });

      if (response.ok) {
        const analytics = await response.json();
        return { success: true, analytics };
      } else {
        const errorData = await response.json();
        return { 
          success: false, 
          error: errorData.detail || 'Failed to fetch course analytics' 
        };
      }
    } catch (error) {
      console.error('Fetch course analytics error:', error);
      return { 
        success: false, 
        error: 'Network error. Please try again.' 
      };
    }
  };

  const getUserAnalytics = async (userId) => {
    try {
      const token = localStorage.getItem('auth_token');
      const response = await fetch(`${backendUrl}/api/analytics/user/${userId}`, {
        headers: {
          'Authorization': `Bearer ${token}`
        }
      });

      if (response.ok) {
        const analytics = await response.json();
        return { success: true, analytics };
      } else {
        const errorData = await response.json();
        return { 
          success: false, 
          error: errorData.detail || 'Failed to fetch user analytics' 
        };
      }
    } catch (error) {
      console.error('Fetch user analytics error:', error);
      return { 
        success: false, 
        error: 'Network error. Please try again.' 
      };
    }
  };

  const getAnalyticsDashboard = async () => {
    try {
      const token = localStorage.getItem('auth_token');
      const response = await fetch(`${backendUrl}/api/analytics/dashboard`, {
        headers: {
          'Authorization': `Bearer ${token}`
        }
      });

      if (response.ok) {
        const dashboard = await response.json();
        return { success: true, dashboard: dashboard.data };
      } else {
        const errorData = await response.json();
        return { 
          success: false, 
          error: errorData.detail || 'Failed to fetch analytics dashboard' 
        };
      }
    } catch (error) {
      console.error('Fetch analytics dashboard error:', error);
      return { 
        success: false, 
        error: 'Network error. Please try again.' 
      };
    }
  };

  // =============================================================================
  // ORPHANED ENROLLMENT CLEANUP FUNCTION
  // =============================================================================

  const cleanupOrphanedEnrollments = async () => {
    try {
      const token = localStorage.getItem('auth_token');
      const response = await fetch(`${backendUrl}/api/enrollments/cleanup-orphaned`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`
        }
      });

      if (response.ok) {
        const result = await response.json();
        return { success: true, message: result.message, deletedCount: result.deletedCount };
      } else {
        const errorData = await response.json();
        return { 
          success: false, 
          error: errorData.detail || 'Failed to cleanup orphaned enrollments' 
        };
      }
    } catch (error) {
      console.error('Cleanup orphaned enrollments error:', error);
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
    // Course management
    createCourse,
    updateCourse,
    deleteCourse,
    getAllCourses,
    getMyCourses,
    getCourseById,
    enrollInCourse,
    unenrollFromCourse,
    // Program management
    createProgram,
    getAllPrograms,
    getMyPrograms,
    getProgramById,
    updateProgram,
    deleteProgram,
    checkProgramAccess,
    // Category management
    createCategory,
    getAllCategories,
    getCategoryById,
    updateCategory,
    deleteCategory,
    // Department management
    createDepartment,
    getAllDepartments,
    getDepartmentById,
    updateDepartment,
    deleteDepartment,
    // Classroom management
    createClassroom,
    getAllClassrooms,
    getMyClassrooms,
    getClassroomById,
    getClassroomStudents,
    updateClassroom,
    deleteClassroom,
    // Enrollment management
    createEnrollment,
    createBulkEnrollments,
    getAllEnrollments,
    getAllEnrollmentsForAnalytics,
    getMyEnrollments,
    getCourseEnrollments,
    getStudentEnrollments,
    updateEnrollment,
    updateEnrollmentProgress,
    uploadFile,
    migrateEnrollmentProgress,
    deleteEnrollment,
    cleanupOrphanedEnrollments,
    // Announcement management
    createAnnouncement,
    getAllAnnouncements,
    getMyAnnouncements,
    getAnnouncementById,
    updateAnnouncement,
    deleteAnnouncement,
    togglePinAnnouncement,
    // Certificate management
    createCertificate,
    getAllCertificates,
    getMyCertificates,
    getCertificateById,
    verifyCertificate,
    updateCertificate,
    revokeCertificate,
    // Quiz/Assessment management
    createQuiz,
    getAllQuizzes,
    getMyQuizzes,
    getQuizById,
    updateQuiz,
    deleteQuiz,
    submitQuizAttempt,
    getQuizAttempts,
    getQuizAttemptById,
    // Final Test management (program-level tests)
    createFinalTest,
    getAllFinalTests,
    getMyFinalTests,
    getFinalTestById,
    updateFinalTest,
    deleteFinalTest,
    submitFinalTestAttempt,
    getFinalTestAttempts,
    getFinalTestAttemptById,
    // Analytics management
    getSystemStats,
    getCourseAnalytics,
    getUserAnalytics,
    getAnalyticsDashboard,
    // User role helpers
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