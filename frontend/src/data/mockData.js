// Mock data for Learning 360 LMS clone
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
    email: 'mike.johnson@learning360.com',
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
    totalLessons: 24,
    isPublic: true,
    status: 'published',
    createdAt: '2024-01-20',
    modules: [
      {
        id: 'm1',
        title: 'Getting Started with React',
        lessons: [
          { id: 'l1', title: 'Introduction to React', type: 'video', duration: '15 min', videoUrl: 'https://www.youtube.com/embed/Tn6-PIqc4UM' },
          { id: 'l2', title: 'Setting up Development Environment', type: 'video', duration: '12 min', videoUrl: 'https://www.youtube.com/embed/x7mH-3Hpb9U' },
          { id: 'l3', title: 'Your First Component', type: 'text', content: 'In this lesson, we will create our first React component...' }
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

export const getUserCertificates = (userId) => {
  return mockCertificates.filter(cert => cert.userId === userId);
};