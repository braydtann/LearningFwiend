// Mock data for LearningFwiend LMS clone
export const mockUsers = [
  {
    id: '1',
    name: 'John Admin',
    email: 'admin@learningfwiend.com',
    role: 'admin',
    avatar: 'https://images.unsplash.com/photo-1472099645785-5658abf4ff4e?w=100&h=100&fit=crop&crop=face',
    joinDate: '2024-01-15'
  },
  {
    id: '2',
    name: 'Sarah Wilson',
    email: 'sarah.wilson@learningfwiend.com',
    role: 'instructor',
    avatar: 'https://images.unsplash.com/photo-1438761681033-6461ffad8d80?w=100&h=100&fit=crop&crop=face',
    joinDate: '2024-02-10'
  },
  {
    id: '3',
    name: 'Mike Johnson',
    email: 'mike.johnson@learningfwiend.com',
    role: 'learner',
    avatar: 'https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?w=100&h=100&fit=crop&crop=face',
    joinDate: '2024-03-05'
  }
];

export const mockCourses = [
  {
    id: '1',
    title: 'React Development Fundamentals',
    description: 'Learn the basics of React development including components, hooks, and state management.',
    category: 'Web Development',
    instructor: 'Sarah Wilson',
    instructorId: '2',
    duration: '8 weeks',
    thumbnail: 'https://images.unsplash.com/photo-1633356122544-f134324a6cee?w=300&h=200&fit=crop',
    enrolledStudents: 45,
    totalLessons: 25,
    isPublic: true,
    status: 'published',
    createdAt: '2024-01-20',
    modules: [
      {
        id: 'm1',
        title: 'Getting Started with React',
        lessons: [
          { id: 'l1', title: 'Introduction to React', type: 'video', duration: '15 min', videoUrl: 'https://www.youtube.com/embed/Tn6-PIqc4UM' },
          { id: 'l2', title: 'Setting up Development Environment', type: 'video', duration: '12 min', videoUrl: 'https://drive.google.com/file/d/1BxBicpQ09uO5m_Lyp9oWw7vtkMEMFHNB/view' },
          { id: 'l3', title: 'React Component Overview', type: 'presentation', duration: '10 min', presentationUrl: 'https://www.canva.com/design/DAFxKzE1234/view?utm_content=DAFxKzE1234' },
          { id: 'l4', title: 'Your First Component', type: 'text', content: 'In this lesson, we will create our first React component...' }
        ]
      },
      {
        id: 'm2',
        title: 'Components and JSX',
        lessons: [
          { id: 'l4', title: 'Understanding JSX', type: 'video', duration: '18 min', videoUrl: 'https://www.youtube.com/embed/7fPXI_MnBOY' },
          { id: 'l5', title: 'Props and Component Communication', type: 'video', duration: '20 min', videoUrl: 'https://www.youtube.com/embed/PHaECbrKgs0' },
          { id: 'l6', title: 'Component Quiz', type: 'quiz', questions: [
            { id: 'q1', question: 'What does JSX stand for?', options: ['JavaScript XML', 'Java Syntax Extension', 'JavaScript Extension'], correct: 0 }
          ]}
        ]
      }
    ]
  },
  {
    id: '2',
    title: 'Python for Data Science',
    description: 'Comprehensive course covering Python programming for data analysis and machine learning.',
    category: 'Data Science',
    instructor: 'Sarah Wilson',
    instructorId: '2',
    duration: '12 weeks',
    thumbnail: 'https://images.unsplash.com/photo-1526379095098-d400fd0bf935?w=300&h=200&fit=crop',
    enrolledStudents: 32,
    totalLessons: 36,
    isPublic: true,
    status: 'published',
    createdAt: '2024-02-15',
    modules: [
      {
        id: 'm3',
        title: 'Python Basics',
        lessons: [
          { id: 'l7', title: 'Python Introduction', type: 'video', duration: '25 min', videoUrl: 'https://www.youtube.com/embed/_uQrJ0TkZlc' },
          { id: 'l8', title: 'Variables and Data Types', type: 'video', duration: '22 min', videoUrl: 'https://www.youtube.com/embed/OH86oLzVzzw' }
        ]
      }
    ]
  },
  {
    id: '3',
    title: 'Digital Marketing Mastery',
    description: 'Master digital marketing strategies including SEO, social media marketing, and analytics.',
    category: 'Marketing',
    instructor: 'Sarah Wilson',
    instructorId: '2',
    duration: '6 weeks',
    thumbnail: 'https://images.unsplash.com/photo-1460925895917-afdab827c52f?w=300&h=200&fit=crop',
    enrolledStudents: 28,
    totalLessons: 18,
    isPublic: true,
    status: 'published',
    createdAt: '2024-03-01',
    modules: [
      {
        id: 'm4',
        title: 'SEO Fundamentals',
        lessons: [
          { id: 'l9', title: 'Introduction to SEO', type: 'video', duration: '20 min', videoUrl: 'https://www.youtube.com/embed/xsVTqzratPs' }
        ]
      }
    ]
  }
];

export const mockEnrollments = [
  {
    id: '1',
    userId: '3',
    courseId: '1',
    enrolledAt: '2024-03-10',
    progress: 65,
    completedLessons: ['l1', 'l2', 'l3', 'l4'],
    lastAccessed: '2024-03-15'
  },
  {
    id: '2',
    userId: '3',
    courseId: '2',
    enrolledAt: '2024-03-08',
    progress: 25,
    completedLessons: ['l7'],
    lastAccessed: '2024-03-12'
  }
];

export const mockCertificates = [
  {
    id: '1',
    userId: '3',
    courseId: '1',
    courseName: 'React Development Fundamentals',
    issuedAt: '2024-03-15',
    certificateUrl: '/certificates/cert-1.pdf'
  }
];

export const mockAnnouncements = [
  {
    id: '1',
    courseId: '1',
    title: 'New Module Available',
    message: 'The Advanced Hooks module is now available for all enrolled students.',
    createdAt: '2024-03-10',
    author: 'Sarah Wilson'
  },
  {
    id: '2',
    courseId: '2',
    title: 'Assignment Due Date Extended',
    message: 'The Python fundamentals assignment due date has been extended to next Friday.',
    createdAt: '2024-03-08',
    author: 'Sarah Wilson'
  }
];

export const getCurrentUser = () => {
  const stored = localStorage.getItem('currentUser');
  return stored ? JSON.parse(stored) : mockUsers[2]; // Default to learner
};

export const setCurrentUser = (user) => {
  localStorage.setItem('currentUser', JSON.stringify(user));
};

export const getEnrolledCourses = (userId) => {
  const enrollments = mockEnrollments.filter(e => e.userId === userId);
  return enrollments.map(enrollment => {
    const course = mockCourses.find(c => c.id === enrollment.courseId);
    return {
      ...course,
      ...enrollment
    };
  });
};

export const getCourseProgress = (userId, courseId) => {
  const enrollment = mockEnrollments.find(e => e.userId === userId && e.courseId === courseId);
  return enrollment ? enrollment.progress : 0;
};

export const mockPrograms = [
  {
    id: '1',
    name: 'Full Stack Development Certification',
    description: 'Complete full-stack development program covering frontend, backend, and deployment',
    courseIds: ['1', '2'], // React Development, Python for Data Science
    courseOrder: ['1', '2'], // Specific order for courses
    duration: '16 weeks',
    difficulty: 'Intermediate',
    createdBy: '1', // Admin
    createdAt: '2024-01-15',
    status: 'active',
    enrolledStudents: 12,
    totalCourses: 2,
    estimatedHours: 120
  },
  {
    id: '2',
    name: 'Digital Marketing Professional',
    description: 'Comprehensive digital marketing program from basics to advanced strategies',
    courseIds: ['3'], // Digital Marketing Mastery
    courseOrder: ['3'],
    duration: '8 weeks',
    difficulty: 'Beginner',
    createdBy: '1',
    createdAt: '2024-02-01',
    status: 'active',
    enrolledStudents: 8,
    totalCourses: 1,
    estimatedHours: 40
  }
];

export const mockProgramEnrollments = [
  {
    id: '1',
    programId: '1',
    userId: '3',
    enrolledAt: '2024-03-01',
    currentCourseId: '1',
    completedCourses: [],
    overallProgress: 25,
    status: 'active'
  }
];

export const getProgramsForAdmin = () => {
  return mockPrograms;
};

export const getUserPrograms = (userId) => {
  const enrollments = mockProgramEnrollments.filter(e => e.userId === userId);
  return enrollments.map(enrollment => {
    const program = mockPrograms.find(p => p.id === enrollment.programId);
    return {
      ...program,
      ...enrollment
    };
  });
};

export const getProgramCourses = (programId) => {
  const program = mockPrograms.find(p => p.id === programId);
  if (!program) return [];
  
  return program.courseOrder.map(courseId => 
    mockCourses.find(course => course.id === courseId)
  ).filter(Boolean);
};

export const getUserCertificates = (userId) => {
  return mockCertificates.filter(cert => cert.userId === userId);
};

export const mockClassrooms = [
  {
    id: '1',
    name: 'Q1 2024 New Agent Training',
    description: 'Comprehensive training program for new customer service agents',
    trainerId: '2', // Sarah Wilson
    trainerName: 'Sarah Wilson',
    courseIds: ['1', '3'], // React Development and Digital Marketing
    studentIds: ['3'], // Mike Johnson
    startDate: '2024-03-01',
    endDate: '2024-04-30',
    status: 'active',
    createdAt: '2024-02-20',
    metrics: {
      totalStudents: 1,
      completedStudents: 0,
      averageProgress: 45,
      averageTimeToCompletion: null,
      averageTestScore: 85,
      completionRate: 0
    }
  },
  {
    id: '2',
    name: 'Advanced Python Bootcamp',
    description: 'Intensive Python training for data science applications',
    trainerId: '2',
    trainerName: 'Sarah Wilson',
    courseIds: ['2'], // Python for Data Science
    studentIds: ['3'],
    startDate: '2024-02-15',
    endDate: '2024-05-15',
    status: 'active',
    createdAt: '2024-02-01',
    metrics: {
      totalStudents: 1,
      completedStudents: 0,
      averageProgress: 25,
      averageTimeToCompletion: null,
      averageTestScore: 78,
      completionRate: 0
    }
  }
];

export const mockClassroomEnrollments = [
  {
    id: '1',
    classroomId: '1',
    studentId: '3',
    enrolledAt: '2024-03-01',
    progress: 45,
    completedCourses: [],
    testScores: [
      { courseId: '1', score: 85, completedAt: '2024-03-15' }
    ],
    totalTimeSpent: 1200, // minutes
    lastAccessed: '2024-03-20'
  },
  {
    id: '2',
    classroomId: '2',
    studentId: '3',
    enrolledAt: '2024-02-15',
    progress: 25,
    completedCourses: [],
    testScores: [
      { courseId: '2', score: 78, completedAt: '2024-03-01' }
    ],
    totalTimeSpent: 800, // minutes
    lastAccessed: '2024-03-18'
  }
];

export const getClassroomsForTrainer = (trainerId) => {
  return mockClassrooms.filter(classroom => classroom.trainerId === trainerId);
};

export const getClassroomStudents = (classroomId) => {
  const classroom = mockClassrooms.find(c => c.id === classroomId);
  if (!classroom) return [];
  
  return classroom.studentIds.map(studentId => {
    const user = mockUsers.find(u => u.id === studentId);
    const enrollment = mockClassroomEnrollments.find(e => e.classroomId === classroomId && e.studentId === studentId);
    return {
      ...user,
      ...enrollment
    };
  });
};

export const getStudentClassrooms = (studentId) => {
  const enrollments = mockClassroomEnrollments.filter(e => e.studentId === studentId);
  return enrollments.map(enrollment => {
    const classroom = mockClassrooms.find(c => c.id === enrollment.classroomId);
    return {
      ...classroom,
      ...enrollment
    };
  });
};