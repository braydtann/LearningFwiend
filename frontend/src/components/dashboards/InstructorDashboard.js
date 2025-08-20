import React, { useState, useEffect } from 'react';
import { useAuth } from '../../contexts/AuthContext';
import { useNavigate } from 'react-router-dom';
import { Card, CardHeader, CardTitle, CardContent } from '../ui/card';
import { Button } from '../ui/button';
import { Badge } from '../ui/badge';
import { BookOpen, Users, TrendingUp, PlusCircle, Eye, Edit, ClipboardCheck } from 'lucide-react';

const InstructorDashboard = () => {
  const { user, getAllCourses } = useAuth();
  const navigate = useNavigate();
  const [myCourses, setMyCourses] = useState([]);
  const [loading, setLoading] = useState(true);

  // Load instructor courses
  useEffect(() => {
    const loadCourses = async () => {
      try {
        const result = await getAllCourses();
        if (result.success) {
          // Filter courses by instructor
          const instructorCourses = result.courses.filter(course => 
            course.instructorId === user?.id || course.instructor === user?.email
          );
          setMyCourses(instructorCourses);
        } else {
          setMyCourses([]);
        }
      } catch (error) {
        console.error('Error loading courses:', error);
        setMyCourses([]);
      } finally {
        setLoading(false);
      }
    };

    if (user) {
      loadCourses();
    }
  }, [user, getAllCourses]);

  // TODO: Replace with backend analytics when available
  const quizAnalytics = []; // getInstructorQuizAnalytics(user?.id);
  const totalStudents = 0; // Calculate from enrollments when backend available
  const activeEnrollments = 0; // Calculate from enrollments when backend available
  
  const stats = {
    courses: myCourses.length,
    students: totalStudents,
    published: publishedCourses,
    quizzes: quizAnalytics.totalQuizzes,
    avgRating: 4.7 // Mock average rating
  };

  return (
    <div className="space-y-8">
      {/* Welcome Section */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-gray-900 mb-2">
            Instructor Dashboard
          </h1>
          <p className="text-gray-600">Manage your courses and track student progress</p>
        </div>
        <Button 
          onClick={() => navigate('/create-course')}
          className="bg-blue-600 hover:bg-blue-700 mr-3"
        >
          <PlusCircle className="w-4 h-4 mr-2" />
          Create New Course
        </Button>
        <Button 
          onClick={() => navigate('/quiz-results')}
          variant="outline"
        >
          <ClipboardCheck className="w-4 h-4 mr-2" />
          Quiz Results
        </Button>
      </div>

      {/* Stats Cards */}
      <div className="grid grid-cols-1 md:grid-cols-5 gap-6">
        <Card className="bg-blue-50 border-blue-200">
          <CardContent className="p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-blue-600 text-sm font-medium">Total Courses</p>
                <p className="text-2xl font-bold text-blue-700">{stats.courses}</p>
              </div>
              <BookOpen className="h-8 w-8 text-blue-600" />
            </div>
          </CardContent>
        </Card>

        <Card className="bg-green-50 border-green-200">
          <CardContent className="p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-green-600 text-sm font-medium">Total Students</p>
                <p className="text-2xl font-bold text-green-700">{stats.students}</p>
              </div>
              <Users className="h-8 w-8 text-green-600" />
            </div>
          </CardContent>
        </Card>

        <Card className="bg-orange-50 border-orange-200">
          <CardContent className="p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-orange-600 text-sm font-medium">Published</p>
                <p className="text-2xl font-bold text-orange-700">{stats.published}</p>
              </div>
              <TrendingUp className="h-8 w-8 text-orange-600" />
            </div>
          </CardContent>
        </Card>

        <Card className="bg-purple-50 border-purple-200">
          <CardContent className="p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-purple-600 text-sm font-medium">Total Quizzes</p>
                <p className="text-2xl font-bold text-purple-700">{stats.quizzes}</p>
              </div>
              <ClipboardCheck className="h-8 w-8 text-purple-600" />
            </div>
          </CardContent>
        </Card>

        <Card className="bg-indigo-50 border-indigo-200">
          <CardContent className="p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-indigo-600 text-sm font-medium">Avg Rating</p>
                <p className="text-2xl font-bold text-indigo-700">{stats.avgRating}</p>
              </div>
              <TrendingUp className="h-8 w-8 text-indigo-600" />
            </div>
          </CardContent>
        </Card>
      </div>

      {/* My Courses */}
      <Card>
        <CardHeader>
          <div className="flex items-center justify-between">
            <CardTitle className="text-xl">My Courses</CardTitle>
            <Button 
              variant="outline" 
              onClick={() => navigate('/create-course')}
            >
              <PlusCircle className="w-4 h-4 mr-2" />
              Create Course
            </Button>
          </div>
        </CardHeader>
        <CardContent>
          {myCourses.length === 0 ? (
            <div className="text-center py-12">
              <BookOpen className="h-12 w-12 text-gray-400 mx-auto mb-4" />
              <h3 className="text-lg font-medium text-gray-900 mb-2">No courses created yet</h3>
              <p className="text-gray-600 mb-4">Create your first course to start teaching</p>
              <Button onClick={() => navigate('/create-course')}>
                <PlusCircle className="w-4 h-4 mr-2" />
                Create Your First Course
              </Button>
            </div>
          ) : (
            <div className="space-y-4">
              {myCourses.map((course) => (
                <Card key={course.id} className="hover:shadow-md transition-shadow">
                  <CardContent className="p-6">
                    <div className="flex items-start justify-between">
                      <div className="flex space-x-4 flex-1">
                        <img 
                          src={course.thumbnail} 
                          alt={course.title}
                          className="w-20 h-20 object-cover rounded-lg"
                        />
                        <div className="flex-1">
                          <h3 className="text-lg font-semibold text-gray-900 mb-2">
                            {course.title}
                          </h3>
                          <p className="text-gray-600 text-sm mb-3 line-clamp-2">
                            {course.description}
                          </p>
                          <div className="flex items-center space-x-4 text-sm text-gray-500">
                            <div className="flex items-center">
                              <Users className="w-4 h-4 mr-1" />
                              {course.enrolledStudents} students
                            </div>
                            <div className="flex items-center">
                              <BookOpen className="w-4 h-4 mr-1" />
                              {course.totalLessons} lessons
                            </div>
                            <Badge variant={course.status === 'published' ? 'default' : 'secondary'}>
                              {course.status}
                            </Badge>
                          </div>
                        </div>
                      </div>
                      <div className="flex items-center space-x-2 ml-4">
                        <Button 
                          size="sm" 
                          variant="outline"
                          onClick={() => navigate(`/course/${course.id}`)}
                        >
                          <Eye className="w-4 h-4 mr-1" />
                          View
                        </Button>
                        <Button 
                          size="sm" 
                          variant="outline"
                          onClick={() => navigate(`/edit-course/${course.id}`)}
                        >
                          <Edit className="w-4 h-4 mr-1" />
                          Edit
                        </Button>
                      </div>
                    </div>
                  </CardContent>
                </Card>
              ))}
            </div>
          )}
        </CardContent>
      </Card>

      {/* Recent Activity */}
      <Card>
        <CardHeader>
          <CardTitle className="text-xl">Recent Student Activity</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="space-y-4">
            <div className="flex items-center justify-between p-4 bg-gray-50 rounded-lg">
              <div>
                <p className="font-medium">Mike Johnson enrolled in React Development Fundamentals</p>
                <p className="text-sm text-gray-600">2 hours ago</p>
              </div>
              <Badge variant="outline">New Enrollment</Badge>
            </div>
            <div className="flex items-center justify-between p-4 bg-gray-50 rounded-lg">
              <div>
                <p className="font-medium">Sarah completed Python for Data Science</p>
                <p className="text-sm text-gray-600">1 day ago</p>
              </div>
              <Badge variant="default">Course Completed</Badge>
            </div>
            <div className="flex items-center justify-between p-4 bg-gray-50 rounded-lg">
              <div>
                <p className="font-medium">New quiz submission for Digital Marketing Mastery</p>
                <p className="text-sm text-gray-600">3 days ago</p>
              </div>
              <Badge variant="secondary">Quiz Submitted</Badge>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  );
};

export default InstructorDashboard;