// Mock data for LearningFwiend LMS clone
export const mockUsers = [
  // Admin Users
  {
    id: '1',
    name: 'John Admin',
    email: 'admin@learningfwiend.com',
    role: 'admin',
    avatar: 'https://images.unsplash.com/photo-1472099645785-5658abf4ff4e?w=100&h=100&fit=crop&crop=face',
    joinDate: '2024-01-15',
    startDate: '2024-01-15',
    departmentId: null, // Admins don't need department
    department: null
  },
  {
    id: '2',
    name: 'Lisa Rodriguez',
    email: 'lisa.rodriguez@learningfwiend.com',
    role: 'admin',
    avatar: 'https://images.unsplash.com/photo-1494790108755-2616b612b739?w=100&h=100&fit=crop&crop=face',
    joinDate: '2024-01-08',
    startDate: '2024-01-08',
    departmentId: null,
    department: null
  },
  
  // Instructor Users
  {
    id: '3',
    name: 'Sarah Wilson',
    email: 'sarah.wilson@learningfwiend.com',
    role: 'instructor',
    avatar: 'https://images.unsplash.com/photo-1438761681033-6461ffad8d80?w=100&h=100&fit=crop&crop=face',
    joinDate: '2024-01-20',
    startDate: '2024-01-20',
    departmentId: '1',
    department: 'Web Development'
  },
  {
    id: '4',
    name: 'Dr. Michael Chen',
    email: 'michael.chen@learningfwiend.com',
    role: 'instructor',
    avatar: 'https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?w=100&h=100&fit=crop&crop=face',
    joinDate: '2024-01-18',
    startDate: '2024-01-18',
    departmentId: '2',
    department: 'Data Science'
  },
  {
    id: '5',
    name: 'Emma Thompson',
    email: 'emma.thompson@learningfwiend.com',
    role: 'instructor',
    avatar: 'https://images.unsplash.com/photo-1544005313-94ddf0286df2?w=100&h=100&fit=crop&crop=face',
    joinDate: '2024-02-01',
    startDate: '2024-02-01',
    departmentId: '3',
    department: 'Digital Marketing'
  },
  {
    id: '6',
    name: 'James Davis',
    email: 'james.davis@learningfwiend.com',
    role: 'instructor',
    avatar: 'https://images.unsplash.com/photo-1500648767791-00dcc994a43e?w=100&h=100&fit=crop&crop=face',
    joinDate: '2024-02-15',
    startDate: '2024-02-15',
    departmentId: '4',
    department: 'Business Management'
  },
  {
    id: '7',
    name: 'Dr. Priya Patel',
    email: 'priya.patel@learningfwiend.com',
    role: 'instructor',
    avatar: 'https://images.unsplash.com/photo-1573496359142-b8d87734a5a2?w=100&h=100&fit=crop&crop=face',
    joinDate: '2024-03-01',
    startDate: '2024-03-01',
    departmentId: '5',
    department: 'Cybersecurity'
  },
  
  // Learner Users
  {
    id: '8',
    name: 'Mike Johnson',
    email: 'mike.johnson@learningfwiend.com',
    role: 'learner',
    avatar: 'https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?w=100&h=100&fit=crop&crop=face',
    joinDate: '2024-01-25',
    startDate: '2024-01-25',
    departmentId: '1',
    department: 'Web Development'
  },
  {
    id: '9',
    name: 'Jennifer Williams',
    email: 'jennifer.williams@learningfwiend.com',
    role: 'learner',
    avatar: 'https://images.unsplash.com/photo-1487412720507-e7ab37603c6f?w=100&h=100&fit=crop&crop=face',
    joinDate: '2024-01-30',
    startDate: '2024-01-30',
    departmentId: '1',
    department: 'Web Development'
  },
  {
    id: '10',
    name: 'David Brown',
    email: 'david.brown@learningfwiend.com',
    role: 'learner',
    avatar: 'https://images.unsplash.com/photo-1463453091185-61582044d556?w=100&h=100&fit=crop&crop=face',
    joinDate: '2024-02-05',
    startDate: '2024-02-05',
    departmentId: '2',
    department: 'Data Science'
  },
  {
    id: '11',
    name: 'Maria Garcia',
    email: 'maria.garcia@learningfwiend.com',
    role: 'learner',
    avatar: 'https://images.unsplash.com/photo-1546967191-fdfb13ed6b1e?w=100&h=100&fit=crop&crop=face',
    joinDate: '2024-02-12',
    startDate: '2024-02-12',
    departmentId: '1',
    department: 'Web Development'
  },
  {
    id: '12',
    name: 'Robert Taylor',
    email: 'robert.taylor@learningfwiend.com',
    role: 'learner',
    avatar: 'https://images.unsplash.com/photo-1492562080023-ab3db95bfbce?w=100&h=100&fit=crop&crop=face',
    joinDate: '2024-02-20',
    startDate: '2024-02-20',
    departmentId: '3',
    department: 'Digital Marketing'
  },
  {
    id: '13',
    name: 'Linda Anderson',
    email: 'linda.anderson@learningfwiend.com',
    role: 'learner',
    avatar: 'https://images.unsplash.com/photo-1580489944761-15a19d654956?w=100&h=100&fit=crop&crop=face',
    joinDate: '2024-02-28',
    startDate: '2024-02-28',
    departmentId: '2',
    department: 'Data Science'
  },
  {
    id: '14',
    name: 'Kevin Lee',
    email: 'kevin.lee@learningfwiend.com',
    role: 'learner',
    avatar: 'https://images.unsplash.com/photo-1519085360753-af0119f7cbe7?w=100&h=100&fit=crop&crop=face',
    joinDate: '2024-03-10',
    startDate: '2024-03-10',
    departmentId: '1',
    department: 'Web Development'
  },
  {
    id: '15',
    name: 'Angela Martinez',
    email: 'angela.martinez@learningfwiend.com',
    role: 'learner',
    avatar: 'https://images.unsplash.com/photo-1513475382585-d06e58bcb0e0?w=100&h=100&fit=crop&crop=face',
    joinDate: '2024-03-15',
    startDate: '2024-03-15',
    departmentId: '3',
    department: 'Digital Marketing'
  },
  {
    id: '16',
    name: 'Thomas Wilson',
    email: 'thomas.wilson@learningfwiend.com',
    role: 'learner',
    avatar: 'https://images.unsplash.com/photo-1472099645785-5658abf4ff4e?w=100&h=100&fit=crop&crop=face',
    joinDate: '2024-03-22',
    startDate: '2024-03-22',
    departmentId: '4',
    department: 'Business Management'
  },
  {
    id: '17',
    name: 'Jessica Clark',
    email: 'jessica.clark@learningfwiend.com',
    role: 'learner',
    avatar: 'https://images.unsplash.com/photo-1534528741775-53994a69daeb?w=100&h=100&fit=crop&crop=face',
    joinDate: '2024-04-01',
    startDate: '2024-04-01',
    departmentId: '1',
    department: 'Web Development'
  },
  {
    id: '18',
    name: 'Christopher Moore',
    email: 'christopher.moore@learningfwiend.com',
    role: 'learner',
    avatar: 'https://images.unsplash.com/photo-1556157382-97eda2d62296?w=100&h=100&fit=crop&crop=face',
    joinDate: '2024-04-08',
    startDate: '2024-04-08',
    departmentId: '2',
    department: 'Data Science'
  },
  {
    id: '19',
    name: 'Amanda White',
    email: 'amanda.white@learningfwiend.com',
    role: 'learner',
    avatar: 'https://images.unsplash.com/photo-1508214751196-bcfd4ca60f91?w=100&h=100&fit=crop&crop=face',
    joinDate: '2024-04-15',
    startDate: '2024-04-15',
    departmentId: '3',
    department: 'Digital Marketing'
  },
  {
    id: '20',
    name: 'Steven Hall',
    email: 'steven.hall@learningfwiend.com',
    role: 'learner',
    avatar: 'https://images.unsplash.com/photo-1507591064344-4c6ce005b128?w=100&h=100&fit=crop&crop=face',
    joinDate: '2024-04-22',
    startDate: '2024-04-22',
    departmentId: '5',
    department: 'Cybersecurity'
  },
  {
    id: '21',
    name: 'Michelle Young',
    email: 'michelle.young@learningfwiend.com',
    role: 'learner',
    avatar: 'https://images.unsplash.com/photo-1485206412256-701ccc5b93ca?w=100&h=100&fit=crop&crop=face',
    joinDate: '2024-05-01',
    startDate: '2024-05-01',
    departmentId: '1',
    department: 'Web Development'
  },
  {
    id: '22',
    name: 'Daniel Harris',
    email: 'daniel.harris@learningfwiend.com',
    role: 'learner',
    avatar: 'https://images.unsplash.com/photo-1560250097-0b93528c311a?w=100&h=100&fit=crop&crop=face',
    joinDate: '2024-05-10',
    startDate: '2024-05-10',
    departmentId: '4',
    department: 'Business Management'
  },
  {
    id: '23',
    name: 'Nicole Lewis',
    email: 'nicole.lewis@learningfwiend.com',
    role: 'learner',
    avatar: 'https://images.unsplash.com/photo-1607746882042-944635dfe10e?w=100&h=100&fit=crop&crop=face',
    joinDate: '2024-05-18',
    startDate: '2024-05-18',
    departmentId: '2',
    department: 'Data Science'
  },
  {
    id: '24',
    name: 'Ryan King',
    email: 'ryan.king@learningfwiend.com',
    role: 'learner',
    avatar: 'https://images.unsplash.com/photo-1599566150163-29194dcaad36?w=100&h=100&fit=crop&crop=face',
    joinDate: '2024-05-25',
    startDate: '2024-05-25',
    departmentId: '3',
    department: 'Digital Marketing'
  },
  {
    id: '25',
    name: 'Stephanie Scott',
    email: 'stephanie.scott@learningfwiend.com',
    role: 'learner',
    avatar: 'https://images.unsplash.com/photo-1502823403499-6ccfcf4fb453?w=100&h=100&fit=crop&crop=face',
    joinDate: '2024-06-01',
    startDate: '2024-06-01',
    departmentId: '5',
    department: 'Cybersecurity'
  }
];

// Course categories data
export const mockCategories = [
  {
    id: '1',
    name: 'Web Development',
    description: 'Modern web development technologies and frameworks',
    createdAt: '2024-01-01',
    createdBy: '1', // John Admin
    isActive: true,
    courseCount: 2
  },
  {
    id: '2',
    name: 'Data Science',
    description: 'Data analysis, machine learning, and statistics',
    createdAt: '2024-01-01',
    createdBy: '1',
    isActive: true,
    courseCount: 2
  },
  {
    id: '3',
    name: 'Digital Marketing',
    description: 'SEO, social media marketing, and digital advertising',
    createdAt: '2024-01-01',
    createdBy: '1',
    isActive: true,
    courseCount: 2
  },
  {
    id: '4',
    name: 'Business Management',
    description: 'Project management, leadership, and business strategy',
    createdAt: '2024-01-01',
    createdBy: '1',
    isActive: true,
    courseCount: 2
  },
  {
    id: '5',
    name: 'Cybersecurity',
    description: 'Information security and threat management',
    createdAt: '2024-01-01',
    createdBy: '1',
    isActive: true,
    courseCount: 2
  }
];

// Mock departments data
export const mockDepartments = [
  {
    id: '1',
    name: 'Web Development',
    description: 'Modern web development technologies including React, JavaScript, HTML, CSS, and full-stack development.',
    createdAt: '2024-01-01',
    createdBy: '1', // John Admin
    isActive: true,
    userCount: 8 // Users with this department
  },
  {
    id: '2',
    name: 'Data Science',
    description: 'Data analysis, machine learning, statistics, and data visualization using Python and related tools.',
    createdAt: '2024-01-01',
    createdBy: '1',
    isActive: true,
    userCount: 4
  },
  {
    id: '3',
    name: 'Digital Marketing',
    description: 'SEO, social media marketing, content strategy, and digital advertising campaigns.',
    createdAt: '2024-01-01',
    createdBy: '1',
    isActive: true,
    userCount: 5
  },
  {
    id: '4',
    name: 'Business Management',
    description: 'Project management, leadership, team management, and business strategy.',
    createdAt: '2024-01-01',
    createdBy: '1',
    isActive: true,
    userCount: 3
  },
  {
    id: '5',
    name: 'Cybersecurity',
    description: 'Information security, network security, threat assessment, and risk management.',
    createdAt: '2024-01-01',
    createdBy: '1',
    isActive: true,
    userCount: 2
  }
];

export const mockCourses = [
  // Web Development Courses
  {
    id: '1',
    title: 'React Development Fundamentals',
    description: 'Learn the basics of React development including components, hooks, and state management.',
    category: 'Web Development',
    instructor: 'Sarah Wilson',
    instructorId: '3',
    duration: '8 weeks',
    thumbnail: 'https://images.unsplash.com/photo-1633356122544-f134324a6cee?w=300&h=200&fit=crop',
    enrolledStudents: 45,
    totalLessons: 25,
    isPublic: true,
    enrollmentType: 'open', // Anyone can enroll
    status: 'published',
    createdAt: '2024-01-20',
    modules: [
      {
        id: 'm1',
        title: 'Getting Started with React',
        lessons: [
          { id: 'l1', title: 'Introduction to React', type: 'video', duration: '15 min', videoUrl: 'https://www.youtube.com/embed/Tn6-PIqc4UM' },
          { id: 'l2', title: 'Setting up Development Environment', type: 'video', duration: '12 min', videoUrl: 'https://drive.google.com/file/d/1BxBicpQ09uO5m_Lyp9oWw7vtkMEMFHNB/view' },
          { id: 'l3', title: 'Your First React App', type: 'text', duration: '10 min', content: 'Learn to create your first React application...' },
          { id: 'l4', title: 'Understanding JSX', type: 'video', duration: '18 min', videoUrl: 'https://www.youtube.com/embed/7fPXI_MnBOY' },
          { id: 'l5', title: 'Components Basics', type: 'text', duration: '20 min', content: 'Understanding React components...' },
          { id: 'l6', title: 'React Quiz 1', type: 'quiz', duration: '15 min', quizId: 'quiz1' }
        ]
      }
    ]
  },
  {
    id: '2',
    title: 'Advanced JavaScript ES6+',
    description: 'Master modern JavaScript features including async/await, destructuring, and modules.',
    category: 'Web Development',
    instructor: 'Sarah Wilson',
    instructorId: '3',
    duration: '6 weeks',
    thumbnail: 'https://images.unsplash.com/photo-1627398242454-45a1465c2479?w=300&h=200&fit=crop',
    enrolledStudents: 38,
    totalLessons: 18,
    isPublic: true,
    enrollmentType: 'assignment', // Assignment only
    status: 'published',
    createdAt: '2024-01-25',
    modules: [
      {
        id: 'm1',
        title: 'Modern JavaScript Features',
        lessons: [
          { id: 'l1', title: 'Arrow Functions and Template Literals', type: 'video', duration: '20 min', videoUrl: 'https://www.youtube.com/embed/h33Srr5J9nY' },
          { id: 'l2', title: 'Destructuring and Spread Operator', type: 'quiz', duration: '15 min', quizId: 'quiz2' }
        ]
      }
    ]
  },
  
  // Data Science Courses
  {
    id: '3',
    title: 'Python for Data Science',
    description: 'Complete introduction to Python programming for data analysis and machine learning.',
    category: 'Data Science',
    instructor: 'Dr. Michael Chen',
    instructorId: '4',
    duration: '10 weeks',
    thumbnail: 'https://images.unsplash.com/photo-1526379879527-8559ecfcaec0?w=300&h=200&fit=crop',
    enrolledStudents: 52,
    totalLessons: 30,
    isPublic: true,
    enrollmentType: 'open', // Anyone can enroll
    status: 'published',
    createdAt: '2024-02-01',
    modules: [
      {
        id: 'm1',
        title: 'Python Fundamentals',
        lessons: [
          { id: 'l1', title: 'Introduction to Python', type: 'video', duration: '25 min', videoUrl: 'https://www.youtube.com/embed/_uQrJ0TkZlc' },
          { id: 'l2', title: 'Python Basics Quiz', type: 'quiz', duration: '20 min', quizId: 'quiz3' }
        ]
      }
    ]
  },
  {
    id: '4',
    title: 'Machine Learning Fundamentals',
    description: 'Learn the core concepts of machine learning with hands-on Python implementations.',
    category: 'Data Science',
    instructor: 'Dr. Michael Chen',
    instructorId: '4',
    duration: '12 weeks',
    thumbnail: 'https://images.unsplash.com/photo-1555949963-aa79dcee981c?w=300&h=200&fit=crop',
    enrolledStudents: 29,
    totalLessons: 35,
    isPublic: true,
    enrollmentType: 'assignment', // Assignment only
    status: 'published',
    createdAt: '2024-02-15',
    modules: [
      {
        id: 'm1',
        title: 'Introduction to ML',
        lessons: [
          { id: 'l1', title: 'What is Machine Learning?', type: 'video', duration: '30 min', videoUrl: 'https://www.youtube.com/embed/ukzFI9rgwfU' }
        ]
      }
    ]
  },
  
  // Digital Marketing Courses
  {
    id: '5',
    title: 'Digital Marketing Mastery',
    description: 'Comprehensive course covering SEO, social media marketing, and content strategy.',
    category: 'Digital Marketing',
    instructor: 'Emma Thompson',
    instructorId: '5',
    duration: '8 weeks',
    thumbnail: 'https://images.unsplash.com/photo-1460925895917-afdab827c52f?w=300&h=200&fit=crop',
    enrolledStudents: 67,
    totalLessons: 22,
    isPublic: true,
    status: 'published',
    createdAt: '2024-02-20',
    modules: [
      {
        id: 'm1',
        title: 'SEO Fundamentals',
        lessons: [
          { id: 'l1', title: 'Introduction to SEO', type: 'video', duration: '20 min', videoUrl: 'https://www.youtube.com/embed/xsVTqzratPs' },
          { id: 'l2', title: 'SEO Quiz', type: 'quiz', duration: '15 min', quizId: 'quiz4' }
        ]
      }
    ]
  },
  {
    id: '6',
    title: 'Social Media Strategy',
    description: 'Learn to create effective social media campaigns across all major platforms.',
    category: 'Digital Marketing',
    instructor: 'Emma Thompson',
    instructorId: '5',
    duration: '6 weeks',
    thumbnail: 'https://images.unsplash.com/photo-1611926653458-09294b3142bf?w=300&h=200&fit=crop',
    enrolledStudents: 43,
    totalLessons: 18,
    isPublic: true,
    status: 'published',
    createdAt: '2024-03-01',
    modules: [
      {
        id: 'm1',
        title: 'Platform Strategies',
        lessons: [
          { id: 'l1', title: 'Facebook Marketing', type: 'video', duration: '25 min', videoUrl: 'https://www.youtube.com/embed/8oe3aEl52V4' }
        ]
      }
    ]
  },
  
  // Business Management Courses
  {
    id: '7',
    title: 'Project Management Essentials',
    description: 'Master the fundamentals of project management using Agile and traditional methodologies.',
    category: 'Business Management',
    instructor: 'James Davis',
    instructorId: '6',
    duration: '10 weeks',
    thumbnail: 'https://images.unsplash.com/photo-1552664730-d307ca884978?w=300&h=200&fit=crop',
    enrolledStudents: 56,
    totalLessons: 28,
    isPublic: true,
    status: 'published',
    createdAt: '2024-02-28',
    modules: [
      {
        id: 'm1',
        title: 'Project Management Fundamentals',
        lessons: [
          { id: 'l1', title: 'Introduction to PM', type: 'video', duration: '22 min', videoUrl: 'https://www.youtube.com/embed/2Ox8bnRc5z0' }
        ]
      }
    ]
  },
  {
    id: '8',
    title: 'Leadership and Team Management',
    description: 'Develop essential leadership skills for managing high-performing teams.',
    category: 'Business Management',
    instructor: 'James Davis',
    instructorId: '6',
    duration: '8 weeks',
    thumbnail: 'https://images.unsplash.com/photo-1522071820081-009f0129c71c?w=300&h=200&fit=crop',
    enrolledStudents: 41,
    totalLessons: 20,
    isPublic: true,
    status: 'published',
    createdAt: '2024-03-15',
    modules: [
      {
        id: 'm1',
        title: 'Leadership Principles',
        lessons: [
          { id: 'l1', title: 'What Makes a Great Leader?', type: 'video', duration: '28 min', videoUrl: 'https://www.youtube.com/embed/llKvV8_T95M' }
        ]
      }
    ]
  },
  
  // Cybersecurity Courses
  {
    id: '9',
    title: 'Cybersecurity Fundamentals',
    description: 'Essential cybersecurity concepts including threat assessment and risk management.',
    category: 'Cybersecurity',
    instructor: 'Dr. Priya Patel',
    instructorId: '7',
    duration: '12 weeks',
    thumbnail: 'https://images.unsplash.com/photo-1563013544-824ae1b704d3?w=300&h=200&fit=crop',
    enrolledStudents: 39,
    totalLessons: 32,
    isPublic: true,
    status: 'published',
    createdAt: '2024-03-10',
    modules: [
      {
        id: 'm1',
        title: 'Introduction to Cybersecurity',
        lessons: [
          { id: 'l1', title: 'Cyber Threats Overview', type: 'video', duration: '25 min', videoUrl: 'https://www.youtube.com/embed/bPVaOlJ6ln0' }
        ]
      }
    ]
  },
  {
    id: '10',
    title: 'Network Security Protocols',
    description: 'Deep dive into network security, firewalls, and intrusion detection systems.',
    category: 'Cybersecurity',
    instructor: 'Dr. Priya Patel',
    instructorId: '7',
    duration: '10 weeks',
    thumbnail: 'https://images.unsplash.com/photo-1558494949-ef010cbdcc31?w=300&h=200&fit=crop',
    enrolledStudents: 28,
    totalLessons: 26,
    isPublic: true,
    status: 'published',
    createdAt: '2024-04-01',
    modules: [
      {
        id: 'm1',
        title: 'Network Fundamentals',
        lessons: [
          { id: 'l1', title: 'OSI Model and Security', type: 'video', duration: '30 min', videoUrl: 'https://www.youtube.com/embed/vv4y_uOneC0' }
        ]
      }
    ]
  }
];

export const mockEnrollments = [
  // January 2024 Enrollments
  { id: '1', userId: '8', courseId: '1', enrolledAt: '2024-01-25', progress: 100, completedLessons: ['l1', 'l2', 'l3', 'l4', 'l5', 'l6'], lastAccessed: '2024-02-15', timeSpent: 32.5 },
  { id: '2', userId: '9', courseId: '1', enrolledAt: '2024-01-28', progress: 85, completedLessons: ['l1', 'l2', 'l3', 'l4'], lastAccessed: '2024-03-10', timeSpent: 28.3 },
  { id: '3', userId: '10', courseId: '3', enrolledAt: '2024-01-30', progress: 92, completedLessons: ['l1', 'l2'], lastAccessed: '2024-03-05', timeSpent: 41.2 },
  
  // February 2024 Enrollments
  { id: '4', userId: '11', courseId: '1', enrolledAt: '2024-02-05', progress: 78, completedLessons: ['l1', 'l2', 'l3'], lastAccessed: '2024-03-12', timeSpent: 25.8 },
  { id: '5', userId: '12', courseId: '2', enrolledAt: '2024-02-08', progress: 100, completedLessons: ['l1', 'l2'], lastAccessed: '2024-02-20', timeSpent: 22.4 },
  { id: '6', userId: '13', courseId: '3', enrolledAt: '2024-02-10', progress: 65, completedLessons: ['l1'], lastAccessed: '2024-03-15', timeSpent: 35.7 },
  { id: '7', userId: '14', courseId: '4', enrolledAt: '2024-02-15', progress: 45, completedLessons: ['l1'], lastAccessed: '2024-03-08', timeSpent: 18.9 },
  { id: '8', userId: '15', courseId: '5', enrolledAt: '2024-02-18', progress: 100, completedLessons: ['l1', 'l2'], lastAccessed: '2024-03-01', timeSpent: 19.6 },
  { id: '9', userId: '16', courseId: '5', enrolledAt: '2024-02-20', progress: 88, completedLessons: ['l1', 'l2'], lastAccessed: '2024-03-05', timeSpent: 16.8 },
  { id: '10', userId: '17', courseId: '6', enrolledAt: '2024-02-25', progress: 72, completedLessons: ['l1'], lastAccessed: '2024-03-18', timeSpent: 14.3 },
  
  // March 2024 Enrollments
  { id: '11', userId: '18', courseId: '7', enrolledAt: '2024-03-01', progress: 90, completedLessons: ['l1'], lastAccessed: '2024-03-20', timeSpent: 38.5 },
  { id: '12', userId: '19', courseId: '8', enrolledAt: '2024-03-05', progress: 83, completedLessons: ['l1'], lastAccessed: '2024-03-22', timeSpent: 31.2 },
  { id: '13', userId: '20', courseId: '9', enrolledAt: '2024-03-08', progress: 67, completedLessons: ['l1'], lastAccessed: '2024-03-25', timeSpent: 42.1 },
  { id: '14', userId: '21', courseId: '1', enrolledAt: '2024-03-10', progress: 94, completedLessons: ['l1', 'l2', 'l3', 'l4', 'l5'], lastAccessed: '2024-03-28', timeSpent: 29.7 },
  { id: '15', userId: '22', courseId: '2', enrolledAt: '2024-03-12', progress: 56, completedLessons: ['l1'], lastAccessed: '2024-03-30', timeSpent: 15.4 },
  { id: '16', userId: '23', courseId: '3', enrolledAt: '2024-03-15', progress: 100, completedLessons: ['l1', 'l2'], lastAccessed: '2024-04-01', timeSpent: 44.8 },
  { id: '17', userId: '24', courseId: '4', enrolledAt: '2024-03-18', progress: 71, completedLessons: ['l1'], lastAccessed: '2024-04-05', timeSpent: 26.3 },
  { id: '18', userId: '25', courseId: '5', enrolledAt: '2024-03-20', progress: 89, completedLessons: ['l1', 'l2'], lastAccessed: '2024-04-08', timeSpent: 18.9 },
  
  // April 2024 Enrollments
  { id: '19', userId: '8', courseId: '2', enrolledAt: '2024-04-01', progress: 75, completedLessons: ['l1'], lastAccessed: '2024-04-25', timeSpent: 20.1 },
  { id: '20', userId: '9', courseId: '6', enrolledAt: '2024-04-03', progress: 82, completedLessons: ['l1'], lastAccessed: '2024-04-28', timeSpent: 15.7 },
  { id: '21', userId: '10', courseId: '7', enrolledAt: '2024-04-05', progress: 68, completedLessons: ['l1'], lastAccessed: '2024-04-30', timeSpent: 35.2 },
  { id: '22', userId: '11', courseId: '8', enrolledAt: '2024-04-08', progress: 100, completedLessons: ['l1'], lastAccessed: '2024-04-20', timeSpent: 28.6 },
  { id: '23', userId: '12', courseId: '9', enrolledAt: '2024-04-10', progress: 54, completedLessons: ['l1'], lastAccessed: '2024-05-02', timeSpent: 38.4 },
  { id: '24', userId: '13', courseId: '10', enrolledAt: '2024-04-12', progress: 77, completedLessons: ['l1'], lastAccessed: '2024-05-05', timeSpent: 31.8 },
  { id: '25', userId: '14', courseId: '1', enrolledAt: '2024-04-15', progress: 91, completedLessons: ['l1', 'l2', 'l3', 'l4', 'l5'], lastAccessed: '2024-05-08', timeSpent: 33.4 },
  { id: '26', userId: '15', courseId: '2', enrolledAt: '2024-04-18', progress: 63, completedLessons: ['l1'], lastAccessed: '2024-05-10', timeSpent: 17.2 },
  { id: '27', userId: '16', courseId: '3', enrolledAt: '2024-04-20', progress: 86, completedLessons: ['l1', 'l2'], lastAccessed: '2024-05-12', timeSpent: 39.6 },
  { id: '28', userId: '17', courseId: '4', enrolledAt: '2024-04-22', progress: 49, completedLessons: ['l1'], lastAccessed: '2024-05-15', timeSpent: 21.7 },
  
  // May 2024 Enrollments
  { id: '29', userId: '18', courseId: '1', enrolledAt: '2024-05-01', progress: 87, completedLessons: ['l1', 'l2', 'l3', 'l4'], lastAccessed: '2024-05-30', timeSpent: 27.9 },
  { id: '30', userId: '19', courseId: '2', enrolledAt: '2024-05-03', progress: 95, completedLessons: ['l1', 'l2'], lastAccessed: '2024-06-01', timeSpent: 23.8 },
  { id: '31', userId: '20', courseId: '5', enrolledAt: '2024-05-05', progress: 72, completedLessons: ['l1', 'l2'], lastAccessed: '2024-06-03', timeSpent: 17.4 },
  { id: '32', userId: '21', courseId: '6', enrolledAt: '2024-05-08', progress: 100, completedLessons: ['l1'], lastAccessed: '2024-05-25', timeSpent: 16.3 },
  { id: '33', userId: '22', courseId: '7', enrolledAt: '2024-05-10', progress: 65, completedLessons: ['l1'], lastAccessed: '2024-06-05', timeSpent: 34.1 },
  { id: '34', userId: '23', courseId: '8', enrolledAt: '2024-05-12', progress: 93, completedLessons: ['l1'], lastAccessed: '2024-06-08', timeSpent: 29.5 },
  { id: '35', userId: '24', courseId: '9', enrolledAt: '2024-05-15', progress: 58, completedLessons: ['l1'], lastAccessed: '2024-06-10', timeSpent: 40.7 },
  { id: '36', userId: '25', courseId: '10', enrolledAt: '2024-05-18', progress: 84, completedLessons: ['l1'], lastAccessed: '2024-06-12', timeSpent: 33.2 },
  { id: '37', userId: '8', courseId: '3', enrolledAt: '2024-05-20', progress: 76, completedLessons: ['l1', 'l2'], lastAccessed: '2024-06-15', timeSpent: 36.8 },
  { id: '38', userId: '9', courseId: '4', enrolledAt: '2024-05-22', progress: 100, completedLessons: ['l1'], lastAccessed: '2024-06-02', timeSpent: 24.6 },
  
  // June 2024 Enrollments (Recent)
  { id: '39', userId: '10', courseId: '8', enrolledAt: '2024-06-01', progress: 45, completedLessons: ['l1'], lastAccessed: '2024-06-18', timeSpent: 19.3 },
  { id: '40', userId: '11', courseId: '9', enrolledAt: '2024-06-03', progress: 62, completedLessons: ['l1'], lastAccessed: '2024-06-20', timeSpent: 35.7 },
  { id: '41', userId: '12', courseId: '10', enrolledAt: '2024-06-05', progress: 38, completedLessons: ['l1'], lastAccessed: '2024-06-22', timeSpent: 22.4 },
  { id: '42', userId: '13', courseId: '1', enrolledAt: '2024-06-08', progress: 73, completedLessons: ['l1', 'l2', 'l3'], lastAccessed: '2024-06-25', timeSpent: 24.1 },
  { id: '43', userId: '14', courseId: '5', enrolledAt: '2024-06-10', progress: 89, completedLessons: ['l1', 'l2'], lastAccessed: '2024-06-27', timeSpent: 18.6 },
  { id: '44', userId: '15', courseId: '6', enrolledAt: '2024-06-12', progress: 54, completedLessons: ['l1'], lastAccessed: '2024-06-28', timeSpent: 13.8 },
  { id: '45', userId: '16', courseId: '7', enrolledAt: '2024-06-15', progress: 71, completedLessons: ['l1'], lastAccessed: '2024-06-30', timeSpent: 32.9 },
  { id: '46', userId: '17', courseId: '2', enrolledAt: '2024-06-18', progress: 26, completedLessons: [], lastAccessed: '2024-06-30', timeSpent: 8.4 },
  { id: '47', userId: '18', courseId: '3', enrolledAt: '2024-06-20', progress: 34, completedLessons: ['l1'], lastAccessed: '2024-07-01', timeSpent: 15.2 },
  { id: '48', userId: '19', courseId: '4', enrolledAt: '2024-06-22', progress: 41, completedLessons: ['l1'], lastAccessed: '2024-07-02', timeSpent: 18.7 },
  
  // Admin and Instructor Enrollments for Learning
  { id: '49', userId: '1', courseId: '5', enrolledAt: '2024-03-01', progress: 100, completedLessons: ['l1', 'l2'], lastAccessed: '2024-03-15', timeSpent: 20.5 },
  { id: '50', userId: '2', courseId: '7', enrolledAt: '2024-03-05', progress: 88, completedLessons: ['l1'], lastAccessed: '2024-03-20', timeSpent: 35.4 },
  { id: '51', userId: '3', courseId: '9', enrolledAt: '2024-04-01', progress: 92, completedLessons: ['l1'], lastAccessed: '2024-04-15', timeSpent: 38.9 },
  { id: '52', userId: '4', courseId: '1', enrolledAt: '2024-02-20', progress: 100, completedLessons: ['l1', 'l2', 'l3', 'l4', 'l5', 'l6'], lastAccessed: '2024-03-10', timeSpent: 31.7 },
  { id: '53', userId: '5', courseId: '3', enrolledAt: '2024-03-10', progress: 85, completedLessons: ['l1', 'l2'], lastAccessed: '2024-04-01', timeSpent: 42.3 },
  { id: '54', userId: '6', courseId: '8', enrolledAt: '2024-04-05', progress: 94, completedLessons: ['l1'], lastAccessed: '2024-04-25', timeSpent: 28.1 },
  { id: '55', userId: '7', courseId: '10', enrolledAt: '2024-05-01', progress: 76, completedLessons: ['l1'], lastAccessed: '2024-05-30', timeSpent: 34.6 }
];

export const mockCertificates = [
  {
    id: '1',
    userId: '8', // Mike Johnson
    programId: '1',
    programName: 'Full Stack Development Certification',
    issuedAt: '2024-04-15',
    certificateUrl: '/certificates/cert-prog-1.pdf'
  },
  {
    id: '2',
    userId: '9', // Jennifer Williams
    programId: '2',
    programName: 'Digital Marketing Professional',
    issuedAt: '2024-05-20',
    certificateUrl: '/certificates/cert-prog-2.pdf'
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
    nestedProgramIds: [], // For 1-level program nesting
    duration: '16 weeks',
    difficulty: 'Intermediate',
    createdBy: '1', // Admin
    createdAt: '2024-01-15',
    deadline: '2024-12-31', // Program completion deadline
    status: 'active',
    enrolledStudents: 12,
    totalCourses: 2,
    estimatedHours: 120,
    finalTest: {
      id: 'ft-prog-1',
      title: 'Full Stack Development Certification Final Assessment',
      description: 'Comprehensive assessment covering all aspects of the Full Stack Development program',
      timeLimit: 90,
      passingScore: 75,
      maxAttempts: 2,
      questions: [
        {
          id: 'q1',
          type: 'multiple-choice',
          question: 'What are the key components of a full-stack web application?',
          options: ['Frontend, Backend, Database', 'HTML, CSS, JavaScript', 'Client, Server, Network', 'UI, API, Storage'],
          correctAnswer: 0,
          points: 10
        },
        {
          id: 'q2',
          type: 'long-form-answer',
          question: 'Explain the MVC (Model-View-Controller) architecture pattern and how it applies to modern web development. Include examples of how React and Python frameworks implement this pattern.',
          points: 20
        },
        {
          id: 'q3',
          type: 'multiple-choice',
          question: 'Which of the following best describes RESTful API design principles?',
          options: [
            'Stateful, session-based communication',
            'Stateless, uniform interface, resource-based URLs',
            'RPC-style method calls',
            'GraphQL query language'
          ],
          correctAnswer: 1,
          points: 10
        }
      ]
    }
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
    deadline: '2024-10-15', // Program completion deadline
    status: 'active',
    enrolledStudents: 8,
    totalCourses: 1,
    estimatedHours: 40,
    finalTest: {
      id: 'ft-prog-2',
      title: 'Digital Marketing Professional Certification Final Assessment',
      description: 'Comprehensive assessment covering digital marketing strategies and implementation',
      timeLimit: 60,
      passingScore: 70,
      maxAttempts: 3,
      questions: [
        {
          id: 'q1',
          type: 'multiple-choice',
          question: 'What is the primary goal of SEO in digital marketing?',
          options: [
            'Increase social media followers',
            'Improve organic search rankings and visibility',
            'Reduce advertising costs',
            'Create viral content'
          ],
          correctAnswer: 1,
          points: 10
        },
        {
          id: 'q2',
          type: 'long-form-answer',
          question: 'Describe a comprehensive digital marketing strategy for a new e-commerce business. Include at least 4 different marketing channels and explain how they work together.',
          points: 25
        }
      ]
    }
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

// Check if user has completed all courses in a program
export const isProgramCompleted = (userId, programId) => {
  const program = mockPrograms.find(p => p.id === programId);
  if (!program) return false;
  
  // Check if all courses in the program are completed (100% progress)
  const allCoursesCompleted = program.courseOrder.every(courseId => {
    const enrollment = mockEnrollments.find(e => 
      e.userId === userId && e.courseId === courseId
    );
    return enrollment && enrollment.progress === 100;
  });
  
  return allCoursesCompleted;
};

// Get completed programs for a user
export const getUserCompletedPrograms = (userId) => {
  return mockPrograms.filter(program => isProgramCompleted(userId, program.id));
};

// Generate certificate for program completion
export const generateProgramCertificate = (userId, programId) => {
  const program = mockPrograms.find(p => p.id === programId);
  const user = mockUsers.find(u => u.id === userId);
  
  if (!program || !user || !isProgramCompleted(userId, programId)) {
    return null;
  }
  
  // Check if certificate already exists
  const existingCert = mockCertificates.find(cert => 
    cert.userId === userId && cert.programId === programId
  );
  
  if (existingCert) {
    return existingCert;
  }
  
  // Create new certificate
  const newCertificate = {
    id: Date.now().toString(),
    userId: userId,
    programId: programId,
    programName: program.name,
    issuedAt: new Date().toISOString().split('T')[0],
    certificateUrl: `/certificates/cert-prog-${programId}-${userId}.pdf`
  };
  
  // Add to mock certificates
  mockCertificates.push(newCertificate);
  
  return newCertificate;
};

// Auto-generate certificates for all completed programs
export const checkAndGenerateCertificates = (userId) => {
  const completedPrograms = getUserCompletedPrograms(userId);
  const newCertificates = [];
  
  completedPrograms.forEach(program => {
    const certificate = generateProgramCertificate(userId, program.id);
    if (certificate) {
      newCertificates.push(certificate);
    }
  });
  
  return newCertificates;
};

// Category management helper functions
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
    id: categoryId // Ensure ID doesn't change
  };
  
  return true;
};

export const deleteCategory = (categoryId) => {
  const categoryIndex = mockCategories.findIndex(c => c.id === categoryId);
  if (categoryIndex === -1) return false;
  
  // Soft delete - mark as inactive
  mockCategories[categoryIndex].isActive = false;
  return true;
};

export const mockClassrooms = [
  {
    id: '1',
    name: 'Q1 2024 New Agent Training',
    batchId: 'BATCH-2024-Q1-001',
    description: 'Comprehensive training program for new customer service agents',
    trainerId: '2', // Sarah Wilson
    trainerName: 'Sarah Wilson',
    courseIds: ['1', '3'], // React Development and Digital Marketing
    studentIds: ['8', '9', '11'], // Mike Johnson, Jennifer Williams, Maria Garcia
    startDate: '2024-03-01',
    endDate: '2024-04-30',
    status: 'active',
    createdAt: '2024-02-20',
    metrics: {
      totalStudents: 3,
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
    batchId: 'BATCH-2024-PY-002',
    description: 'Intensive Python training for data science applications',
    trainerId: '2',
    trainerName: 'Sarah Wilson',
    courseIds: ['2'], // Python for Data Science
    studentIds: ['8', '10', '13'], // Mike Johnson, David Brown, Linda Anderson
    startDate: '2024-02-15',
    endDate: '2024-05-15',
    status: 'active',
    createdAt: '2024-02-01',
    metrics: {
      totalStudents: 3,
      completedStudents: 0,
      averageProgress: 25,
      averageTimeToCompletion: null,
      averageTestScore: 78,
      completionRate: 0
    }
  },
  {
    id: '3',
    name: 'Web Development Intensive',
    batchId: 'BATCH-2024-WD-003',
    description: 'Comprehensive web development training covering modern frameworks',
    trainerId: '3', // Sarah Wilson
    trainerName: 'Sarah Wilson',
    courseIds: ['1', '2'], // React Development, Advanced JavaScript
    studentIds: ['9', '14', '17'], // Jennifer Williams, Kevin Lee, Jessica Clark
    startDate: '2024-03-15',
    endDate: '2024-06-15',
    status: 'active',
    createdAt: '2024-03-01',
    metrics: {
      totalStudents: 3,
      completedStudents: 0,
      averageProgress: 35,
      averageTimeToCompletion: null,
      averageTestScore: 82,
      completionRate: 0
    }
  },
  {
    id: '4',
    name: 'Data Science Fundamentals',
    batchId: 'BATCH-2024-DS-004',
    description: 'Introduction to data science concepts and Python programming',
    trainerId: '4', // Dr. Michael Chen
    trainerName: 'Dr. Michael Chen',
    courseIds: ['3', '4'], // Python for Data Science, Machine Learning
    studentIds: ['10', '13', '18'], // David Brown, Linda Anderson, Christopher Moore
    startDate: '2024-04-01',
    endDate: '2024-07-01',
    status: 'active',
    createdAt: '2024-03-15',
    metrics: {
      totalStudents: 3,
      completedStudents: 0,
      averageProgress: 20,
      averageTimeToCompletion: null,
      averageTestScore: 75,
      completionRate: 0
    }
  }
];

export const mockClassroomEnrollments = [
  // Q1 2024 New Agent Training enrollments
  {
    id: '1',
    classroomId: '1',
    studentId: '8', // Mike Johnson
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
    classroomId: '1',
    studentId: '9', // Jennifer Williams
    enrolledAt: '2024-03-01',
    progress: 38,
    completedCourses: [],
    testScores: [
      { courseId: '1', score: 78, completedAt: '2024-03-12' }
    ],
    totalTimeSpent: 950, // minutes
    lastAccessed: '2024-03-18'
  },
  {
    id: '3',
    classroomId: '1',
    studentId: '11', // Maria Garcia
    enrolledAt: '2024-03-01',
    progress: 52,
    completedCourses: [],
    testScores: [
      { courseId: '1', score: 92, completedAt: '2024-03-20' }
    ],
    totalTimeSpent: 1350, // minutes
    lastAccessed: '2024-03-22'
  },
  
  // Advanced Python Bootcamp enrollments
  {
    id: '4',
    classroomId: '2',
    studentId: '8', // Mike Johnson
    enrolledAt: '2024-02-15',
    progress: 25,
    completedCourses: [],
    testScores: [
      { courseId: '2', score: 78, completedAt: '2024-03-01' }
    ],
    totalTimeSpent: 800, // minutes
    lastAccessed: '2024-03-18'
  },
  {
    id: '5',
    classroomId: '2',
    studentId: '10', // David Brown
    enrolledAt: '2024-02-15',
    progress: 32,
    completedCourses: [],
    testScores: [
      { courseId: '2', score: 84, completedAt: '2024-02-28' }
    ],
    totalTimeSpent: 920, // minutes
    lastAccessed: '2024-03-15'
  },
  {
    id: '6',
    classroomId: '2',
    studentId: '13', // Linda Anderson
    enrolledAt: '2024-02-15',
    progress: 18,
    completedCourses: [],
    testScores: [
      { courseId: '2', score: 72, completedAt: '2024-02-25' }
    ],
    totalTimeSpent: 650, // minutes
    lastAccessed: '2024-03-10'
  },

  // Web Development Intensive enrollments
  {
    id: '7',
    classroomId: '3',
    studentId: '9', // Jennifer Williams
    enrolledAt: '2024-03-15',
    progress: 35,
    completedCourses: [],
    testScores: [
      { courseId: '1', score: 88, completedAt: '2024-03-25' }
    ],
    totalTimeSpent: 780, // minutes
    lastAccessed: '2024-03-28'
  },
  {
    id: '8',
    classroomId: '3',
    studentId: '14', // Kevin Lee
    enrolledAt: '2024-03-15',
    progress: 42,
    completedCourses: [],
    testScores: [
      { courseId: '1', score: 81, completedAt: '2024-03-22' }
    ],
    totalTimeSpent: 890, // minutes
    lastAccessed: '2024-03-30'
  },
  {
    id: '9',
    classroomId: '3',
    studentId: '17', // Jessica Clark
    enrolledAt: '2024-03-15',
    progress: 28,
    completedCourses: [],
    testScores: [],
    totalTimeSpent: 520, // minutes
    lastAccessed: '2024-03-26'
  },

  // Data Science Fundamentals enrollments
  {
    id: '10',
    classroomId: '4',
    studentId: '10', // David Brown
    enrolledAt: '2024-04-01',
    progress: 20,
    completedCourses: [],
    testScores: [
      { courseId: '3', score: 75, completedAt: '2024-04-10' }
    ],
    totalTimeSpent: 640, // minutes
    lastAccessed: '2024-04-15'
  },
  {
    id: '11',
    classroomId: '4',
    studentId: '13', // Linda Anderson
    enrolledAt: '2024-04-01',
    progress: 25,
    completedCourses: [],
    testScores: [
      { courseId: '3', score: 79, completedAt: '2024-04-08' }
    ],
    totalTimeSpent: 720, // minutes
    lastAccessed: '2024-04-18'
  },
  {
    id: '12',
    classroomId: '4',
    studentId: '18', // Christopher Moore
    enrolledAt: '2024-04-01',
    progress: 15,
    completedCourses: [],
    testScores: [],
    totalTimeSpent: 480, // minutes
    lastAccessed: '2024-04-12'
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

// Quiz-related mock data
export const mockQuizAttempts = [
  // January 2024 Quiz Attempts
  { id: '1', userId: '8', courseId: '1', lessonId: 'l6', quizId: 'quiz1', attempt: 1, startedAt: '2024-01-28T10:00:00Z', completedAt: '2024-01-28T10:08:30Z', timeSpent: 510, score: 92, totalPoints: 20, earnedPoints: 18, passed: true, isTest: false, answers: [], status: 'completed' },
  { id: '2', userId: '9', courseId: '1', lessonId: 'l6', quizId: 'quiz1', attempt: 1, startedAt: '2024-01-30T14:00:00Z', completedAt: '2024-01-30T14:12:15Z', timeSpent: 735, score: 85, totalPoints: 20, earnedPoints: 17, passed: true, isTest: false, answers: [], status: 'completed' },
  { id: '3', userId: '10', courseId: '3', lessonId: 'l2', quizId: 'quiz3', attempt: 1, startedAt: '2024-01-31T16:30:00Z', completedAt: '2024-01-31T16:45:20Z', timeSpent: 920, score: 88, totalPoints: 25, earnedPoints: 22, passed: true, isTest: false, answers: [], status: 'completed' },
  
  // February 2024 Quiz Attempts
  { id: '4', userId: '11', courseId: '1', lessonId: 'l6', quizId: 'quiz1', attempt: 1, startedAt: '2024-02-08T11:00:00Z', completedAt: '2024-02-08T11:09:45Z', timeSpent: 585, score: 75, totalPoints: 20, earnedPoints: 15, passed: true, isTest: false, answers: [], status: 'completed' },
  { id: '5', userId: '12', courseId: '2', lessonId: 'l2', quizId: 'quiz2', attempt: 1, startedAt: '2024-02-10T13:15:00Z', completedAt: '2024-02-10T13:28:30Z', timeSpent: 810, score: 94, totalPoints: 30, earnedPoints: 28, passed: true, isTest: false, answers: [], status: 'completed' },
  { id: '6', userId: '13', courseId: '3', lessonId: 'l2', quizId: 'quiz3', attempt: 1, startedAt: '2024-02-12T15:00:00Z', completedAt: '2024-02-12T15:18:15Z', timeSpent: 1095, score: 82, totalPoints: 25, earnedPoints: 20, passed: true, isTest: false, answers: [], status: 'completed' },
  { id: '7', userId: '14', courseId: '4', lessonId: 'l1', quizId: 'quiz4', attempt: 1, startedAt: '2024-02-18T09:30:00Z', completedAt: '2024-02-18T09:45:00Z', timeSpent: 900, score: 71, totalPoints: 35, earnedPoints: 25, passed: true, isTest: false, answers: [], status: 'completed' },
  { id: '8', userId: '15', courseId: '5', lessonId: 'l2', quizId: 'quiz5', attempt: 1, startedAt: '2024-02-20T14:45:00Z', completedAt: '2024-02-20T15:02:30Z', timeSpent: 1050, score: 96, totalPoints: 25, earnedPoints: 24, passed: true, isTest: false, answers: [], status: 'completed' },
  
  // Final Test Attempts - February
  { id: '9', userId: '8', courseId: '1', lessonId: 'final-test', quizId: 'final-test-1', attempt: 1, startedAt: '2024-02-15T09:00:00Z', completedAt: '2024-02-15T10:30:00Z', timeSpent: 5400, score: 89, totalPoints: 100, earnedPoints: 89, passed: true, isTest: true, answers: [], status: 'completed' },
  { id: '10', userId: '12', courseId: '2', lessonId: 'final-test', quizId: 'final-test-2', attempt: 1, startedAt: '2024-02-22T10:00:00Z', completedAt: '2024-02-22T11:15:00Z', timeSpent: 4500, score: 91, totalPoints: 100, earnedPoints: 91, passed: true, isTest: true, answers: [], status: 'completed' },
  
  // March 2024 Quiz Attempts
  { id: '11', userId: '16', courseId: '5', lessonId: 'l2', quizId: 'quiz5', attempt: 1, startedAt: '2024-03-05T16:00:00Z', completedAt: '2024-03-05T16:15:45Z', timeSpent: 945, score: 87, totalPoints: 25, earnedPoints: 22, passed: true, isTest: false, answers: [], status: 'completed' },
  { id: '12', userId: '17', courseId: '6', lessonId: 'l1', quizId: 'quiz6', attempt: 1, startedAt: '2024-03-08T12:30:00Z', completedAt: '2024-03-08T12:48:20Z', timeSpent: 1100, score: 79, totalPoints: 30, earnedPoints: 24, passed: true, isTest: false, answers: [], status: 'completed' },
  { id: '13', userId: '18', courseId: '7', lessonId: 'l1', quizId: 'quiz7', attempt: 1, startedAt: '2024-03-10T10:15:00Z', completedAt: '2024-03-10T10:35:30Z', timeSpent: 1230, score: 93, totalPoints: 40, earnedPoints: 37, passed: true, isTest: false, answers: [], status: 'completed' },
  { id: '14', userId: '19', courseId: '8', lessonId: 'l1', quizId: 'quiz8', attempt: 1, startedAt: '2024-03-12T14:00:00Z', completedAt: '2024-03-12T14:22:15Z', timeSpent: 1335, score: 84, totalPoints: 35, earnedPoints: 29, passed: true, isTest: false, answers: [], status: 'completed' },
  { id: '15', userId: '20', courseId: '9', lessonId: 'l1', quizId: 'quiz9', attempt: 1, startedAt: '2024-03-15T11:45:00Z', completedAt: '2024-03-15T12:08:45Z', timeSpent: 1425, score: 78, totalPoints: 45, earnedPoints: 35, passed: true, isTest: false, answers: [], status: 'completed' },
  { id: '16', userId: '21', courseId: '1', lessonId: 'l6', quizId: 'quiz1', attempt: 1, startedAt: '2024-03-18T13:30:00Z', completedAt: '2024-03-18T13:42:00Z', timeSpent: 720, score: 90, totalPoints: 20, earnedPoints: 18, passed: true, isTest: false, answers: [], status: 'completed' },
  
  // Final Test Attempts - March
  { id: '17', userId: '15', courseId: '5', lessonId: 'final-test', quizId: 'final-test-5', attempt: 1, startedAt: '2024-03-20T13:00:00Z', completedAt: '2024-03-20T14:20:00Z', timeSpent: 4800, score: 93, totalPoints: 100, earnedPoints: 93, passed: true, isTest: true, answers: [], status: 'completed' },
  { id: '18', userId: '18', courseId: '7', lessonId: 'final-test', quizId: 'final-test-7', attempt: 1, startedAt: '2024-03-25T10:30:00Z', completedAt: '2024-03-25T12:00:00Z', timeSpent: 5400, score: 87, totalPoints: 100, earnedPoints: 87, passed: true, isTest: true, answers: [], status: 'completed' },
  
  // April 2024 Quiz Attempts
  { id: '19', userId: '8', courseId: '2', lessonId: 'l2', quizId: 'quiz2', attempt: 1, startedAt: '2024-04-05T15:00:00Z', completedAt: '2024-04-05T15:18:30Z', timeSpent: 1110, score: 86, totalPoints: 30, earnedPoints: 26, passed: true, isTest: false, answers: [], status: 'completed' },
  { id: '20', userId: '9', courseId: '6', lessonId: 'l1', quizId: 'quiz6', attempt: 1, startedAt: '2024-04-08T11:15:00Z', completedAt: '2024-04-08T11:32:45Z', timeSpent: 1065, score: 81, totalPoints: 30, earnedPoints: 24, passed: true, isTest: false, answers: [], status: 'completed' },
  { id: '21', userId: '11', courseId: '8', lessonId: 'l1', quizId: 'quiz8', attempt: 1, startedAt: '2024-04-12T16:30:00Z', completedAt: '2024-04-12T16:55:00Z', timeSpent: 1500, score: 95, totalPoints: 35, earnedPoints: 33, passed: true, isTest: false, answers: [], status: 'completed' },
  { id: '22', userId: '14', courseId: '1', lessonId: 'l6', quizId: 'quiz1', attempt: 1, startedAt: '2024-04-20T10:00:00Z', completedAt: '2024-04-20T10:11:30Z', timeSpent: 690, score: 88, totalPoints: 20, earnedPoints: 18, passed: true, isTest: false, answers: [], status: 'completed' },
  
  // May 2024 Quiz Attempts
  { id: '23', userId: '18', courseId: '1', lessonId: 'l6', quizId: 'quiz1', attempt: 1, startedAt: '2024-05-10T14:45:00Z', completedAt: '2024-05-10T14:58:15Z', timeSpent: 795, score: 83, totalPoints: 20, earnedPoints: 17, passed: true, isTest: false, answers: [], status: 'completed' },
  { id: '24', userId: '19', courseId: '2', lessonId: 'l2', quizId: 'quiz2', attempt: 1, startedAt: '2024-05-15T12:00:00Z', completedAt: '2024-05-15T12:19:30Z', timeSpent: 1170, score: 92, totalPoints: 30, earnedPoints: 28, passed: true, isTest: false, answers: [], status: 'completed' },
  { id: '25', userId: '21', courseId: '6', lessonId: 'l1', quizId: 'quiz6', attempt: 1, startedAt: '2024-05-20T09:30:00Z', completedAt: '2024-05-20T09:48:45Z', timeSpent: 1125, score: 89, totalPoints: 30, earnedPoints: 27, passed: true, isTest: false, answers: [], status: 'completed' },
  
  // Final Test Attempts - May
  { id: '26', userId: '11', courseId: '8', lessonId: 'final-test', quizId: 'final-test-8', attempt: 1, startedAt: '2024-05-25T11:00:00Z', completedAt: '2024-05-25T12:15:00Z', timeSpent: 4500, score: 94, totalPoints: 100, earnedPoints: 94, passed: true, isTest: true, answers: [], status: 'completed' },
  { id: '27', userId: '19', courseId: '2', lessonId: 'final-test', quizId: 'final-test-2', attempt: 1, startedAt: '2024-05-28T14:30:00Z', completedAt: '2024-05-28T15:45:00Z', timeSpent: 4500, score: 96, totalPoints: 100, earnedPoints: 96, passed: true, isTest: true, answers: [], status: 'completed' },
  
  // June 2024 Quiz Attempts (Recent)
  { id: '28', userId: '10', courseId: '8', lessonId: 'l1', quizId: 'quiz8', attempt: 1, startedAt: '2024-06-05T13:15:00Z', completedAt: '2024-06-05T13:38:30Z', timeSpent: 1410, score: 77, totalPoints: 35, earnedPoints: 27, passed: true, isTest: false, answers: [], status: 'completed' },
  { id: '29', userId: '13', courseId: '1', lessonId: 'l6', quizId: 'quiz1', attempt: 1, startedAt: '2024-06-10T11:00:00Z', completedAt: '2024-06-10T11:13:45Z', timeSpent: 825, score: 85, totalPoints: 20, earnedPoints: 17, passed: true, isTest: false, answers: [], status: 'completed' },
  { id: '30', userId: '14', courseId: '5', lessonId: 'l2', quizId: 'quiz5', attempt: 1, startedAt: '2024-06-15T15:30:00Z', completedAt: '2024-06-15T15:48:00Z', timeSpent: 1080, score: 91, totalPoints: 25, earnedPoints: 23, passed: true, isTest: false, answers: [], status: 'completed' },
  
  // Failed Attempts (for realistic data)
  { id: '31', userId: '22', courseId: '3', lessonId: 'l2', quizId: 'quiz3', attempt: 1, startedAt: '2024-03-20T16:00:00Z', completedAt: '2024-03-20T16:25:00Z', timeSpent: 1500, score: 65, totalPoints: 25, earnedPoints: 16, passed: false, isTest: false, answers: [], status: 'completed' },
  { id: '32', userId: '22', courseId: '3', lessonId: 'l2', quizId: 'quiz3', attempt: 2, startedAt: '2024-03-22T10:00:00Z', completedAt: '2024-03-22T10:20:30Z', timeSpent: 1230, score: 84, totalPoints: 25, earnedPoints: 21, passed: true, isTest: false, answers: [], status: 'completed' },
  { id: '33', userId: '17', courseId: '4', lessonId: 'l1', quizId: 'quiz4', attempt: 1, startedAt: '2024-04-25T14:00:00Z', completedAt: '2024-04-25T14:28:15Z', timeSpent: 1695, score: 68, totalPoints: 35, earnedPoints: 24, passed: false, isTest: false, answers: [], status: 'completed' },
  { id: '34', userId: '17', courseId: '4', lessonId: 'l1', quizId: 'quiz4', attempt: 2, startedAt: '2024-04-27T12:30:00Z', completedAt: '2024-04-27T12:52:00Z', timeSpent: 1320, score: 74, totalPoints: 35, earnedPoints: 26, passed: true, isTest: false, answers: [], status: 'completed' },
  
  // Instructor and Admin Quiz Attempts
  { id: '35', userId: '4', courseId: '1', lessonId: 'l6', quizId: 'quiz1', attempt: 1, startedAt: '2024-03-01T10:30:00Z', completedAt: '2024-03-01T10:42:15Z', timeSpent: 705, score: 100, totalPoints: 25, earnedPoints: 25, passed: true, isTest: false, answers: [], status: 'completed' },
  { id: '36', userId: '3', courseId: '9', lessonId: 'l1', quizId: 'quiz9', attempt: 1, startedAt: '2024-04-10T15:00:00Z', completedAt: '2024-04-10T15:25:30Z', timeSpent: 1530, score: 98, totalPoints: 45, earnedPoints: 44, passed: true, isTest: false, answers: [], status: 'completed' },
  { id: '37', userId: '5', courseId: '3', lessonId: 'l2', quizId: 'quiz3', attempt: 1, startedAt: '2024-03-25T11:15:00Z', completedAt: '2024-03-25T11:38:45Z', timeSpent: 1425, score: 96, totalPoints: 25, earnedPoints: 24, passed: true, isTest: false, answers: [], status: 'completed' },
  
  // In-Progress Attempts
  { id: '38', userId: '24', courseId: '9', lessonId: 'l1', quizId: 'quiz9', attempt: 1, startedAt: '2024-06-20T14:00:00Z', completedAt: null, timeSpent: 0, score: null, totalPoints: 45, earnedPoints: null, passed: null, isTest: false, answers: [], status: 'in-progress' },
  { id: '39', userId: '25', courseId: '10', lessonId: 'l1', quizId: 'quiz10', attempt: 1, startedAt: '2024-06-25T16:30:00Z', completedAt: null, timeSpent: 0, score: null, totalPoints: 50, earnedPoints: null, passed: null, isTest: false, answers: [], status: 'in-progress' }
];

export const mockQuizResults = [
  {
    id: '1',
    userId: '3',
    courseId: '1',
    lessonId: 'l6',
    quizId: 'quiz1',
    bestScore: 85,
    averageScore: 85,
    totalAttempts: 1,
    completedAttempts: 1,
    passed: true,
    firstAttemptScore: 85,
    lastAttemptAt: '2024-03-15T10:08:30Z',
    timeSpentTotal: 510 // total seconds across all attempts
  }
];

// Helper functions for quiz data
export const getQuizAttempts = (userId, courseId, lessonId, quizId) => {
  return mockQuizAttempts.filter(attempt => 
    attempt.userId === userId && 
    attempt.courseId === courseId && 
    attempt.lessonId === lessonId && 
    attempt.quizId === quizId
  );
};

export const getQuizResults = (userId, courseId, lessonId, quizId) => {
  return mockQuizResults.find(result => 
    result.userId === userId && 
    result.courseId === courseId && 
    result.lessonId === lessonId && 
    result.quizId === quizId
  );
};

export const getUserQuizResults = (userId) => {
  return mockQuizResults.filter(result => result.userId === userId);
};

export const getInstructorQuizAnalytics = (instructorId) => {
  // In real app, would filter by instructor's courses
  const instructorCourses = mockCourses.filter(course => course.instructorId === instructorId);
  const courseIds = instructorCourses.map(course => course.id);
  
  const relevantResults = mockQuizResults.filter(result => 
    courseIds.includes(result.courseId)
  );
  
  return {
    totalQuizzes: instructorCourses.reduce((total, course) => {
      const quizLessons = course.modules?.reduce((moduleTotal, module) => {
        return moduleTotal + (module.lessons?.filter(lesson => lesson.type === 'quiz')?.length || 0);
      }, 0) || 0;
      return total + quizLessons;
    }, 0),
    totalAttempts: relevantResults.reduce((total, result) => total + result.totalAttempts, 0),
    averageScore: relevantResults.length > 0 
      ? relevantResults.reduce((total, result) => total + result.averageScore, 0) / relevantResults.length 
      : 0,
    passRate: relevantResults.length > 0 
      ? (relevantResults.filter(result => result.passed).length / relevantResults.length) * 100 
      : 0
  };
};

// Department helper functions
export const getDepartments = () => {
  return mockDepartments;
};

export const getDepartmentById = (departmentId) => {
  return mockDepartments.find(dept => dept.id === departmentId);
};

export const getUsersByDepartment = (departmentId) => {
  return mockUsers.filter(user => user.departmentId === departmentId);
};

// Program deadline helper functions
export const getProgramDeadlineStatus = (deadline) => {
  const today = new Date();
  const deadlineDate = new Date(deadline);
  const daysRemaining = Math.ceil((deadlineDate - today) / (1000 * 60 * 60 * 24));
  
  if (daysRemaining < 0) {
    return { status: 'overdue', daysRemaining: Math.abs(daysRemaining), message: `Overdue by ${Math.abs(daysRemaining)} days` };
  } else if (daysRemaining <= 7) {
    return { status: 'urgent', daysRemaining, message: `${daysRemaining} days remaining` };
  } else if (daysRemaining <= 30) {
    return { status: 'warning', daysRemaining, message: `${daysRemaining} days remaining` };
  } else {
    return { status: 'normal', daysRemaining, message: `${daysRemaining} days remaining` };
  }
};

export const getProgramsWithDeadlineStatus = () => {
  return mockPrograms.map(program => ({
    ...program,
    deadlineStatus: program.deadline ? getProgramDeadlineStatus(program.deadline) : null
  }));
};

// Course progression helper functions
export const getUserProgramProgress = (userId, programId) => {
  const enrollment = mockProgramEnrollments.find(e => e.userId === userId && e.programId === programId);
  return enrollment || null;
};

export const isCourseUnlocked = (userId, programId, courseId) => {
  const program = mockPrograms.find(p => p.id === programId);
  if (!program) return false;

  const courseIndex = program.courseOrder.indexOf(courseId);
  if (courseIndex === -1) return false;
  
  // First course is always unlocked
  if (courseIndex === 0) return true;
  
  // Check if previous course is completed with passing grade
  const previousCourseId = program.courseOrder[courseIndex - 1];
  const userEnrollment = mockEnrollments.find(e => 
    e.userId === userId && e.courseId === previousCourseId
  );
  
  // Course is unlocked if previous course has 100% completion
  return userEnrollment && userEnrollment.progress === 100;
};

export const getCourseProgressionStatus = (userId, programId) => {
  const program = mockPrograms.find(p => p.id === programId);
  if (!program) return [];

  return program.courseOrder.map((courseId, index) => {
    const course = mockCourses.find(c => c.id === courseId);
    const isUnlocked = isCourseUnlocked(userId, programId, courseId);
    const userEnrollment = mockEnrollments.find(e => 
      e.userId === userId && e.courseId === courseId
    );
    
    return {
      ...course,
      courseId,
      index,
      isUnlocked,
      isCompleted: userEnrollment?.progress === 100,
      progress: userEnrollment?.progress || 0,
      status: !isUnlocked ? 'locked' : 
              userEnrollment?.progress === 100 ? 'completed' :
              userEnrollment?.progress > 0 ? 'in-progress' : 'available'
    };
  });
};

// Classroom access control helper functions
export const isClassroomExpired = (classroom) => {
  if (!classroom.endDate) return false;
  const today = new Date();
  const endDate = new Date(classroom.endDate);
  return today > endDate;
};

export const getClassroomAccessStatus = (classroom) => {
  if (!classroom.endDate) {
    return { hasAccess: true, status: 'no-end-date', message: 'No end date set' };
  }
  
  const today = new Date();
  const endDate = new Date(classroom.endDate);
  const daysRemaining = Math.ceil((endDate - today) / (1000 * 60 * 60 * 24));
  
  if (daysRemaining < 0) {
    return { 
      hasAccess: false, 
      status: 'expired', 
      message: `Classroom ended ${Math.abs(daysRemaining)} days ago`,
      daysOverdue: Math.abs(daysRemaining)
    };
  } else if (daysRemaining <= 7) {
    return { 
      hasAccess: true, 
      status: 'ending-soon', 
      message: `Classroom ends in ${daysRemaining} days`,
      daysRemaining
    };
  } else {
    return { 
      hasAccess: true, 
      status: 'active', 
      message: `${daysRemaining} days remaining`,
      daysRemaining
    };
  }
};

export const getUserClassroomAccess = (userId, classroomId) => {
  // Check if user is enrolled in classroom
  const enrollment = mockClassroomEnrollments.find(e => 
    e.studentId === userId && e.classroomId === classroomId
  );
  
  if (!enrollment) {
    return { hasAccess: false, reason: 'not-enrolled', message: 'You are not enrolled in this classroom' };
  }
  
  // Check if classroom has expired
  const classroom = mockClassrooms.find(c => c.id === classroomId);
  const accessStatus = getClassroomAccessStatus(classroom);
  
  if (!accessStatus.hasAccess) {
    return { 
      hasAccess: false, 
      reason: 'classroom-expired', 
      message: accessStatus.message,
      ...accessStatus 
    };
  }
  
  return { hasAccess: true, status: accessStatus.status, message: accessStatus.message };
};

// Program helper functions for edit functionality
export const getProgramById = (programId) => {
  return mockPrograms.find(program => program.id === programId);
};

export const updateProgram = (programId, updatedProgram) => {
  const programIndex = mockPrograms.findIndex(p => p.id === programId);
  if (programIndex === -1) return false;
  
  // Update the program in the mock data
  mockPrograms[programIndex] = {
    ...mockPrograms[programIndex],
    ...updatedProgram,
    id: programId // Ensure ID doesn't change
  };
  
  return true;
};

export const addProgram = (newProgram) => {
  // Add the new program to the mock data array
  mockPrograms.push(newProgram);
  return true;
};

// Notification system data structures
export const mockNotifications = [
  // Mike Johnson (ID: 8) notifications
  {
    id: '1',
    userId: '8',
    type: 'classroom_assignment',
    title: 'Assigned to New Classroom',
    message: 'You have been assigned to "Q1 2024 New Agent Training" classroom.',
    classroomId: '1',
    isRead: false,
    createdAt: '2024-03-01T09:00:00Z',
    actionUrl: '/classroom/1'
  },
  {
    id: '2',
    userId: '8',
    type: 'classroom_assignment',
    title: 'Assigned to New Classroom',
    message: 'You have been assigned to "Advanced Python Bootcamp" classroom.',
    classroomId: '2',
    isRead: false,
    createdAt: '2024-02-15T10:30:00Z',
    actionUrl: '/classroom/2'
  },
  
  // Jennifer Williams (ID: 9) notifications
  {
    id: '3',
    userId: '9',
    type: 'classroom_assignment',
    title: 'Assigned to New Classroom',
    message: 'You have been assigned to "Q1 2024 New Agent Training" classroom.',
    classroomId: '1',
    isRead: true,
    createdAt: '2024-03-01T09:00:00Z',
    actionUrl: '/classroom/1'
  },
  {
    id: '4',
    userId: '9',
    type: 'classroom_assignment',
    title: 'Assigned to New Classroom',
    message: 'You have been assigned to "Web Development Intensive" classroom.',
    classroomId: '3',
    isRead: false,
    createdAt: '2024-03-15T14:15:00Z',
    actionUrl: '/classroom/3'
  },
  
  // David Brown (ID: 10) notifications
  {
    id: '5',
    userId: '10',
    type: 'classroom_assignment',
    title: 'Assigned to New Classroom',
    message: 'You have been assigned to "Advanced Python Bootcamp" classroom.',
    classroomId: '2',
    isRead: false,
    createdAt: '2024-02-15T10:30:00Z',
    actionUrl: '/classroom/2'
  },
  {
    id: '6',
    userId: '10',
    type: 'classroom_assignment',
    title: 'Assigned to New Classroom',
    message: 'You have been assigned to "Data Science Fundamentals" classroom.',
    classroomId: '4',
    isRead: false,
    createdAt: '2024-04-01T11:45:00Z',
    actionUrl: '/classroom/4'
  },
  
  // Maria Garcia (ID: 11) notifications
  {
    id: '7',
    userId: '11',
    type: 'classroom_assignment',
    title: 'Assigned to New Classroom',
    message: 'You have been assigned to "Q1 2024 New Agent Training" classroom.',
    classroomId: '1',
    isRead: true,
    createdAt: '2024-03-01T09:00:00Z',
    actionUrl: '/classroom/1'
  },
  
  // Linda Anderson (ID: 13) notifications
  {
    id: '8',
    userId: '13',
    type: 'classroom_assignment',
    title: 'Assigned to New Classroom',
    message: 'You have been assigned to "Advanced Python Bootcamp" classroom.',
    classroomId: '2',
    isRead: false,
    createdAt: '2024-02-15T10:30:00Z',
    actionUrl: '/classroom/2'
  },
  {
    id: '9',
    userId: '13',
    type: 'classroom_assignment',
    title: 'Assigned to New Classroom',
    message: 'You have been assigned to "Data Science Fundamentals" classroom.',
    classroomId: '4',
    isRead: false,
    createdAt: '2024-04-01T11:45:00Z',
    actionUrl: '/classroom/4'
  },
  
  // Kevin Lee (ID: 14) notifications
  {
    id: '10',
    userId: '14',
    type: 'classroom_assignment',
    title: 'Assigned to New Classroom',
    message: 'You have been assigned to "Web Development Intensive" classroom.',
    classroomId: '3',
    isRead: false,
    createdAt: '2024-03-15T14:15:00Z',
    actionUrl: '/classroom/3'
  },
  
  // Jessica Clark (ID: 17) notifications
  {
    id: '11',
    userId: '17',
    type: 'classroom_assignment',
    title: 'Assigned to New Classroom',
    message: 'You have been assigned to "Web Development Intensive" classroom.',
    classroomId: '3',
    isRead: true,
    createdAt: '2024-03-15T14:15:00Z',
    actionUrl: '/classroom/3'
  },
  
  // Christopher Moore (ID: 18) notifications
  {
    id: '12',
    userId: '18',
    type: 'classroom_assignment',
    title: 'Assigned to New Classroom',
    message: 'You have been assigned to "Data Science Fundamentals" classroom.',
    classroomId: '4',
    isRead: false,
    createdAt: '2024-04-01T11:45:00Z',
    actionUrl: '/classroom/4'
  }
];

// Helper functions for notifications
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

// Check if student is assigned to classrooms (for notification badge logic)
export const getStudentClassroomAssignments = (userId) => {
  // Find classrooms where the student is assigned
  const assignedClassrooms = mockClassrooms.filter(classroom => 
    classroom.studentIds.includes(userId)
  );
  
  // Also check classroom enrollments
  const enrolledClassrooms = mockClassroomEnrollments
    .filter(enrollment => enrollment.studentId === userId)
    .map(enrollment => mockClassrooms.find(c => c.id === enrollment.classroomId))
    .filter(Boolean);
  
  // Combine and deduplicate
  const allClassrooms = [...assignedClassrooms];
  enrolledClassrooms.forEach(classroom => {
    if (!allClassrooms.find(c => c.id === classroom.id)) {
      allClassrooms.push(classroom);
    }
  });
  
  return allClassrooms;
};

export const hasUnreadClassroomAssignments = (userId) => {
  const unreadNotifications = getUnreadNotifications(userId);
  return unreadNotifications.some(notification => 
    notification.type === 'classroom_assignment'
  );
};