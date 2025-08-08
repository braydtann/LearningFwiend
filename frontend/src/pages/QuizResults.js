import React, { useState } from 'react';
import { useAuth } from '../contexts/AuthContext';
import { Card, CardHeader, CardTitle, CardContent } from '../components/ui/card';
import { Button } from '../components/ui/button';
import { Badge } from '../components/ui/badge';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '../components/ui/tabs';
import { 
  mockCourses, 
  mockQuizAttempts, 
  mockQuizResults, 
  mockUsers,
  mockClassrooms,
  mockClassroomEnrollments,
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
  Filter
} from 'lucide-react';

const QuizResults = () => {
  const { user, isInstructor, isAdmin } = useAuth();
  const [selectedCourse, setSelectedCourse] = useState('all');

  // Get courses based on user role
  const courses = isInstructor 
    ? mockCourses.filter(course => course.instructorId === user?.id)
    : isAdmin 
    ? mockCourses 
    : [];

  // Get quiz analytics
  const analytics = getInstructorQuizAnalytics(user?.id);

  // Filter quiz results based on selected course
  const filteredResults = selectedCourse === 'all' 
    ? mockQuizResults 
    : mockQuizResults.filter(result => result.courseId === selectedCourse);

  // Get quiz attempts for detailed view
  const filteredAttempts = selectedCourse === 'all'
    ? mockQuizAttempts
    : mockQuizAttempts.filter(attempt => attempt.courseId === selectedCourse);

  // Calculate statistics
  const stats = {
    totalQuizzes: analytics.totalQuizzes,
    totalAttempts: filteredAttempts.length,
    averageScore: filteredResults.length > 0 
      ? Math.round(filteredResults.reduce((sum, result) => sum + result.averageScore, 0) / filteredResults.length)
      : 0,
    passRate: filteredResults.length > 0 
      ? Math.round((filteredResults.filter(result => result.passed).length / filteredResults.length) * 100)
      : 0,
    completedAttempts: filteredAttempts.filter(attempt => attempt.status === 'completed').length,
    inProgressAttempts: filteredAttempts.filter(attempt => attempt.status === 'in-progress').length
  };

  // Get recent quiz attempts with user details
  const recentAttempts = filteredAttempts
    .filter(attempt => attempt.status === 'completed')
    .sort((a, b) => new Date(b.completedAt) - new Date(a.completedAt))
    .slice(0, 10)
    .map(attempt => {
      const student = mockUsers.find(u => u.id === attempt.userId);
      const course = mockCourses.find(c => c.id === attempt.courseId);
      return {
        ...attempt,
        studentName: student?.name || 'Unknown',
        courseName: course?.title || 'Unknown Course'
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
          <h1 className="text-3xl font-bold text-gray-900">Quiz Results & Analytics</h1>
          <p className="text-gray-600">Monitor student performance and quiz analytics</p>
        </div>
        <div className="flex items-center space-x-4">
          <select
            value={selectedCourse}
            onChange={(e) => setSelectedCourse(e.target.value)}
            className="px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
          >
            <option value="all">All Courses</option>
            {courses.map(course => (
              <option key={course.id} value={course.id}>{course.title}</option>
            ))}
          </select>
        </div>
      </div>

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
                {filteredResults.length > 0 ? (
                  filteredResults.map((result) => {
                    const student = mockUsers.find(u => u.id === result.userId);
                    const course = mockCourses.find(c => c.id === result.courseId);
                    return (
                      <div 
                        key={result.id} 
                        className="flex items-center justify-between p-4 border rounded-lg"
                      >
                        <div className="flex items-center space-x-4">
                          <img 
                            src={student?.avatar || 'https://images.unsplash.com/photo-1472099645785-5658abf4ff4e?w=40&h=40&fit=crop&crop=face'} 
                            className="w-10 h-10 rounded-full object-cover"
                            alt={student?.name}
                          />
                          <div>
                            <p className="font-medium text-gray-900">{student?.name || 'Unknown Student'}</p>
                            <p className="text-sm text-gray-600">{course?.title || 'Unknown Course'}</p>
                          </div>
                        </div>
                        <div className="text-right">
                          <div className="flex items-center space-x-3">
                            <div className="text-sm">
                              <p className="text-gray-600">Best: <span className="font-medium">{result.bestScore}%</span></p>
                              <p className="text-gray-600">Attempts: <span className="font-medium">{result.totalAttempts}</span></p>
                            </div>
                            <Badge variant={result.passed ? "default" : "destructive"}>
                              {result.passed ? "Passed" : "Failed"}
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
                    const courseAttempts = filteredAttempts.filter(attempt => attempt.courseId === course.id);
                    const courseResults = filteredResults.filter(result => result.courseId === course.id);
                    const coursePassRate = courseResults.length > 0 
                      ? Math.round((courseResults.filter(result => result.passed).length / courseResults.length) * 100)
                      : 0;
                    
                    return (
                      <div key={course.id} className="p-3 border rounded-lg">
                        <div className="flex items-center justify-between mb-2">
                          <p className="font-medium text-gray-900">{course.title}</p>
                          <Badge variant="outline">{coursePassRate}% pass rate</Badge>
                        </div>
                        <div className="flex items-center justify-between text-sm text-gray-600">
                          <span>{courseAttempts.length} attempts</span>
                          <span>{courseResults.length} students</span>
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
    </div>
  );
};

export default QuizResults;