// Mock data for LearningFwiend LMS - CLEAN SLATE FOR PRODUCTION
// Note: Replace this mock data system with your actual database integration

// Users data - Replace with your user management system
export const mockUsers = [
  {
    id: '1',
    name: 'Admin User',
    email: 'admin@example.com',
    role: 'admin',
    department: 'Administration',
    departmentId: '1',
    joinDate: '2024-01-01',
    avatar: '/avatars/admin.jpg',
    status: 'active'
  }
];

// Departments data - Replace with your department management system  
export const mockDepartments = [
  {
    id: '1',
    name: 'Administration',
    description: 'System administration and management',
    createdAt: '2024-01-01',
    memberCount: 1
  }
];

// Course categories data - Replace with your category management system
export const mockCategories = [
  {
    id: '1',
    name: 'General',
    description: 'General purpose courses',
    createdAt: '2024-01-01',
    createdBy: '1',
    isActive: true,
    courseCount: 0
  }
];

// Courses data - Replace with your course management system
export const mockCourses = [];

// Programs data - Replace with your program management system
export const mockPrograms = [];

// Classrooms data - Replace with your classroom management system
export const mockClassrooms = [];

// Enrollments data - Replace with your enrollment tracking system
export const mockEnrollments = [];
export const mockClassroomEnrollments = [];

// Certificates data - Replace with your certificate system
export const mockCertificates = [];

// Notifications data - Replace with your notification system
export const mockNotifications = [];

// Announcements data - Replace with your announcement system
export const mockAnnouncements = [];

// Quiz attempts and results - Replace with your assessment system
export const mockQuizAttempts = [];
export const mockQuizResults = [];

// Helper functions - Update these to work with your database/API

// User management functions
export const getUsersForAdmin = () => {
  return mockUsers;
};

// Program management functions
export const getProgramsForAdmin = () => {
  return mockPrograms;
};

export const getProgramsWithDeadlineStatus = () => {
  return mockPrograms.map(program => ({
    ...program,
    deadlineStatus: 'upcoming' // Replace with actual deadline calculation
  }));
};

export const getProgramDeadlineStatus = (deadline) => {
  if (!deadline) return 'none';
  const deadlineDate = new Date(deadline);
  const now = new Date();
  const daysUntilDeadline = Math.ceil((deadlineDate - now) / (1000 * 60 * 60 * 24));
  
  if (daysUntilDeadline < 0) return 'overdue';
  if (daysUntilDeadline <= 7) return 'urgent';
  if (daysUntilDeadline <= 30) return 'upcoming';
  return 'future';
};

export const addProgram = (newProgram) => {
  const program = {
    id: Date.now().toString(),
    ...newProgram,
    createdAt: new Date().toISOString().split('T')[0],
    status: 'active',
    enrolledStudents: 0,
    totalCourses: newProgram.courseIds.length,
    estimatedHours: newProgram.courseIds.length * 20
  };
  mockPrograms.push(program);
  return true;
};

export const getProgramById = (programId) => {
  return mockPrograms.find(program => program.id === programId);
};

export const updateProgram = (programId, updatedProgram) => {
  const programIndex = mockPrograms.findIndex(p => p.id === programId);
  if (programIndex === -1) return false;
  
  mockPrograms[programIndex] = {
    ...mockPrograms[programIndex],
    ...updatedProgram,
    id: programId
  };
  return true;
};

// Category management functions
export const getCategories = () => {
  return mockCategories.filter(category => category.isActive);
};

export const getAllCategories = () => {
  return mockCategories;
};

export const getCategoryById = (categoryId) => {
  return mockCategories.find(category => category.id === categoryId);
};

export const addCategory = (newCategory) => {
  const category = {
    id: Date.now().toString(),
    createdAt: new Date().toISOString().split('T')[0],
    isActive: true,
    courseCount: 0,
    ...newCategory
  };
  
  mockCategories.push(category);
  return category;
};

export const updateCategory = (categoryId, updatedCategory) => {
  const categoryIndex = mockCategories.findIndex(c => c.id === categoryId);
  if (categoryIndex === -1) return false;
  
  mockCategories[categoryIndex] = {
    ...mockCategories[categoryIndex],
    ...updatedCategory,
    id: categoryId
  };
  
  return true;
};

export const deleteCategory = (categoryId) => {
  const categoryIndex = mockCategories.findIndex(c => c.id === categoryId);
  if (categoryIndex === -1) return false;
  
  mockCategories[categoryIndex].isActive = false;
  return true;
};

// Notification functions
export const getUserNotifications = (userId) => {
  return mockNotifications.filter(notification => notification.userId === userId);
};

export const getUnreadNotifications = (userId) => {
  return mockNotifications.filter(notification => 
    notification.userId === userId && !notification.isRead
  );
};

export const markNotificationAsRead = (notificationId) => {
  const notification = mockNotifications.find(n => n.id === notificationId);
  if (notification) {
    notification.isRead = true;
  }
  return true;
};

export const markAllNotificationsAsRead = (userId) => {
  mockNotifications.forEach(notification => {
    if (notification.userId === userId) {
      notification.isRead = true;
    }
  });
  return true;
};

export const addNotification = (notification) => {
  const newNotification = {
    id: Date.now().toString(),
    createdAt: new Date().toISOString(),
    isRead: false,
    ...notification
  };
  mockNotifications.push(newNotification);
  return newNotification;
};

// Certificate functions
export const getUserCertificates = (userId) => {
  return mockCertificates.filter(cert => cert.userId === userId);
};

export const isProgramCompleted = (userId, programId) => {
  // Replace with actual completion checking logic
  return false;
};

export const getUserCompletedPrograms = (userId) => {
  return mockPrograms.filter(program => isProgramCompleted(userId, program.id));
};

export const generateProgramCertificate = (userId, programId) => {
  // Replace with actual certificate generation logic
  return null;
};

export const checkAndGenerateCertificates = (userId) => {
  // Replace with actual certificate checking logic
  return [];
};

// Nested programs functions
export const getAvailablePrograms = (excludeProgramId = null) => {
  return mockPrograms.filter(program => {
    if (program.id === excludeProgramId) return false;
    if (program.nestedProgramIds && program.nestedProgramIds.length > 0) return false;
    return true;
  });
};

export const getNestedPrograms = (programId) => {
  const program = mockPrograms.find(p => p.id === programId);
  if (!program || !program.nestedProgramIds) return [];
  
  return program.nestedProgramIds.map(nestedId => 
    mockPrograms.find(p => p.id === nestedId)
  ).filter(Boolean);
};

export const hasNestedPrograms = (programId) => {
  const program = mockPrograms.find(p => p.id === programId);
  return program && program.nestedProgramIds && program.nestedProgramIds.length > 0;
};

export const canNestProgram = (parentProgramId, childProgramId) => {
  const parentProgram = mockPrograms.find(p => p.id === parentProgramId);
  const childProgram = mockPrograms.find(p => p.id === childProgramId);
  
  if (!parentProgram || !childProgram) return false;
  if (parentProgramId === childProgramId) return false;
  if (childProgram.nestedProgramIds && childProgram.nestedProgramIds.length > 0) return false;
  if (childProgram.nestedProgramIds && childProgram.nestedProgramIds.includes(parentProgramId)) return false;
  
  return true;
};

export const getTotalProgramCourses = (programId) => {
  const program = mockPrograms.find(p => p.id === programId);
  if (!program) return [];
  
  let allCourses = [];
  
  if (program.courseIds) {
    allCourses = program.courseIds.map(courseId => 
      mockCourses.find(c => c.id === courseId)
    ).filter(Boolean);
  }
  
  if (program.nestedProgramIds) {
    program.nestedProgramIds.forEach(nestedId => {
      const nestedProgram = mockPrograms.find(p => p.id === nestedId);
      if (nestedProgram && nestedProgram.courseIds) {
        const nestedCourses = nestedProgram.courseIds.map(courseId => 
          mockCourses.find(c => c.id === courseId)
        ).filter(Boolean);
        allCourses = [...allCourses, ...nestedCourses];
      }
    });
  }
  
  return allCourses;
};

// Placeholder functions - Replace with your actual implementations
export const getQuizAttempts = () => mockQuizAttempts;
export const getQuizResults = () => mockQuizResults;
export const getStudentClassroomAssignments = () => [];
export const hasUnreadClassroomAssignments = () => false;

// Missing functions needed by components - Add your implementations
export const getInstructorQuizAnalytics = (instructorId) => ({
  totalQuizzes: 0,
  totalAttempts: 0,
  averageScore: 0,
  quizzes: []
});

export const getEnrolledCourses = (userId) => [];

export const getStudentClassrooms = (userId) => [];

export const getUserQuizResults = (userId) => [];

export const getCurrentUser = () => mockUsers[0] || null;

export const setCurrentUser = (user) => {
  // Replace with actual user persistence logic
  return user;
};

export const getClassroomStudents = (classroomId) => [];

export const getClassroomsForTrainer = (trainerId) => [];

export const getClassroomAccessStatus = (classroomId, userId) => ({
  hasAccess: false,
  reason: 'No data available'
});

export const getCourseProgress = (userId, courseId) => ({
  progress: 0,
  completedLessons: 0,
  totalLessons: 0
});

export const getUserClassroomAccess = (userId) => [];

export const getUsersByDepartment = (departmentId) => 
  mockUsers.filter(user => user.departmentId === departmentId);

export const getCourseProgressionStatus = (userId, programId) => ({
  currentCourseIndex: 0,
  canAccessCourse: () => true,
  completedCourses: []
});