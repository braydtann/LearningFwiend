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
          { 
            id: 'l6', 
            title: 'Component Quiz', 
            type: 'quiz', 
            duration: '10 min',
            quiz: {
              id: 'quiz1',
              title: 'React Components Quiz',
              description: 'Test your knowledge of React components and JSX',
              timeLimit: 10, // minutes
              maxAttempts: 3,
              passingScore: 70,
              shuffleQuestions: true,
              showResults: true,
              questions: [
                {
                  id: 'q1',
                  type: 'multiple-choice',
                  question: 'What does JSX stand for?',
                  questionImage: 'https://images.unsplash.com/photo-1555066931-4365d14bab8c?w=400&h=200&fit=crop',
                  options: [
                    { text: 'JavaScript XML', image: '', audio: '' },
                    { text: 'Java Syntax Extension', image: '', audio: '' },
                    { text: 'JavaScript Extension', image: '', audio: '' },
                    { text: 'Just Simple XML', image: '', audio: '' }
                  ],
                  correctAnswer: 0,
                  points: 5,
                  explanation: 'JSX stands for JavaScript XML. It allows you to write HTML-like syntax in JavaScript.'
                },
                {
                  id: 'q2',
                  type: 'select-all-that-apply',
                  question: 'Which of the following are valid React hooks? (Select all that apply)',
                  questionAudio: 'https://www.soundjay.com/misc/sounds/bell-ringing-05.wav',
                  options: [
                    { text: 'useState', image: 'https://images.unsplash.com/photo-1633356122544-f134324a6cee?w=100&h=100&fit=crop', audio: '' },
                    { text: 'useEffect', image: 'https://images.unsplash.com/photo-1633356122102-3fe601e05bd2?w=100&h=100&fit=crop', audio: '' },
                    { text: 'useProps', image: '', audio: '' },
                    { text: 'useContext', image: 'https://images.unsplash.com/photo-1633356122544-f134324a6cee?w=100&h=100&fit=crop', audio: '' },
                    { text: 'useComponent', image: '', audio: '' }
                  ],
                  correctAnswers: [0, 1, 3], // useState, useEffect, useContext
                  points: 8,
                  explanation: 'useState, useEffect, and useContext are built-in React hooks. useProps and useComponent do not exist.'
                },
                {
                  id: 'q4',
                  type: 'true-false',
                  question: 'React components must always return a single element.',
                  correctAnswer: true,
                  points: 3,
                  explanation: 'React components must return a single element, but it can contain multiple child elements.'
                },
                {
                  id: 'q5',
                  type: 'chronological-order',
                  question: 'Arrange the following React component lifecycle phases in chronological order:',
                  items: [
                    { text: 'Component mounts', image: 'https://images.unsplash.com/photo-1518073176059-65c11ec1d93b?w=100&h=100&fit=crop', audio: '' },
                    { text: 'Component updates', image: 'https://images.unsplash.com/photo-1516321497487-e288fb19713f?w=100&h=100&fit=crop', audio: '' },
                    { text: 'Component unmounts', image: 'https://images.unsplash.com/photo-1516321497487-e288fb19713f?w=100&h=100&fit=crop', audio: '' },
                    { text: 'Component renders', image: 'https://images.unsplash.com/photo-1516321497487-e288fb19713f?w=100&h=100&fit=crop', audio: '' }
                  ],
                  correctOrder: [0, 3, 1, 2], // Mount -> Render -> Update -> Unmount
                  points: 10,
                  explanation: 'React components follow the lifecycle: Mount → Render → Update (if needed) → Unmount'
                },
                {
                  id: 'q6',
                  type: 'long-form-answer',
                  question: 'Explain the concept of "lifting state up" in React and provide a practical example of when you would use this pattern.',
                  sampleAnswer: 'Lifting state up means moving state from child components to their common parent component when multiple children need to share or synchronize state. For example, if you have two sibling components that need to display and modify the same user data, you would move the user state to their parent component and pass it down as props.',
                  points: 15,
                  explanation: 'This question tests understanding of React state management patterns and requires manual grading for full credit.',
                  wordLimit: 500
                },
                {
                  id: 'q7',
                  type: 'multiple-choice-multimedia',
                  question: 'Which of the following code snippets correctly implements a React functional component?',
                  options: [
                    {
                      type: 'image',
                      url: 'https://images.unsplash.com/photo-1555066931-4365d14bab8c?w=300&h=200&fit=crop',
                      alt: 'Code snippet showing function component'
                    },
                    {
                      type: 'text',
                      content: 'const MyComponent = () => { return <div>Hello</div>; }'
                    },
                    {
                      type: 'text', 
                      content: 'class MyComponent extends Component { render() { return <div>Hello</div>; } }'
                    },
                    {
                      type: 'text',
                      content: 'function MyComponent() { return <div>Hello</div>; }'
                    }
                  ],
                  correctAnswer: 1,
                  points: 6,
                  explanation: 'Both arrow functions and regular functions can be used for functional components, but option B shows the modern arrow function syntax.'
                }
              ]
            }
          }
        ]
      }
    ],
    finalTest: {
      id: 'final_test_1',
      title: 'React Development Fundamentals - Final Assessment',
      description: 'Comprehensive test covering all React topics from the course',
      timeLimit: 120, // 120 minutes
      maxAttempts: 3,
      passingScore: 70,
      shuffleQuestions: true,
      showResults: true,
      questions: [
        {
          id: 'ft_q1',
          type: 'multiple-choice',
          question: 'What is the primary purpose of React?',
          options: [
            'To build user interfaces',
            'To manage databases', 
            'To handle server requests',
            'To create mobile apps only'
          ],
          correctAnswer: 0,
          points: 5,
          explanation: 'React is a JavaScript library primarily used for building user interfaces.'
        },
        {
          id: 'ft_q2',
          type: 'select-all-that-apply',
          question: 'Which of the following are React lifecycle methods? (Select all that apply)',
          options: [
            'componentDidMount',
            'componentWillUpdate', 
            'componentDidUpdate',
            'componentWillUnmount',
            'componentDidCreate'
          ],
          correctAnswers: [0, 2, 3], // componentDidMount, componentDidUpdate, componentWillUnmount
          points: 12,
          explanation: 'componentDidMount, componentDidUpdate, and componentWillUnmount are valid React lifecycle methods. componentDidCreate does not exist.'
        },
        {
          id: 'ft_q3',
          type: 'long-form-answer',
          question: 'Compare and contrast functional components with class components in React. Discuss the advantages and disadvantages of each approach and when you might choose one over the other.',
          sampleAnswer: 'Functional components are simpler, easier to test, and can use hooks for state management. Class components have more verbose syntax but provide lifecycle methods. With hooks, functional components can do everything class components can do, making them preferred for modern React development.',
          points: 25,
          explanation: 'This question tests comprehensive understanding of React component types.',
          wordLimit: 600
        }
      ]
    }
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
    ],
    finalTest: {
      id: 'final_test_2',
      title: 'Python for Data Science - Final Assessment',
      description: 'Comprehensive test covering all topics from the Python for Data Science course',
      timeLimit: 90, // 90 minutes
      maxAttempts: 2,
      passingScore: 75,
      shuffleQuestions: true,
      showResults: true,
      questions: [
        {
          id: 'ft_q1',
          type: 'select-all-that-apply',
          question: 'Which of the following are valid Python data types? (Select all that apply)',
          options: ['int', 'string', 'list', 'boolean', 'array'],
          correctAnswers: [0, 1, 2, 3], // int, string, list, boolean (array is not a built-in type)
          points: 10,
          explanation: 'Python has int, str (string), list, and bool data types built-in. Array is available through numpy, not built-in.'
        },
        {
          id: 'ft_q2',
          type: 'chronological-order',
          question: 'Arrange the following steps of a typical data science workflow in chronological order:',
          items: [
            'Data Collection',
            'Data Analysis', 
            'Data Cleaning',
            'Model Deployment',
            'Model Training'
          ],
          correctOrder: [0, 2, 1, 4, 3], // Collection -> Cleaning -> Analysis -> Training -> Deployment
          points: 15,
          explanation: 'Data science workflow: Collect data → Clean data → Analyze data → Train models → Deploy models'
        },
        {
          id: 'ft_q3',
          type: 'long-form-answer',
          question: 'Explain the difference between supervised and unsupervised learning. Provide examples of each and discuss when you would use one approach over the other.',
          sampleAnswer: 'Supervised learning uses labeled training data to learn patterns and make predictions on new data (e.g., email spam detection, image classification). Unsupervised learning finds hidden patterns in unlabeled data (e.g., customer segmentation, anomaly detection). Use supervised when you have labeled examples; use unsupervised for exploration and pattern discovery.',
          points: 20,
          explanation: 'This question tests understanding of core machine learning concepts.',
          wordLimit: 750
        }
      ]
    }
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
    lastAccessed: '2024-03-15',
    timeSpent: 12.5 // hours
  },
  {
    id: '2',
    userId: '3',
    courseId: '2',
    enrolledAt: '2024-03-08',
    progress: 25,
    completedLessons: ['l7'],
    lastAccessed: '2024-03-12',
    timeSpent: 8.2 // hours
  },
  // Additional enrollments for better analytics
  {
    id: '3',
    userId: '2', // instructor as learner
    courseId: '3',
    enrolledAt: '2024-02-15',
    progress: 100,
    completedLessons: ['l8', 'l9'],
    lastAccessed: '2024-03-01',
    timeSpent: 15.8
  },
  {
    id: '4',
    userId: '1', // admin as learner
    courseId: '1',
    enrolledAt: '2024-01-20',
    progress: 45,
    completedLessons: ['l1', 'l2'],
    lastAccessed: '2024-03-18',
    timeSpent: 7.3
  },
  {
    id: '5',
    userId: '2',
    courseId: '2',
    enrolledAt: '2024-02-01',
    progress: 80,
    completedLessons: ['l7', 'l8'],
    lastAccessed: '2024-03-10',
    timeSpent: 18.7
  },
  {
    id: '6',
    userId: '1',
    courseId: '3',
    enrolledAt: '2024-03-01',
    progress: 30,
    completedLessons: ['l8'],
    lastAccessed: '2024-03-14',
    timeSpent: 4.5
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

// Quiz-related mock data
export const mockQuizAttempts = [
  {
    id: '1',
    userId: '3',
    courseId: '1',
    lessonId: 'l6',
    quizId: 'quiz1',
    attempt: 1,
    startedAt: '2024-03-15T10:00:00Z',
    completedAt: '2024-03-15T10:08:30Z',
    timeSpent: 510, // seconds
    score: 85,
    totalPoints: 20,
    earnedPoints: 17,
    passed: true,
    answers: [
      { questionId: 'q1', answer: 0, correct: true, points: 5 },
      { questionId: 'q2', answer: 0, correct: true, points: 5 },
      { questionId: 'q3', answer: true, correct: true, points: 3 },
      { questionId: 'q4', answer: 'To create reusable UI components', correct: true, points: 4 }
    ],
    status: 'completed'
  },
  {
    id: '2',
    userId: '3',
    courseId: '1',
    lessonId: 'l6',
    quizId: 'quiz1',
    attempt: 2,
    startedAt: '2024-03-16T14:00:00Z',
    completedAt: null,
    timeSpent: 0,
    score: null,
    totalPoints: 20,
    earnedPoints: null,
    passed: null,
    answers: [],
    status: 'in-progress'
  }
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