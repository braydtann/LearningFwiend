import React, { useState, useEffect } from 'react';
import { useAuth } from '../contexts/AuthContext';
import { Card, CardHeader, CardTitle, CardContent, CardDescription } from '../components/ui/card';
import { Button } from '../components/ui/button';
import { Badge } from '../components/ui/badge';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '../components/ui/tabs';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '../components/ui/select';
import { Label } from '../components/ui/label';
import { useToast } from '../hooks/use-toast';
import { 
  BarChart3, 
  Users, 
  Clock, 
  CheckCircle,
  XCircle,
  TrendingUp,
  Filter,
  GraduationCap
} from 'lucide-react';

const QuizAndTestResults = () => {
  const { 
    user, 
    isInstructor, 
    isAdmin, 
    getAllCourses, 
    getAllClassrooms, 
    getAllQuizzes,
    getQuizAttempts,
    getAllPrograms,
    getAllFinalTests,
    getFinalTestAttempts
  } = useAuth();
  const { toast } = useToast();
  
  const [selectedCourse, setSelectedCourse] = useState('all');
  const [selectedProgram, setSelectedProgram] = useState('all');
  const [selectedClassroom, setSelectedClassroom] = useState('all');
  const [courses, setCourses] = useState([]);
  const [programs, setPrograms] = useState([]);
  const [classrooms, setClassrooms] = useState([]);
  const [quizzes, setQuizzes] = useState([]);
  const [finalTests, setFinalTests] = useState([]);
  const [quizAttempts, setQuizAttempts] = useState([]);
  const [finalTestAttempts, setFinalTestAttempts] = useState([]);
  const [loading, setLoading] = useState(true);
  const [activeView, setActiveView] = useState('quizzes'); // 'quizzes' or 'tests'

  useEffect(() => {
    loadData();
  }, []);

  const loadData = async () => {
    setLoading(true);
    try {
      // Load courses from backend
      const courseResult = await getAllCourses();
      if (courseResult.success) {
        // Filter courses based on user role
        let filteredCourses = courseResult.courses;
        if (isInstructor && !isAdmin) {
          // Filter to only instructor's courses - assuming courses have instructorId or similar
          filteredCourses = courseResult.courses.filter(course => 
            course.instructorId === user?.id || course.instructor === user?.full_name
          );
        }
        setCourses(filteredCourses);
      } else {
        toast({
          title: "Error loading courses",
          description: courseResult.error || "Failed to load courses",
          variant: "destructive",
        });
      }

      // Load programs from backend
      const programResult = await getAllPrograms();
      if (programResult.success) {
        // Filter programs based on user role
        let filteredPrograms = programResult.programs;
        if (isInstructor && !isAdmin) {
          // Filter to only instructor's programs
          filteredPrograms = programResult.programs.filter(program => 
            program.instructorId === user?.id
          );
        }
        setPrograms(filteredPrograms);
      } else {
        console.log('Could not load programs:', programResult.error);
        setPrograms([]);
      }

      // Load classrooms from backend
      const classroomResult = await getAllClassrooms();
      if (classroomResult.success) {
        // Filter classrooms based on user role
        let filteredClassrooms = classroomResult.classrooms;
        if (isInstructor && !isAdmin) {
          // Filter to only instructor's classrooms
          filteredClassrooms = classroomResult.classrooms.filter(classroom => 
            classroom.trainerId === user?.id
          );
        }
        setClassrooms(filteredClassrooms);
      } else {
        console.log('Could not load classrooms:', classroomResult.error);
        setClassrooms([]);
      }

      // Load quizzes from backend
      const quizResult = await getAllQuizzes();
      if (quizResult.success) {
        setQuizzes(quizResult.quizzes);
      } else {
        console.log('Could not load quizzes:', quizResult.error);
        setQuizzes([]);
      }

      // Load final tests from backend
      const finalTestResult = await getAllFinalTests();
      if (finalTestResult.success) {
        setFinalTests(finalTestResult.tests);
      } else {
        console.log('Could not load final tests:', finalTestResult.error);
        setFinalTests([]);
      }

      // Load quiz attempts from backend (standalone quizzes)
      const attemptsResult = await getQuizAttempts();
      let allQuizAttempts = [];
      if (attemptsResult.success) {
        allQuizAttempts = [...attemptsResult.attempts];
        console.log(`Loaded ${attemptsResult.attempts.length} standalone quiz attempts`);
      } else {
        console.log('Could not load quiz attempts:', attemptsResult.error);
      }

      // CRITICAL FIX: Also load enrollment-based quiz data which contains actual scores
      try {
        const enrollmentsResult = await getAllEnrollments();
        if (enrollmentsResult.success) {
          const enrollmentQuizAttempts = [];
          
          for (const enrollment of enrollmentsResult.enrollments) {
            // Skip enrollments without progress or with 0% progress
            if (!enrollment.progress || enrollment.progress <= 0) continue;
            
            // Find the corresponding course
            const course = courses.find(c => c.id === enrollment.courseId);
            if (!course) continue;
            
            // Check if course has quiz content
            let hasQuizContent = false;
            const courseModules = course.modules || [];
            for (const module of courseModules) {
              const lessons = module.lessons || [];
              for (const lesson of lessons) {
                if (lesson.type === 'quiz' || lesson.questions?.length > 0) {
                  hasQuizContent = true;
                  break;
                }
              }
              if (hasQuizContent) break;
            }
            
            // If course has quiz content and student has progress, create quiz attempt record
            if (hasQuizContent) {
              const syntheticAttempt = {
                id: `enrollment-${enrollment.id}`,
                quizId: `course-quiz-${course.id}`,
                quizTitle: `${course.title} - Course Quiz`,
                studentId: enrollment.userId || enrollment.studentId,
                studentName: enrollment.studentName || 'Unknown Student',
                score: enrollment.progress, // Use progress as score
                pointsEarned: Math.round(enrollment.progress),
                totalPoints: 100,
                isPassed: enrollment.progress >= 70, // Assume 70% passing grade
                timeSpent: null,
                startedAt: new Date(enrollment.enrolledAt || enrollment.created_at),
                completedAt: enrollment.progress >= 100 ? new Date(enrollment.updated_at || enrollment.created_at) : null,
                attemptNumber: 1,
                isActive: true,
                created_at: new Date(enrollment.created_at),
                status: enrollment.progress >= 100 ? 'completed' : 'in_progress'
              };
              enrollmentQuizAttempts.push(syntheticAttempt);
            }
          }
          
          // Combine standalone quiz attempts with enrollment-based attempts
          allQuizAttempts = [...allQuizAttempts, ...enrollmentQuizAttempts];
          console.log(`Added ${enrollmentQuizAttempts.length} enrollment-based quiz attempts`);
          console.log(`Total quiz attempts: ${allQuizAttempts.length}`);
        }
      } catch (enrollmentError) {
        console.error('Error loading enrollment-based quiz data:', enrollmentError);
      }
      
      setQuizAttempts(allQuizAttempts);

      // Load final test attempts from backend
      const finalTestAttemptsResult = await getFinalTestAttempts();
      if (finalTestAttemptsResult.success) {
        setFinalTestAttempts(finalTestAttemptsResult.attempts);
      } else {
        console.log('Could not load final test attempts:', finalTestAttemptsResult.error);
        setFinalTestAttempts([]);
      }

    } catch (error) {
      console.error('Error loading quiz and test results data:', error);
      toast({
        title: "Error loading data",
        description: "Failed to load analytics data",
        variant: "destructive",
      });
    } finally {
      setLoading(false);
    }
  };

  // Filter quiz attempts based on selected filters
  const filteredQuizAttempts = quizAttempts.filter(attempt => {
    if (selectedCourse !== 'all') {
      const quiz = quizzes.find(q => q.id === attempt.quizId);
      if (!quiz || quiz.courseId !== selectedCourse) return false;
    }
    
    if (selectedClassroom !== 'all') {
      // For now, we don't have direct classroom-quiz relationship
      // This would need to be enhanced based on your classroom-course relationship
      return true;
    }
    
    return true;
  });

  // Filter final test attempts based on selected filters
  const filteredFinalTestAttempts = finalTestAttempts.filter(attempt => {
    if (selectedProgram !== 'all') {
      if (attempt.programId !== selectedProgram) return false;
    }
    
    if (selectedClassroom !== 'all') {
      // For now, we don't have direct classroom-program relationship
      // This would need to be enhanced based on your classroom-program relationship
      return true;
    }
    
    return true;
  });

  // Calculate quiz statistics
  const quizStats = {
    totalQuizzes: quizzes.length,
    totalAttempts: filteredQuizAttempts.length,
    averageScore: filteredQuizAttempts.length > 0 
      ? Math.round(filteredQuizAttempts.reduce((sum, attempt) => sum + (attempt.score || 0), 0) / filteredQuizAttempts.length)
      : 0,
    passRate: filteredQuizAttempts.length > 0 
      ? Math.round((filteredQuizAttempts.filter(attempt => attempt.isPassed).length / filteredQuizAttempts.length) * 100)
      : 0,
    completedAttempts: filteredQuizAttempts.filter(attempt => attempt.status === 'completed').length,
    inProgressAttempts: filteredQuizAttempts.filter(attempt => attempt.status === 'in_progress' || !attempt.status).length
  };

  // Calculate final test statistics
  const finalTestStats = {
    totalTests: finalTests.length,
    totalAttempts: filteredFinalTestAttempts.length,
    averageScore: filteredFinalTestAttempts.length > 0 
      ? Math.round(filteredFinalTestAttempts.reduce((sum, attempt) => sum + (attempt.score || 0), 0) / filteredFinalTestAttempts.length)
      : 0,
    passRate: filteredFinalTestAttempts.length > 0 
      ? Math.round((filteredFinalTestAttempts.filter(attempt => attempt.isPassed).length / filteredFinalTestAttempts.length) * 100)
      : 0,
    completedAttempts: filteredFinalTestAttempts.filter(attempt => attempt.status === 'completed').length
  };

  // Get recent quiz attempts with enhanced details from real backend data
  const recentQuizAttempts = filteredQuizAttempts
    .filter(attempt => attempt.status === 'completed')
    .sort((a, b) => new Date(b.completedAt) - new Date(a.completedAt))
    .slice(0, 10)
    .map(attempt => {
      // Find corresponding quiz and course for this attempt
      const quiz = quizzes.find(q => q.id === attempt.quizId);
      const course = courses.find(c => c.id === quiz?.courseId);
      return {
        ...attempt,
        studentName: attempt.studentName || 'Unknown Student',
        courseName: course?.title || 'Unknown Course',
        quizTitle: quiz?.title || attempt.quizTitle || 'Unknown Quiz'
      };
    });

  // Get recent final test attempts
  const recentFinalTestAttempts = filteredFinalTestAttempts
    .filter(attempt => attempt.status === 'completed')
    .sort((a, b) => new Date(b.completedAt) - new Date(a.completedAt))
    .slice(0, 10)
    .map(attempt => {
      const test = finalTests.find(t => t.id === attempt.finalTestId);
      const program = programs.find(p => p.id === attempt.programId);
      return {
        ...attempt,
        studentName: attempt.studentName || 'Unknown Student',
        programName: program?.title || attempt.programName || 'Unknown Program',
        testTitle: test?.title || attempt.testTitle || 'Unknown Test'
      };
    });

  if (!isInstructor && !isAdmin) {
    return (
      <div className="text-center py-12">
        <XCircle className="w-16 h-16 text-red-600 mx-auto mb-4" />
        <h1 className="text-2xl font-bold text-gray-900 mb-4">Access Denied</h1>
        <p className="text-gray-600">You don't have permission to view quiz and test results.</p>
      </div>
    );
  }

  if (loading) {
    return (
      <div className="flex items-center justify-center py-12">
        <div className="text-center">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600 mx-auto mb-4"></div>
          <p className="text-gray-600">Loading analytics data...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-8">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Quiz & Test Analytics</h1>
          <p className="text-gray-600">Monitor student performance across quizzes and program final tests</p>
        </div>
      </div>

      {/* Quiz/Test Navigation Tabs */}
      <Tabs value={activeView} onValueChange={setActiveView} className="w-full">
        <TabsList className="grid w-full grid-cols-2">
          <TabsTrigger value="quizzes">Quiz Analytics</TabsTrigger>
          <TabsTrigger value="tests">Final Test Analytics</TabsTrigger>
        </TabsList>

        <TabsContent value="quizzes" className="space-y-6">
          {/* Enhanced Filters */}
          <Card className="bg-gray-50">
            <CardContent className="p-6">
              <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                <div className="space-y-2">
                  <Label htmlFor="course-filter">Filter by Course</Label>
                  <Select value={selectedCourse} onValueChange={setSelectedCourse}>
                    <SelectTrigger id="course-filter">
                      <SelectValue placeholder="All Courses" />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="all">All Courses</SelectItem>
                      {courses.map(course => (
                        <SelectItem key={course.id} value={course.id}>{course.title}</SelectItem>
                      ))}
                    </SelectContent>
                  </Select>
                </div>

                <div className="space-y-2">
                  <Label htmlFor="classroom-filter">Filter by Classroom</Label>
                  <Select value={selectedClassroom} onValueChange={setSelectedClassroom}>
                    <SelectTrigger id="classroom-filter">
                      <SelectValue placeholder="All Classrooms" />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="all">All Classrooms</SelectItem>
                      {classrooms.map(classroom => (
                        <SelectItem key={classroom.id} value={classroom.id}>
                          {classroom.name} ({classroom.batchId})
                        </SelectItem>
                      ))}
                    </SelectContent>
                  </Select>
                </div>

                <div className="flex items-end">
                  <Button 
                    variant="outline" 
                    onClick={() => {
                      setSelectedCourse('all');
                      setSelectedClassroom('all');
                    }}
                    className="w-full"
                  >
                    <Filter className="w-4 h-4 mr-2" />
                    Clear Filters
                  </Button>
                </div>
              </div>
            </CardContent>
          </Card>

          {/* Quiz Statistics */}
          <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
            <Card>
              <CardContent className="p-6">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-sm font-medium text-gray-600">Total Quizzes</p>
                    <p className="text-2xl font-bold text-gray-900">{quizStats.totalQuizzes}</p>
                  </div>
                  <BarChart3 className="w-8 h-8 text-blue-600" />
                </div>
              </CardContent>
            </Card>

            <Card>
              <CardContent className="p-6">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-sm font-medium text-gray-600">Total Attempts</p>
                    <p className="text-2xl font-bold text-gray-900">{quizStats.totalAttempts}</p>
                  </div>
                  <Users className="w-8 h-8 text-green-600" />
                </div>
              </CardContent>
            </Card>

            <Card>
              <CardContent className="p-6">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-sm font-medium text-gray-600">Average Score</p>
                    <p className="text-2xl font-bold text-gray-900">{quizStats.averageScore}%</p>
                  </div>
                  <TrendingUp className="w-8 h-8 text-yellow-600" />
                </div>
              </CardContent>
            </Card>

            <Card>
              <CardContent className="p-6">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-sm font-medium text-gray-600">Pass Rate</p>
                    <p className="text-2xl font-bold text-gray-900">{quizStats.passRate}%</p>
                  </div>
                  <CheckCircle className="w-8 h-8 text-purple-600" />
                </div>
              </CardContent>
            </Card>
          </div>

          {/* Quiz Performance Overview */}
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            {/* Recent Quiz Attempts */}
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center space-x-2">
                  <Clock className="w-5 h-5" />
                  <span>Recent Quiz Attempts</span>
                </CardTitle>
                <CardDescription>Latest student submissions</CardDescription>
              </CardHeader>
              <CardContent>
                <div className="space-y-3">
                  {recentQuizAttempts.map(attempt => (
                    <div key={attempt.id} className="flex items-center justify-between py-2 border-b last:border-b-0">
                      <div className="flex-1">
                        <p className="font-medium text-sm">{attempt.studentName}</p>
                        <p className="text-xs text-gray-600">{attempt.courseName}</p>
                        <p className="text-xs text-gray-500">{attempt.quizTitle}</p>
                      </div>
                      <div className="text-right">
                        <Badge variant={attempt.isPassed ? "default" : "destructive"}>
                          {Math.round(attempt.score)}%
                        </Badge>
                        <p className="text-xs text-gray-500 mt-1">
                          {new Date(attempt.completedAt).toLocaleDateString()}
                        </p>
                      </div>
                    </div>
                  ))}
                  
                  {recentQuizAttempts.length === 0 && (
                    <div className="text-center py-4 text-gray-500">
                      <p>No quiz attempts yet.</p>
                    </div>
                  )}
                </div>
              </CardContent>
            </Card>

            {/* Course Quiz Performance */}
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center space-x-2">
                  <BarChart3 className="w-5 h-5" />
                  <span>Course Performance</span>
                </CardTitle>
                <CardDescription>Quiz performance breakdown by course</CardDescription>
              </CardHeader>
              <CardContent>
                <div className="space-y-4">
                  {courses.map(course => {
                    const courseQuizzes = quizzes.filter(quiz => quiz.courseId === course.id);
                    const courseAttempts = quizAttempts.filter(attempt => {
                      const quiz = quizzes.find(q => q.id === attempt.quizId);
                      return quiz && quiz.courseId === course.id;
                    });
                    const avgScore = courseAttempts.length > 0 
                      ? Math.round(courseAttempts.reduce((sum, attempt) => sum + (attempt.score || 0), 0) / courseAttempts.length)
                      : 0;
                    const passRate = courseAttempts.length > 0 
                      ? Math.round((courseAttempts.filter(attempt => attempt.isPassed).length / courseAttempts.length) * 100)
                      : 0;
                    
                    return (
                      <div key={course.id} className="border rounded-lg p-4">
                        <div className="flex items-center justify-between mb-2">
                          <h4 className="font-medium text-sm">{course.title}</h4>
                          <Badge variant="outline">{courseQuizzes.length} quiz{courseQuizzes.length !== 1 ? 'zes' : ''}</Badge>
                        </div>
                        <div className="grid grid-cols-2 gap-4 text-sm">
                          <div>
                            <p className="text-gray-600">Attempts: {courseAttempts.length}</p>
                            <p className="text-gray-600">Avg Score: {avgScore}%</p>
                          </div>
                          <div>
                            <p className="text-gray-600">Pass Rate: {passRate}%</p>
                            <p className="text-gray-600">
                              Passed: {courseAttempts.filter(attempt => attempt.isPassed).length}
                            </p>
                          </div>
                        </div>
                      </div>
                    );
                  })}
                  
                  {courses.length === 0 && (
                    <div className="text-center py-4 text-gray-500">
                      <p>No courses available.</p>
                    </div>
                  )}
                </div>
              </CardContent>
            </Card>
          </div>
        </TabsContent>

        <TabsContent value="tests" className="space-y-6">
          {/* Enhanced Filters for Final Tests */}
          <Card className="bg-gray-50">
            <CardContent className="p-6">
              <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                <div className="space-y-2">
                  <Label htmlFor="program-filter">Filter by Program</Label>
                  <Select value={selectedProgram} onValueChange={setSelectedProgram}>
                    <SelectTrigger id="program-filter">
                      <SelectValue placeholder="All Programs" />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="all">All Programs</SelectItem>
                      {programs.map(program => (
                        <SelectItem key={program.id} value={program.id}>{program.title}</SelectItem>
                      ))}
                    </SelectContent>
                  </Select>
                </div>

                <div className="space-y-2">
                  <Label htmlFor="classroom-filter-tests">Filter by Classroom</Label>
                  <Select value={selectedClassroom} onValueChange={setSelectedClassroom}>
                    <SelectTrigger id="classroom-filter-tests">
                      <SelectValue placeholder="All Classrooms" />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="all">All Classrooms</SelectItem>
                      {classrooms.map(classroom => (
                        <SelectItem key={classroom.id} value={classroom.id}>
                          {classroom.name} ({classroom.batchId})
                        </SelectItem>
                      ))}
                    </SelectContent>
                  </Select>
                </div>

                <div className="flex items-end">
                  <Button 
                    variant="outline" 
                    onClick={() => {
                      setSelectedProgram('all');
                      setSelectedClassroom('all');
                    }}
                    className="w-full"
                  >
                    <Filter className="w-4 h-4 mr-2" />
                    Clear Filters
                  </Button>
                </div>
              </div>
            </CardContent>
          </Card>

          {/* Final Test Statistics */}
          <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
            <Card>
              <CardContent className="p-6">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-sm font-medium text-gray-600">Total Final Tests</p>
                    <p className="text-2xl font-bold text-gray-900">{finalTestStats.totalTests}</p>
                  </div>
                  <GraduationCap className="w-8 h-8 text-blue-600" />
                </div>
              </CardContent>
            </Card>

            <Card>
              <CardContent className="p-6">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-sm font-medium text-gray-600">Total Attempts</p>
                    <p className="text-2xl font-bold text-gray-900">{finalTestStats.totalAttempts}</p>
                  </div>
                  <Users className="w-8 h-8 text-green-600" />
                </div>
              </CardContent>
            </Card>

            <Card>
              <CardContent className="p-6">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-sm font-medium text-gray-600">Average Score</p>
                    <p className="text-2xl font-bold text-gray-900">{finalTestStats.averageScore}%</p>
                  </div>
                  <TrendingUp className="w-8 h-8 text-yellow-600" />
                </div>
              </CardContent>
            </Card>

            <Card>
              <CardContent className="p-6">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-sm font-medium text-gray-600">Pass Rate</p>
                    <p className="text-2xl font-bold text-gray-900">{finalTestStats.passRate}%</p>
                  </div>
                  <CheckCircle className="w-8 h-8 text-purple-600" />
                </div>
              </CardContent>
            </Card>
          </div>

          {/* Final Test Performance Overview */}
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            {/* Recent Final Test Attempts */}
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center space-x-2">
                  <Clock className="w-5 h-5" />
                  <span>Recent Final Test Attempts</span>
                </CardTitle>
                <CardDescription>Latest student submissions</CardDescription>
              </CardHeader>
              <CardContent>
                <div className="space-y-3">
                  {recentFinalTestAttempts.map(attempt => (
                    <div key={attempt.id} className="flex items-center justify-between py-2 border-b last:border-b-0">
                      <div className="flex-1">
                        <p className="font-medium text-sm">{attempt.studentName}</p>
                        <p className="text-xs text-gray-600">{attempt.programName}</p>
                        <p className="text-xs text-gray-500">{attempt.testTitle}</p>
                      </div>
                      <div className="text-right">
                        <Badge variant={attempt.isPassed ? "default" : "destructive"}>
                          {Math.round(attempt.score)}%
                        </Badge>
                        <p className="text-xs text-gray-500 mt-1">
                          {new Date(attempt.completedAt).toLocaleDateString()}
                        </p>
                      </div>
                    </div>
                  ))}
                  
                  {recentFinalTestAttempts.length === 0 && (
                    <div className="text-center py-4 text-gray-500">
                      <p>No final test attempts yet.</p>
                    </div>
                  )}
                </div>
              </CardContent>
            </Card>

            {/* Program Performance Summary */}
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center space-x-2">
                  <BarChart3 className="w-5 h-5" />
                  <span>Program Performance</span>
                </CardTitle>
                <CardDescription>Performance breakdown by program</CardDescription>
              </CardHeader>
              <CardContent>
                <div className="space-y-4">
                  {programs.map(program => {
                    const programAttempts = finalTestAttempts.filter(attempt => attempt.programId === program.id);
                    const programTests = finalTests.filter(test => test.programId === program.id);
                    const avgScore = programAttempts.length > 0 
                      ? Math.round(programAttempts.reduce((sum, attempt) => sum + (attempt.score || 0), 0) / programAttempts.length)
                      : 0;
                    const passRate = programAttempts.length > 0 
                      ? Math.round((programAttempts.filter(attempt => attempt.isPassed).length / programAttempts.length) * 100)
                      : 0;
                    
                    return (
                      <div key={program.id} className="border rounded-lg p-4">
                        <div className="flex items-center justify-between mb-2">
                          <h4 className="font-medium text-sm">{program.title}</h4>
                          <Badge variant="outline">{programTests.length} test{programTests.length !== 1 ? 's' : ''}</Badge>
                        </div>
                        <div className="grid grid-cols-2 gap-4 text-sm">
                          <div>
                            <p className="text-gray-600">Attempts: {programAttempts.length}</p>
                            <p className="text-gray-600">Avg Score: {avgScore}%</p>
                          </div>
                          <div>
                            <p className="text-gray-600">Pass Rate: {passRate}%</p>
                            <p className="text-gray-600">
                              Passed: {programAttempts.filter(attempt => attempt.isPassed).length}
                            </p>
                          </div>
                        </div>
                      </div>
                    );
                  })}
                  
                  {programs.length === 0 && (
                    <div className="text-center py-4 text-gray-500">
                      <p>No programs available.</p>
                    </div>
                  )}
                </div>
              </CardContent>
            </Card>
          </div>
        </TabsContent>
      </Tabs>
    </div>
  );
};

export default QuizAndTestResults;