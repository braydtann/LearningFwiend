import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../../contexts/AuthContext';
import { Card, CardHeader, CardTitle, CardContent } from '../ui/card';
import { Button } from '../ui/button';
import { Badge } from '../ui/badge';
import { Users, BookOpen, TrendingUp, UserCheck, BarChart, Settings } from 'lucide-react';

const AdminDashboard = () => {
  const navigate = useNavigate();
  const { getAllUsers, getAllCourses } = useAuth();
  
  const [users, setUsers] = useState([]);
  const [courses, setCourses] = useState([]);
  const [loading, setLoading] = useState(true);
  
  useEffect(() => {
    loadDashboardData();
  }, []);

  const loadDashboardData = async () => {
    setLoading(true);
    try {
      // Load users
      const usersResult = await getAllUsers();
      if (usersResult.success) {
        setUsers(usersResult.users);
      }

      // Load courses
      const coursesResult = await getAllCourses();
      if (coursesResult.success) {
        setCourses(coursesResult.courses);
      }
    } catch (error) {
      console.error('Error loading dashboard data:', error);
    } finally {
      setLoading(false);
    }
  };
  
  const stats = {
    totalUsers: users.length,
    totalCourses: courses.length,
    totalEnrollments: 0, // TODO: Add enrollment count when backend supports it
    activeUsers: users.filter(user => user.role !== 'admin').length,
    instructors: users.filter(user => user.role === 'instructor').length,
    students: users.filter(user => user.role === 'learner').length,
    publishedCourses: courses.filter(course => course.status === 'published').length
  };

  const recentUsers = users.slice(-3);
  const recentCourses = courses.slice(-3);

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto mb-4"></div>
          <h2 className="text-xl font-semibold text-gray-900 mb-2">Loading Dashboard</h2>
          <p className="text-gray-600">Please wait while we fetch the data...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-8">
      {/* Welcome Section */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-gray-900 mb-2">
            Admin Dashboard
          </h1>
          <p className="text-gray-600">Manage your LearningFwiend platform</p>
        </div>
        <Button 
          onClick={() => navigate('/analytics')}
          className="bg-blue-600 hover:bg-blue-700"
        >
          <BarChart className="w-4 h-4 mr-2" />
          View Analytics
        </Button>
      </div>

      {/* Stats Cards */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
        <Card className="bg-blue-50 border-blue-200">
          <CardContent className="p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-blue-600 text-sm font-medium">Total Users</p>
                <p className="text-2xl font-bold text-blue-700">{stats.totalUsers}</p>
              </div>
              <Users className="h-8 w-8 text-blue-600" />
            </div>
          </CardContent>
        </Card>

        <Card className="bg-green-50 border-green-200">
          <CardContent className="p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-green-600 text-sm font-medium">Total Courses</p>
                <p className="text-2xl font-bold text-green-700">{stats.totalCourses}</p>
              </div>
              <BookOpen className="h-8 w-8 text-green-600" />
            </div>
          </CardContent>
        </Card>

        <Card className="bg-orange-50 border-orange-200">
          <CardContent className="p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-orange-600 text-sm font-medium">Enrollments</p>
                <p className="text-2xl font-bold text-orange-700">{stats.totalEnrollments}</p>
              </div>
              <TrendingUp className="h-8 w-8 text-orange-600" />
            </div>
          </CardContent>
        </Card>

        <Card className="bg-purple-50 border-purple-200">
          <CardContent className="p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-purple-600 text-sm font-medium">Active Users</p>
                <p className="text-2xl font-bold text-purple-700">{stats.activeUsers}</p>
              </div>
              <UserCheck className="h-8 w-8 text-purple-600" />
            </div>
          </CardContent>
        </Card>
      </div>

      {/* User Distribution */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <Card>
          <CardHeader>
            <CardTitle className="text-xl">User Distribution</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              <div className="flex items-center justify-between p-4 bg-blue-50 rounded-lg">
                <div className="flex items-center">
                  <Users className="h-5 w-5 text-blue-600 mr-3" />
                  <span className="font-medium">Students</span>
                </div>
                <div className="text-right">
                  <span className="text-2xl font-bold text-blue-700">{stats.students}</span>
                  <p className="text-sm text-gray-600">Learners</p>
                </div>
              </div>
              
              <div className="flex items-center justify-between p-4 bg-green-50 rounded-lg">
                <div className="flex items-center">
                  <UserCheck className="h-5 w-5 text-green-600 mr-3" />
                  <span className="font-medium">Instructors</span>
                </div>
                <div className="text-right">
                  <span className="text-2xl font-bold text-green-700">{stats.instructors}</span>
                  <p className="text-sm text-gray-600">Teachers</p>
                </div>
              </div>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle className="text-xl">Course Statistics</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              <div className="flex items-center justify-between p-4 bg-green-50 rounded-lg">
                <div className="flex items-center">
                  <BookOpen className="h-5 w-5 text-green-600 mr-3" />
                  <span className="font-medium">Published Courses</span>
                </div>
                <div className="text-right">
                  <span className="text-2xl font-bold text-green-700">{stats.publishedCourses}</span>
                  <p className="text-sm text-gray-600">Live</p>
                </div>
              </div>
              
              <div className="flex items-center justify-between p-4 bg-orange-50 rounded-lg">
                <div className="flex items-center">
                  <TrendingUp className="h-5 w-5 text-orange-600 mr-3" />
                  <span className="font-medium">Total Enrollments</span>
                </div>
                <div className="text-right">
                  <span className="text-2xl font-bold text-orange-700">{stats.totalEnrollments}</span>
                  <p className="text-sm text-gray-600">Active</p>
                </div>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Recent Activity */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <Card>
          <CardHeader>
            <div className="flex items-center justify-between">
              <CardTitle className="text-xl">Recent Users</CardTitle>
              <Button 
                variant="outline" 
                size="sm"
                onClick={() => navigate('/users')}
              >
                View All
              </Button>
            </div>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              {recentUsers.map((user) => (
                <div key={user.id} className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
                  <div className="flex items-center space-x-3">
                    <div className="w-10 h-10 bg-blue-100 rounded-full flex items-center justify-center">
                      <Users className="w-5 h-5 text-blue-600" />
                    </div>
                    <div>
                      <p className="font-medium text-gray-900">{user.full_name}</p>
                      <p className="text-sm text-gray-600">{user.email}</p>
                    </div>
                  </div>
                  <Badge variant={user.role === 'instructor' ? 'default' : 'secondary'}>
                    {user.role}
                  </Badge>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <div className="flex items-center justify-between">
              <CardTitle className="text-xl">Recent Courses</CardTitle>
              <Button 
                variant="outline" 
                size="sm"
                onClick={() => navigate('/courses')}
              >
                View All
              </Button>
            </div>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              {recentCourses.map((course) => (
                <div key={course.id} className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
                  <div className="flex items-center space-x-3">
                    <div className="w-10 h-10 bg-green-100 rounded-lg flex items-center justify-center">
                      <BookOpen className="w-5 h-5 text-green-600" />
                    </div>
                    <div>
                      <p className="font-medium text-gray-900">{course.title}</p>
                      <p className="text-sm text-gray-600">by {course.instructor}</p>
                    </div>
                  </div>
                  <Badge variant={course.status === 'published' ? 'default' : 'secondary'}>
                    {course.status}
                  </Badge>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Quick Actions */}
      <Card>
        <CardHeader>
          <CardTitle className="text-xl">Quick Actions</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <Button 
              variant="outline" 
              className="p-6 h-auto flex-col space-y-2"
              onClick={() => navigate('/users')}
            >
              <Users className="h-8 w-8 text-blue-600" />
              <span>Manage Users</span>
            </Button>
            
            <Button 
              variant="outline" 
              className="p-6 h-auto flex-col space-y-2"
              onClick={() => navigate('/courses')}
            >
              <BookOpen className="h-8 w-8 text-green-600" />
              <span>Manage Courses</span>
            </Button>
            
            <Button 
              variant="outline" 
              className="p-6 h-auto flex-col space-y-2"
              onClick={() => navigate('/analytics')}
            >
              <BarChart className="h-8 w-8 text-purple-600" />
              <span>View Analytics</span>
            </Button>
          </div>
        </CardContent>
      </Card>
    </div>
  );
};

export default AdminDashboard;