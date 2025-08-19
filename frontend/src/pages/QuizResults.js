import React, { useState, useEffect } from 'react';
import { useAuth } from '../contexts/AuthContext';
import { Card, CardHeader, CardTitle, CardContent } from '../components/ui/card';
import { Button } from '../components/ui/button';
import { Badge } from '../components/ui/badge';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '../components/ui/tabs';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '../components/ui/select';
import { Label } from '../components/ui/label';
import { useToast } from '../hooks/use-toast';
// Mock data imports - kept as fallback only
import { 
  getInstructorQuizAnalytics 
} from '../data/mockData';
import { 
  BarChart3, 
  Users, 
  Clock, 
  CheckCircle,
  XCircle,
  TrendingUp,
  FileText,
  Award,
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

  // Load real data on component mount
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
        // Don't show error for programs as it might not be critical
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
        // Don't show error for classrooms as it might not be critical
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

      // Load quiz attempts from backend
      const attemptsResult = await getQuizAttempts();
      if (attemptsResult.success) {
        setQuizAttempts(attemptsResult.attempts);
      } else {
        console.log('Could not load quiz attempts:', attemptsResult.error);
        setQuizAttempts([]);
      }

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

  // Get quiz analytics - now using real backend data
  const analytics = {
    totalQuizzes: quizzes.length,
    totalCourses: courses.length,
    totalStudents: 0, // This would need a separate API call to count students
    averageScore: 0
  };

  // Filter results and attempts based on selections using REAL data
  let filteredQuizzes = quizzes;
  let filteredAttempts = quizAttempts;
  
  if (selectedCourse !== 'all') {
    filteredQuizzes = quizzes.filter(quiz => quiz.courseId === selectedCourse);
    filteredAttempts = quizAttempts.filter(attempt => {
      // Find quiz for this attempt and check if it's in the selected course
      const quiz = quizzes.find(q => q.id === attempt.quizId);
      return quiz && quiz.courseId === selectedCourse;
    });
  }

  // Apply classroom filter if selected
  // Note: This would need classroom-student relationship data from backend
  if (selectedClassroom !== 'all') {
    // For now, this is a placeholder until classroom-student relationships are fully implemented
    // In a real implementation, we would fetch students from the selected classroom
    // and filter attempts by those student IDs
    console.log('Classroom filtering not yet implemented - would need student roster data');
  }

  // Calculate real statistics from backend data
  const stats = {
    totalQuizzes: filteredQuizzes.length,
    totalAttempts: filteredAttempts.length,
    averageScore: filteredAttempts.length > 0 
      ? Math.round(filteredAttempts.reduce((sum, attempt) => sum + (attempt.score || 0), 0) / filteredAttempts.length)
      : 0,
    passRate: filteredAttempts.length > 0 
      ? Math.round((filteredAttempts.filter(attempt => attempt.isPassed).length / filteredAttempts.length) * 100)
      : 0,
    completedAttempts: filteredAttempts.filter(attempt => attempt.status === 'completed').length,
    inProgressAttempts: filteredAttempts.filter(attempt => attempt.status === 'in_progress' || !attempt.status).length
  };

  // Get recent quiz attempts with enhanced details from real backend data
  const recentAttempts = filteredAttempts
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

  if (!isInstructor && !isAdmin) {
    return (
      <div className="text-center py-12">
        <XCircle className="w-16 h-16 text-red-600 mx-auto mb-4" />
        <h1 className="text-2xl font-bold text-gray-900 mb-4">Access Denied</h1>
        <p className="text-gray-600">You don't have permission to view quiz results.</p>
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

          {/* Active Filters Display */}
          <div className="flex items-center space-x-2 mt-4">
            <span className="text-sm text-gray-500">Active Filters:</span>
            {selectedCourse !== 'all' && (
              <Badge variant="secondary" className="bg-blue-100 text-blue-800">
                Course: {courses.find(c => c.id === selectedCourse)?.title || 'Unknown'}
              </Badge>
            )}
            {selectedClassroom !== 'all' && (
              <Badge variant="secondary" className="bg-green-100 text-green-800">
                Classroom: {classrooms.find(c => c.id === selectedClassroom)?.name || 'Unknown'}
              </Badge>
            )}
            {selectedCourse === 'all' && selectedClassroom === 'all' && (
              <span className="text-sm text-gray-400">None</span>
            )}
          </div>
        </CardContent>
      </Card>

      {/* Statistics Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <Card>
          <CardContent className="p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-600">Total Quizzes</p>
                <p className="text-2xl font-bold text-gray-900">{stats.totalQuizzes}</p>
              </div>
              <div className="w-12 h-12 bg-blue-100 rounded-lg flex items-center justify-center">
                <FileText className="w-6 h-6 text-blue-600" />
              </div>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-600">Total Attempts</p>
                <p className="text-2xl font-bold text-gray-900">{stats.totalAttempts}</p>
              </div>
              <div className="w-12 h-12 bg-green-100 rounded-lg flex items-center justify-center">
                <Users className="w-6 h-6 text-green-600" />
              </div>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-600">Average Score</p>
                <p className="text-2xl font-bold text-gray-900">{stats.averageScore}%</p>
              </div>
              <div className="w-12 h-12 bg-purple-100 rounded-lg flex items-center justify-center">
                <BarChart3 className="w-6 h-6 text-purple-600" />
              </div>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-600">Pass Rate</p>
                <p className="text-2xl font-bold text-gray-900">{stats.passRate}%</p>
              </div>
              <div className="w-12 h-12 bg-orange-100 rounded-lg flex items-center justify-center">
                <Award className="w-6 h-6 text-orange-600" />
              </div>
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Detailed Results */}
      <Tabs defaultValue="recent" className="w-full">
        <TabsList className="grid w-full grid-cols-3">
          <TabsTrigger value="recent">Recent Attempts</TabsTrigger>
          <TabsTrigger value="students">Student Performance</TabsTrigger>
          <TabsTrigger value="analytics">Quiz Analytics</TabsTrigger>
        </TabsList>

        <TabsContent value="recent" className="space-y-6">
          <Card>
            <CardHeader>
              <CardTitle>Recent Quiz Attempts</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                {recentAttempts.length > 0 ? (
                  recentAttempts.map((attempt) => (
                    <div 
                      key={attempt.id} 
                      className="flex items-center justify-between p-4 border rounded-lg hover:bg-gray-50"
                    >
                      <div className="flex items-center space-x-4">
                        <div className="w-10 h-10 bg-gray-100 rounded-full flex items-center justify-center">
                          <Users className="w-5 h-5 text-gray-600" />
                        </div>
                        <div>
                          <p className="font-medium text-gray-900">{attempt.studentName}</p>
                          <p className="text-sm text-gray-600">{attempt.courseName}</p>
                        </div>
                      </div>
                      <div className="text-right">
                        <div className="flex items-center space-x-2">
                          <Badge variant={attempt.passed ? "default" : "destructive"}>
                            {attempt.score}%
                          </Badge>
                          {attempt.passed ? (
                            <CheckCircle className="w-4 h-4 text-green-600" />
                          ) : (
                            <XCircle className="w-4 h-4 text-red-600" />
                          )}
                        </div>
                        <p className="text-sm text-gray-500">
                          {new Date(attempt.completedAt).toLocaleDateString()}
                        </p>
                      </div>
                    </div>
                  ))
                ) : (
                  <div className="text-center py-8 text-gray-500">
                    <FileText className="w-12 h-12 mx-auto mb-4 opacity-50" />
                    <p>No quiz attempts found for the selected filters.</p>
                  </div>
                )}
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="students" className="space-y-6">
          <Card>
            <CardHeader>
              <CardTitle>Student Performance Overview</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                {filteredAttempts.length > 0 ? (
                  // Group attempts by student and show their performance
                  Object.entries(
                    filteredAttempts.reduce((acc, attempt) => {
                      const studentId = attempt.userId || attempt.studentId;
                      if (!acc[studentId]) {
                        acc[studentId] = [];
                      }
                      acc[studentId].push(attempt);
                      return acc;
                    }, {})
                  ).map(([studentId, attempts]) => {
                    const studentName = attempts[0]?.studentName || 'Unknown Student';
                    const averageScore = Math.round(
                      attempts.reduce((sum, attempt) => sum + (attempt.score || 0), 0) / attempts.length
                    );
                    const totalAttempts = attempts.length;
                    const passedAttempts = attempts.filter(attempt => attempt.isPassed).length;
                    
                    return (
                      <div 
                        key={studentId} 
                        className="flex items-center justify-between p-4 border rounded-lg"
                      >
                        <div className="flex items-center space-x-4">
                          <div className="w-10 h-10 rounded-full bg-blue-100 flex items-center justify-center">
                            <Users className="w-5 h-5 text-blue-600" />
                          </div>
                          <div>
                            <p className="font-medium text-gray-900">{studentName}</p>
                            <p className="text-sm text-gray-600">{totalAttempts} quiz attempts</p>
                          </div>
                        </div>
                        <div className="text-right">
                          <div className="flex items-center space-x-3">
                            <div className="text-sm">
                              <div className="text-gray-600">Average Score</div>
                              <div className="font-semibold text-gray-900">{averageScore}%</div>
                            </div>
                            <div className="text-sm">
                              <div className="text-gray-600">Pass Rate</div>
                              <div className="font-semibold text-gray-900">
                                {Math.round((passedAttempts / totalAttempts) * 100)}%
                              </div>
                            </div>
                            <Badge variant={averageScore >= 70 ? 'default' : 'destructive'}>
                              {averageScore >= 70 ? 'Good' : 'Needs Improvement'}
                            </Badge>
                          </div>
                        </div>
                      </div>
                    );
                  })
                ) : (
                  <div className="text-center py-8 text-gray-500">
                    <Users className="w-12 h-12 mx-auto mb-4 opacity-50" />
                    <p>No student performance data available for the selected filters.</p>
                  </div>
                )}
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="analytics" className="space-y-6">
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            <Card>
              <CardHeader>
                <CardTitle>Quiz Performance Metrics</CardTitle>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="flex items-center justify-between p-3 bg-green-50 rounded-lg">
                  <div className="flex items-center space-x-2">
                    <CheckCircle className="w-5 h-5 text-green-600" />
                    <span className="text-green-800">Completed Attempts</span>
                  </div>
                  <span className="font-bold text-green-800">{stats.completedAttempts}</span>
                </div>
                
                <div className="flex items-center justify-between p-3 bg-yellow-50 rounded-lg">
                  <div className="flex items-center space-x-2">
                    <Clock className="w-5 h-5 text-yellow-600" />
                    <span className="text-yellow-800">In Progress</span>
                  </div>
                  <span className="font-bold text-yellow-800">{stats.inProgressAttempts}</span>
                </div>
                
                <div className="flex items-center justify-between p-3 bg-blue-50 rounded-lg">
                  <div className="flex items-center space-x-2">
                    <TrendingUp className="w-5 h-5 text-blue-600" />
                    <span className="text-blue-800">Pass Rate</span>
                  </div>
                  <span className="font-bold text-blue-800">{stats.passRate}%</span>
                </div>
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <CardTitle>Course Breakdown</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-3">
                  {courses.map(course => {
                    const courseAttempts = filteredAttempts.filter(attempt => {
                      // Find quiz for this attempt and check if it's in the selected course
                      const quiz = quizzes.find(q => q.id === attempt.quizId);
                      return quiz && quiz.courseId === course.id;
                    });
                    const coursePassRate = courseAttempts.length > 0 
                      ? Math.round((courseAttempts.filter(attempt => attempt.isPassed).length / courseAttempts.length) * 100)
                      : 0;
                    
                    // Count unique students for this course
                    const uniqueStudents = new Set(courseAttempts.map(attempt => attempt.userId || attempt.studentId)).size;
                    
                    return (
                      <div key={course.id} className="p-3 border rounded-lg">
                        <div className="flex items-center justify-between mb-2">
                          <p className="font-medium text-gray-900">{course.title}</p>
                          <Badge variant="outline">{coursePassRate}% pass rate</Badge>
                        </div>
                        <div className="flex items-center justify-between text-sm text-gray-600">
                          <span>{courseAttempts.length} attempts</span>
                          <span>{uniqueStudents} students</span>
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
      </Tabs>
        </TabsContent>

        <TabsContent value="tests" className="space-y-6">
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center space-x-2">
                <GraduationCap className="w-5 h-5" />
                <span>Final Test Analytics</span>
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="text-center py-8 text-gray-500">
                <GraduationCap className="w-12 h-12 mx-auto mb-4 opacity-50" />
                <p>Final test analytics will be implemented here.</p>
                <p className="text-sm mt-2">This section will show program final test results and performance metrics.</p>
              </div>
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>
    </div>
  );
};

export default QuizAndTestResults;